"""Serviço principal de domínio do RoomFlow.

Centraliza as regras de negócio e orquestra persistência em TXT/JSON:
usuários, setores, solicitações, reservas, bloqueios, notificações e logs.
"""

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .filedb import FileDB
from .models import AuditEvent, Block, Booking, BookingRequest, Notification, Room, User
from .security import hash_password, verify_password
from .validators import format_date_br, minutes_to_time, parse_date_br, parse_time_hhmm, time_to_minutes

ROLE_ADMIN = "ADMIN"
ROLE_RH = "RH"
ROLE_USER = "USER"

REQ_PENDING = "PENDENTE"
REQ_APPROVED = "APROVADA"
REQ_DENIED = "NEGADA"
REQ_CANCELLED = "CANCELADA"

BOOK_ACTIVE = "ATIVA"
BOOK_IN_PROGRESS = "EM_ANDAMENTO"
BOOK_CANCELLED = "CANCELADA"
BOOK_CANCELLED_EMERGENCY = "CANCELADA_POR_EMERGENCIA"
BOOK_EXPIRED = "EXPIRADA"
BOOK_DONE = "CONCLUIDA"

BLOCK_ACTIVE = "ATIVO"
BLOCK_INACTIVE = "INATIVO"


class RoomFlowService:
    def __init__(self, db: FileDB, config):
        self.db = db
        self.cfg = config
        self.db.ensure_dirs()

    def now(self):
        return datetime.now()

    def now_iso(self):
        return self.now().isoformat(timespec="seconds")

    def today_iso(self):
        return self.now().strftime("%Y-%m-%d")

    def today_br(self):
        return format_date_br(self.today_iso())

    def _users_dir(self) -> Path:
        return self.db.data_dir / "users"

    def _rooms_dir(self) -> Path:
        return self.db.data_dir / "rooms"

    def _sectors_dir(self) -> Path:
        return self.db.data_dir / "sectors"

    def _bookings_file(self, ds_iso: str, room_id: str) -> Path:
        return self.db.data_dir / "bookings" / f"{ds_iso}_{room_id}.txt"

    def _requests_file(self, ym: str) -> Path:
        return self.db.data_dir / "requests" / f"{ym}.txt"

    def _logs_file(self, ym: str) -> Path:
        return self.db.data_dir / "logs" / f"audit_{ym}.txt"

    def _notif_file(self, user_id: str) -> Path:
        return self.db.data_dir / "notifications" / f"{user_id}.txt"

    def _blocks_file(self, room_id: str) -> Path:
        return self.db.data_dir / "blocks" / f"{room_id}.txt"

    def _meta_file(self, name: str) -> Path:
        return self.db.data_dir / "_meta" / f"{name}.txt"

    def get_runtime_config(self):
        default = {
            "business_start": getattr(self.cfg, "BUSINESS_START", "07:00"),
            "business_end": getattr(self.cfg, "BUSINESS_END", "18:30"),
            "slot_minutes": 15,
            "min_booking_minutes": getattr(self.cfg, "MIN_BOOKING_MINUTES", 15),
            "checkin_grace_minutes": getattr(self.cfg, "CHECKIN_GRACE_MINUTES", 15),
            "user_cancel_limit_minutes": getattr(self.cfg, "USER_CANCEL_LIMIT_MINUTES", 30),
        }
        cfg_path = self._meta_file("config")
        saved = self.db.read_json(cfg_path, {})
        merged = {**default, **saved}
        return merged

    def _next_id(self, key: str, prefix: str) -> str:
        path = self._meta_file("counters")
        with self.db.file_lock(path):
            counters = self.db.read_json(
                path,
                {"users": 0, "bookings": 0, "requests": 0, "audit": 0, "notifications": 0, "blocks": 0},
            )
            counters.setdefault("notifications", 0)
            counters.setdefault("blocks", 0)
            counters[key] = int(counters.get(key, 0)) + 1
            self.db.write_json_atomic(path, counters, use_lock=False)
            return f"{prefix}_{counters[key]:04d}"

    def _audit(self, actor_user_id: str, actor_username: str, action: str, target_type: str, target_id: str, details: dict):
        ts = self.now_iso()
        ym = ts[:7]
        path = self._logs_file(ym)
        event = AuditEvent(
            id=self._next_id("audit", "aud"),
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            created_at=ts,
        )
        data = self.db.read_json(path, {"month": ym, "items": []})
        data["items"].append(event.to_dict())
        self.db.write_json_atomic(path, data)

    def list_audit_events(self, ym: str, action: str = ""):
        events = self.db.read_json(self._logs_file(ym), {"month": ym, "items": []}).get("items", [])
        if action:
            events = [x for x in events if x.get("action") == action]
        return sorted(events, key=lambda x: x.get("created_at", ""), reverse=True)

    def ensure_seed(self):
        counters_path = self._meta_file("counters")
        if not counters_path.exists():
            self.db.write_json_atomic(
                counters_path,
                {"users": 0, "bookings": 0, "requests": 0, "audit": 0, "notifications": 0, "blocks": 0},
            )

        cfg_path = self._meta_file("config")
        if not cfg_path.exists():
            self.db.write_json_atomic(
                cfg_path,
                {
                    "business_start": "07:00",
                    "business_end": "18:30",
                    "slot_minutes": 15,
                    "min_booking_minutes": 15,
                    "checkin_grace_minutes": 15,
                    "user_cancel_limit_minutes": 30,
                },
            )

        for sector in ["RH", "TI", "DESENVOLVIMENTO", "ENGENHARIA"]:
            sfile = self._sectors_dir() / f"{sector}.txt"
            if not sfile.exists():
                self.db.write_json_atomic(sfile, {"name": sector})

        self._migrate_admin_sector_to_rh()

        now = self.now_iso()
        rooms = [
            Room(id="room_1", name="Sala 1", capacity_label="Menor", capacity=6, created_at=now),
            Room(id="room_2", name="Sala 2", capacity_label="Maior", capacity=14, created_at=now),
            Room(id="room_3", name="Sala 3", capacity_label="Média", capacity=10, created_at=now),
        ]
        for room in rooms:
            rfile = self._rooms_dir() / f"{room.id}.txt"
            if not rfile.exists():
                self.db.write_json_atomic(rfile, room.to_dict())

        if not self.find_user_by_username("admin"):
            self.create_user("admin", "RH", ROLE_ADMIN, "admin123", actor_username="system", actor_id="system")
            self.create_user("rh", "RH", ROLE_RH, "rh123", actor_username="system", actor_id="system")
            self.create_user("dev1", "DESENVOLVIMENTO", ROLE_USER, "dev123", actor_username="system", actor_id="system")
            self.create_user("eng1", "ENGENHARIA", ROLE_USER, "eng123", actor_username="system", actor_id="system")
            self.create_user("ti1", "TI", ROLE_USER, "ti123", actor_username="system", actor_id="system")
            self._seed_demo_data()

    def _seed_demo_data(self):
        users = {u.username: u for u in self.list_users()}
        today = self.today_iso()

        booking = Booking(
            id=self._next_id("bookings", "b"),
            room_id="room_1",
            date=today,
            start="09:00",
            end="10:00",
            sector=users["dev1"].sector,
            created_by=users["dev1"].id,
            created_by_username=users["dev1"].username,
            approved_by=users["rh"].id,
            status=BOOK_ACTIVE,
            created_at=self.now_iso(),
            updated_at=self.now_iso(),
        )
        self._save_booking(booking)

        self.create_block(
            room_id="room_2",
            start_date_iso=today,
            end_date_iso=today,
            start="12:00",
            end="13:00",
            reason="Almoço",
            actor=users["rh"],
            weekdays=[datetime.strptime(today, "%Y-%m-%d").isoweekday()],
            audit=False,
        )

        req = self._new_request(
            room_id="room_1",
            date_iso=today,
            start="09:30",
            end="10:30",
            reason="Solicitação com conflito (demo)",
            user=users["eng1"],
        )
        self._save_request(req)

    def list_sectors(self):
        out = []
        for p in sorted(self._sectors_dir().glob("*.txt")):
            data = self.db.read_json(p, {})
            if data.get("name") and data.get("name") != "ADMIN":
                out.append(data["name"])
        return out

    def normalize_sector_name(self, sector: str) -> str:
        clean = (sector or "").strip().upper()
        if not clean:
            raise ValueError("Nome do setor é obrigatório")
        if "/" in clean or "\\" in clean:
            raise ValueError("Nome do setor inválido")
        return clean

    def sector_exists(self, sector: str) -> bool:
        name = self.normalize_sector_name(sector)
        return name in self.list_sectors()

    def create_sector(self, sector: str, actor: User):
        name = self.normalize_sector_name(sector)
        if name == "ADMIN":
            raise ValueError("ADMIN é nível de acesso, não setor")
        if self.sector_exists(name):
            raise ValueError("Setor já existe")
        sfile = self._sectors_dir() / f"{name}.txt"
        self.db.write_json_atomic(sfile, {"name": name, "created_at": self.now_iso()})
        self._audit(actor.id, actor.username, "SECTOR_CREATED", "SECTOR", name, {})
        return name

    def _migrate_admin_sector_to_rh(self):
        admin_sector_file = self._sectors_dir() / "ADMIN.txt"
        if admin_sector_file.exists():
            admin_sector_file.unlink()

        changed = []
        for user in self.list_users():
            if user.sector == "ADMIN":
                user.sector = "RH"
                user.updated_at = self.now_iso()
                self.db.write_json_atomic(self._users_dir() / f"{user.id}.txt", user.to_dict())
                changed.append(user.id)

        if changed:
            self._audit("system", "system", "SECTOR_MIGRATION", "SECTOR", "ADMIN", {"migrated_users": changed, "to": "RH"})

    def list_users_by_sector(self, sector: str):
        name = self.normalize_sector_name(sector)
        return [u for u in self.list_users() if u.sector == name]

    def list_rooms(self):
        rooms = []
        for p in sorted(self._rooms_dir().glob("room_*.txt")):
            data = self.db.read_json(p, {})
            if data:
                data.setdefault("capacity", 0)
                data.setdefault("created_at", "")
                rooms.append(Room(**data))
        return rooms

    def get_room(self, room_id: str) -> Optional[Room]:
        data = self.db.read_json(self._rooms_dir() / f"{room_id}.txt", None)
        if not data:
            return None
        data.setdefault("capacity", 0)
        data.setdefault("created_at", "")
        return Room(**data)

    def list_users(self):
        users = []
        for p in sorted(self._users_dir().glob("u_*.txt")):
            data = self.db.read_json(p, {})
            if data:
                data.setdefault("created_at", "")
                data.setdefault("updated_at", "")
                users.append(User(**data))
        return users

    def get_user(self, user_id: str) -> Optional[User]:
        data = self.db.read_json(self._users_dir() / f"{user_id}.txt", None)
        if not data:
            return None
        data.setdefault("created_at", "")
        data.setdefault("updated_at", "")
        return User(**data)

    def find_user_by_username(self, username: str) -> Optional[User]:
        for user in self.list_users():
            if user.username == username:
                return user
        return None

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.find_user_by_username(username)
        if not user or not user.is_active:
            return None
        return user if verify_password(password, user.password) else None

    def create_user(self, username: str, sector: str, role: str, raw_password: str, actor_username: str, actor_id: str):
        if self.find_user_by_username(username):
            raise ValueError("Usuário já existe")
        sector_name = self.normalize_sector_name(sector)
        if not self.sector_exists(sector_name):
            raise ValueError("Setor inválido")
        uid = self._next_id("users", "u")
        now = self.now_iso()
        u = User(
            id=uid,
            username=username,
            role=role,
            sector=sector_name,
            password=hash_password(
                raw_password,
                algorithm=getattr(self.cfg, "PASSWORD_ALGORITHM", "sha256"),
                iterations=getattr(self.cfg, "PASSWORD_ITERATIONS", 220_000),
                salt_bytes=getattr(self.cfg, "PASSWORD_SALT_BYTES", 16),
            ),
            must_change_password=True,
            created_at=now,
            updated_at=now,
        )
        self.db.write_json_atomic(self._users_dir() / f"{u.id}.txt", u.to_dict())
        self._audit(actor_id, actor_username, "USER_CREATED", "USER", u.id, {"username": username, "role": role, "sector": sector_name})
        return u

    def update_user_role_sector(self, user_id: str, role: str, sector: str, actor_id: str, actor_username: str):
        user = self.get_user(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        sector_name = self.normalize_sector_name(sector)
        if not self.sector_exists(sector_name):
            raise ValueError("Setor inválido")
        user.role = role
        user.sector = sector_name
        user.updated_at = self.now_iso()
        self.db.write_json_atomic(self._users_dir() / f"{user.id}.txt", user.to_dict())
        self._audit(actor_id, actor_username, "USER_UPDATED", "USER", user.id, {"role": role, "sector": sector_name})

    def reset_user_password(self, user_id: str, new_password: str, actor_id: str, actor_username: str):
        user = self.get_user(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        user.password = hash_password(
            new_password,
            algorithm=getattr(self.cfg, "PASSWORD_ALGORITHM", "sha256"),
            iterations=getattr(self.cfg, "PASSWORD_ITERATIONS", 220_000),
            salt_bytes=getattr(self.cfg, "PASSWORD_SALT_BYTES", 16),
        )
        user.must_change_password = True
        user.updated_at = self.now_iso()
        self.db.write_json_atomic(self._users_dir() / f"{user.id}.txt", user.to_dict())
        self._audit(actor_id, actor_username, "PASSWORD_RESET", "USER", user.id, {})

    def delete_user(self, user_id: str, actor: User):
        user = self.get_user(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        if user.id == actor.id:
            raise ValueError("Você não pode excluir o próprio usuário")
        user_file = self._users_dir() / f"{user.id}.txt"
        if user_file.exists():
            user_file.unlink()
        self._audit(actor.id, actor.username, "USER_DELETED", "USER", user.id, {"username": user.username, "sector": user.sector, "role": user.role})

    def change_own_password(self, user: User, current_password: str, new_password: str):
        if not verify_password(current_password, user.password):
            raise ValueError("Senha atual inválida")
        user.password = hash_password(
            new_password,
            algorithm=getattr(self.cfg, "PASSWORD_ALGORITHM", "sha256"),
            iterations=getattr(self.cfg, "PASSWORD_ITERATIONS", 220_000),
            salt_bytes=getattr(self.cfg, "PASSWORD_SALT_BYTES", 16),
        )
        user.must_change_password = False
        user.updated_at = self.now_iso()
        self.db.write_json_atomic(self._users_dir() / f"{user.id}.txt", user.to_dict())
        self._audit(user.id, user.username, "PASSWORD_CHANGED", "USER", user.id, {})

    def _request_from_dict(self, item: dict) -> BookingRequest:
        if "requested_by" not in item:
            item = {
                "id": item.get("id", ""),
                "requested_by": item.get("user_id", ""),
                "username": item.get("username", ""),
                "sector": item.get("sector", ""),
                "room_id": item.get("room_id", ""),
                "date": item.get("date", ""),
                "start": item.get("start", item.get("start_time", "")),
                "end": item.get("end", item.get("end_time", "")),
                "reason": item.get("reason", ""),
                "status": "NEGADA" if item.get("status") == "RECUSADA" else item.get("status", REQ_PENDING),
                "created_at": item.get("created_at", ""),
                "decided_at": item.get("decided_at"),
                "decided_by": item.get("decided_by"),
                "decision_reason": item.get("decision_reason", ""),
                "has_conflict": item.get("has_conflict", item.get("is_conflicting_on_create", False)),
                "conflict_summary": item.get("conflict_summary", ""),
                "recurrence_group_id": item.get("recurrence_group_id", item.get("recurring_group")),
            }
        return BookingRequest(**item)

    def _booking_from_dict(self, item: dict) -> Booking:
        if "created_by" not in item:
            item = {
                "id": item.get("id", ""),
                "room_id": item.get("room_id", ""),
                "date": item.get("date", ""),
                "start": item.get("start", item.get("start_time", "")),
                "end": item.get("end", item.get("end_time", "")),
                "sector": item.get("sector", ""),
                "created_by": item.get("created_by", item.get("user_id", "")),
                "created_by_username": item.get("created_by_username", item.get("username", "")),
                "approved_by": item.get("approved_by", ""),
                "status": item.get("status", BOOK_ACTIVE),
                "request_id": item.get("request_id"),
                "is_emergency": item.get("is_emergency", False),
                "emergency_reason": item.get("emergency_reason", ""),
                "requires_checkin": item.get("requires_checkin", True),
                "checkin_deadline_minutes": item.get("checkin_deadline_minutes", self.get_runtime_config()["checkin_grace_minutes"]),
                "checked_in_at": item.get("checked_in_at", item.get("checkin_confirmed_at")),
                "recurrence_group_id": item.get("recurrence_group_id"),
                "cancel_reason": item.get("cancel_reason", ""),
                "cancelled_by": item.get("cancelled_by", ""),
                "created_at": item.get("created_at", ""),
                "updated_at": item.get("updated_at", ""),
            }
        return Booking(**item)

    def _save_request(self, req: BookingRequest):
        ym = req.date[:7]
        path = self._requests_file(ym)
        data = self.db.read_json(path, {"month": ym, "items": []})
        items = [x for x in data["items"] if x.get("id") != req.id]
        items.append(req.to_dict())
        data["items"] = items
        self.db.write_json_atomic(path, data)

    def _load_request(self, request_id: str) -> Optional[BookingRequest]:
        for path in sorted((self.db.data_dir / "requests").glob("*.txt")):
            data = self.db.read_json(path, {"items": []})
            for item in data.get("items", []):
                if item.get("id") == request_id:
                    return self._request_from_dict(item)
        return None

    def list_requests(self, filters: Optional[dict] = None):
        filters = filters or {}
        out = []
        month = filters.get("month")
        files = [self._requests_file(month)] if month else sorted((self.db.data_dir / "requests").glob("*.txt"))
        for path in files:
            data = self.db.read_json(path, {"items": []})
            for raw in data.get("items", []):
                req = self._request_from_dict(raw)
                if filters.get("status") and req.status != filters["status"]:
                    continue
                if filters.get("room_id") and req.room_id != filters["room_id"]:
                    continue
                if filters.get("sector") and req.sector != filters["sector"]:
                    continue
                if filters.get("date") and req.date != filters["date"]:
                    continue
                if "has_conflict" in filters and filters["has_conflict"] is not None and req.has_conflict != filters["has_conflict"]:
                    continue
                if filters.get("requested_by") and req.requested_by != filters["requested_by"]:
                    continue
                out.append(req)
        out.sort(key=lambda x: (x.date, x.start))
        return out

    def _load_bookings_file(self, ds_iso: str, room_id: str):
        return self.db.read_json(self._bookings_file(ds_iso, room_id), {"date": ds_iso, "room_id": room_id, "items": []})

    def _save_booking(self, booking: Booking):
        data = self._load_bookings_file(booking.date, booking.room_id)
        data["items"] = [x for x in data["items"] if x.get("id") != booking.id]
        data["items"].append(booking.to_dict())
        self.db.write_json_atomic(self._bookings_file(booking.date, booking.room_id), data)

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        for path in sorted((self.db.data_dir / "bookings").glob("*.txt")):
            data = self.db.read_json(path, {"items": []})
            for raw in data.get("items", []):
                if raw.get("id") == booking_id:
                    return self._booking_from_dict(raw)
        return None

    def list_bookings(self, filters: Optional[dict] = None):
        self.expire_due_checkins()
        filters = filters or {}
        out = []
        for path in sorted((self.db.data_dir / "bookings").glob("*.txt")):
            name = path.stem
            if "_room_" not in name:
                continue
            fdate = name.split("_room_")[0]
            if filters.get("date") and filters["date"] != fdate:
                continue
            if filters.get("month") and not fdate.startswith(filters["month"]):
                continue
            if filters.get("room_id") and not name.endswith(filters["room_id"]):
                continue

            data = self.db.read_json(path, {"items": []})
            for raw in data.get("items", []):
                booking = self._booking_from_dict(raw)
                if filters.get("created_by") and booking.created_by != filters["created_by"]:
                    continue
                if filters.get("status") and booking.status != filters["status"]:
                    continue
                if filters.get("sector") and booking.sector != filters["sector"]:
                    continue
                if "is_emergency" in filters and filters["is_emergency"] is not None and booking.is_emergency != filters["is_emergency"]:
                    continue
                if filters.get("date_from") and booking.date < filters["date_from"]:
                    continue
                if filters.get("date_to") and booking.date > filters["date_to"]:
                    continue
                if filters.get("search") and filters["search"].lower() not in (booking.cancel_reason or "").lower() and filters["search"].lower() not in (booking.emergency_reason or "").lower():
                    continue
                out.append(booking)
        out.sort(key=lambda x: (x.date, x.start))
        return out

    def _load_blocks_room(self, room_id: str):
        data = self.db.read_json(self._blocks_file(room_id), {"room_id": room_id, "items": []})
        return data

    def _block_from_dict(self, raw: dict) -> Block:
        raw.setdefault("date", None)
        raw.setdefault("weekday", None)
        raw.setdefault("start_date", raw.get("date"))
        raw.setdefault("end_date", raw.get("date"))
        raw.setdefault("weekdays", [])
        if raw.get("weekdays") is None:
            raw["weekdays"] = []
        if raw.get("weekday") is not None and not raw.get("weekdays"):
            legacy_weekday = int(raw.get("weekday"))
            # Compatibilidade: legado podia estar em 0..6; novo padrão usa 1..7.
            raw["weekdays"] = [legacy_weekday + 1] if 0 <= legacy_weekday <= 6 else [legacy_weekday]
        raw.setdefault("updated_at", raw.get("created_at", ""))
        return Block(**raw)

    def list_blocks(self, room_id: Optional[str] = None, date_iso: Optional[str] = None, active_only: bool = True):
        out = []
        room_ids = [room_id] if room_id else [r.id for r in self.list_rooms()]
        weekday_iso = datetime.strptime(date_iso, "%Y-%m-%d").isoweekday() if date_iso else None
        for rid in room_ids:
            data = self._load_blocks_room(rid)
            for raw in data.get("items", []):
                blk = self._block_from_dict(raw)
                if active_only and blk.status != BLOCK_ACTIVE:
                    continue
                if date_iso:
                    in_date_range = True
                    start_date = blk.start_date or blk.date
                    end_date = blk.end_date or blk.date
                    if start_date and date_iso < start_date:
                        in_date_range = False
                    if end_date and date_iso > end_date:
                        in_date_range = False

                    allowed_weekdays = blk.weekdays or []
                    if blk.weekday is not None and not allowed_weekdays:
                        legacy_weekday = int(blk.weekday)
                        allowed_weekdays = [legacy_weekday + 1] if 0 <= legacy_weekday <= 6 else [legacy_weekday]

                    weekday_match = True if not allowed_weekdays else (weekday_iso in allowed_weekdays)
                    legacy_specific_date_match = (blk.date == date_iso) if blk.date else True

                    if not (in_date_range and weekday_match and legacy_specific_date_match):
                        continue
                out.append(blk)
        out.sort(key=lambda x: (x.room_id, x.start))
        return out

    def create_block(
        self,
        room_id: str,
        start_date_iso: str,
        end_date_iso: str,
        start: str,
        end: str,
        reason: str,
        actor: User,
        weekdays: list[int],
        audit: bool = True,
    ):
        self.validate_booking_window(start_date_iso, start, end)
        datetime.strptime(end_date_iso, "%Y-%m-%d")
        if start_date_iso > end_date_iso:
            raise ValueError("Data início deve ser menor ou igual à data fim")
        if not weekdays:
            raise ValueError("Selecione ao menos um dia da semana")
        weekdays = sorted(set(int(x) for x in weekdays))
        if any(w < 1 or w > 7 for w in weekdays):
            raise ValueError("Dias da semana inválidos")
        if not reason.strip():
            raise ValueError("Motivo do bloqueio é obrigatório")
        blk = Block(
            id=self._next_id("blocks", "blk"),
            room_id=room_id,
            date=None,
            weekday=None,
            start=parse_time_hhmm(start),
            end=parse_time_hhmm(end),
            reason=reason.strip(),
            created_by=actor.id,
            status=BLOCK_ACTIVE,
            start_date=start_date_iso,
            end_date=end_date_iso,
            weekdays=weekdays,
            created_at=self.now_iso(),
            updated_at=self.now_iso(),
        )
        data = self._load_blocks_room(room_id)
        data["items"].append(blk.to_dict())
        self.db.write_json_atomic(self._blocks_file(room_id), data)
        if audit:
            self._audit(
                actor.id,
                actor.username,
                "BLOCK_CREATED",
                "BLOCK",
                blk.id,
                {"room_id": room_id, "start_date": start_date_iso, "end_date": end_date_iso, "weekdays": weekdays},
            )
        return blk

    def disable_block(self, block_id: str, actor: User):
        for room in self.list_rooms():
            data = self._load_blocks_room(room.id)
            changed = False
            for item in data.get("items", []):
                if item.get("id") == block_id:
                    item["status"] = BLOCK_INACTIVE
                    item["updated_at"] = self.now_iso()
                    changed = True
                    self.db.write_json_atomic(self._blocks_file(room.id), data)
                    self._audit(actor.id, actor.username, "BLOCK_DISABLED", "BLOCK", block_id, {"room_id": room.id})
                    return
            if changed:
                break
        raise ValueError("Bloqueio não encontrado")

    def build_time_options(self):
        cfg = self.get_runtime_config()
        start = time_to_minutes(cfg["business_start"])
        end = time_to_minutes(cfg["business_end"])
        step = int(cfg.get("slot_minutes", 15))
        options = []
        cur = start
        while cur <= end:
            options.append(minutes_to_time(cur))
            cur += step
        return options

    def blocked_time_points(self, room_id: str, date_iso: str) -> set[str]:
        cfg = self.get_runtime_config()
        step = int(cfg.get("slot_minutes", 15))
        points = set()
        blocks = self.list_blocks(room_id=room_id, date_iso=date_iso, active_only=True)
        for blk in blocks:
            cur = time_to_minutes(blk.start)
            end = time_to_minutes(blk.end)
            while cur < end:
                points.add(minutes_to_time(cur))
                cur += step
        return points

    def reserved_time_points(self, room_id: str, date_iso: str) -> set[str]:
        cfg = self.get_runtime_config()
        step = int(cfg.get("slot_minutes", 15))
        points = set()
        bookings = self.list_bookings({"room_id": room_id, "date": date_iso})
        for b in bookings:
            if b.status not in (BOOK_ACTIVE, BOOK_IN_PROGRESS):
                continue
            cur = time_to_minutes(b.start)
            end = time_to_minutes(b.end)
            while cur < end:
                points.add(minutes_to_time(cur))
                cur += step
        return points

    def _overlaps(self, a_start: str, a_end: str, b_start: str, b_end: str):
        return time_to_minutes(a_start) < time_to_minutes(b_end) and time_to_minutes(b_start) < time_to_minutes(a_end)

    def validate_booking_window(self, date_iso: str, start: str, end: str):
        datetime.strptime(date_iso, "%Y-%m-%d")
        start = parse_time_hhmm(start)
        end = parse_time_hhmm(end)
        cfg = self.get_runtime_config()
        if time_to_minutes(start) >= time_to_minutes(end):
            raise ValueError("Hora inicial deve ser menor que final")
        if (time_to_minutes(end) - time_to_minutes(start)) < int(cfg["min_booking_minutes"]):
            raise ValueError(f"Duração mínima de {cfg['min_booking_minutes']} minutos")
        if time_to_minutes(start) < time_to_minutes(cfg["business_start"]) or time_to_minutes(end) > time_to_minutes(cfg["business_end"]):
            raise ValueError("Horário fora do expediente")

    def find_conflicting_active_bookings(self, room_id: str, date_iso: str, start: str, end: str):
        conflicts = []
        data = self._load_bookings_file(date_iso, room_id)
        for raw in data.get("items", []):
            b = self._booking_from_dict(raw)
            if b.status not in (BOOK_ACTIVE, BOOK_IN_PROGRESS):
                continue
            if self._overlaps(start, end, b.start, b.end):
                conflicts.append(b)
        return conflicts

    def find_conflicting_blocks(self, room_id: str, date_iso: str, start: str, end: str):
        out = []
        for blk in self.list_blocks(room_id=room_id, date_iso=date_iso, active_only=True):
            if self._overlaps(start, end, blk.start, blk.end):
                out.append(blk)
        return out

    def get_semaphore(self, room_id: str, date_iso: str, start: str, end: str):
        try:
            self.validate_booking_window(date_iso, start, end)
        except Exception as exc:
            return {"color": "vermelho", "label": "Vermelho", "message": str(exc), "can_submit": False}

        block_conflicts = self.find_conflicting_blocks(room_id, date_iso, start, end)
        if block_conflicts:
            blk = block_conflicts[0]
            return {
                "color": "vermelho",
                "label": "Vermelho",
                "message": f"Conflito com bloqueio: {blk.reason}",
                "can_submit": False,
            }

        booking_conflicts = self.find_conflicting_active_bookings(room_id, date_iso, start, end)
        if booking_conflicts:
            first = booking_conflicts[0]
            return {
                "color": "vermelho",
                "label": "Vermelho",
                "message": f"Conflito com reserva ativa de setor {first.sector}",
                "can_submit": False,
            }

        return {"color": "verde", "label": "Verde", "message": "Sem conflito detectado", "can_submit": True}

    def _new_request(self, room_id: str, date_iso: str, start: str, end: str, reason: str, user: User, recurrence_group_id: Optional[str] = None):
        semaphore = self.get_semaphore(room_id, date_iso, start, end)
        if not semaphore["can_submit"]:
            raise ValueError(semaphore["message"])
        req = BookingRequest(
            id=self._next_id("requests", "r"),
            requested_by=user.id,
            username=user.username,
            sector=user.sector,
            room_id=room_id,
            date=date_iso,
            start=start,
            end=end,
            reason=reason.strip(),
            status=REQ_PENDING,
            created_at=self.now_iso(),
            has_conflict=semaphore["color"] == "amarelo",
            conflict_summary=semaphore["message"] if semaphore["color"] == "amarelo" else "",
            recurrence_group_id=recurrence_group_id,
        )
        return req

    def create_request(self, room_id: str, date_iso: str, start: str, end: str, reason: str, user: User):
        req = self._new_request(room_id, date_iso, start, end, reason, user)
        self._save_request(req)
        self._audit(user.id, user.username, "REQUEST_CREATED", "REQUEST", req.id, {"room_id": room_id, "date": date_iso})
        return req

    def create_recurring_weekly_requests(self, room_id: str, start_date_iso: str, start: str, end: str, reason: str, user: User, occurrences: int):
        if occurrences <= 0:
            raise ValueError("Número de ocorrências deve ser maior que zero")
        base = datetime.strptime(start_date_iso, "%Y-%m-%d").date()
        group = f"rec_{uuid.uuid4().hex[:8]}"
        created = []
        for i in range(occurrences):
            date_iso = (base + timedelta(days=7 * i)).strftime("%Y-%m-%d")
            req = self._new_request(room_id, date_iso, start, end, reason, user, recurrence_group_id=group)
            self._save_request(req)
            created.append(req)
        self._audit(user.id, user.username, "REQUEST_RECURRING_CREATED", "REQUEST_GROUP", group, {"count": len(created)})
        return created

    def cancel_request(self, request_id: str, actor: User, reason: str = "", force: bool = False):
        req = self._load_request(request_id)
        if not req:
            raise ValueError("Solicitação não encontrada")
        if req.status != REQ_PENDING:
            raise ValueError("Só é possível cancelar solicitação pendente")
        if not force and req.requested_by != actor.id:
            raise ValueError("Sem permissão")
        req.status = REQ_CANCELLED
        req.decision_reason = reason.strip()
        req.decided_at = self.now_iso()
        req.decided_by = actor.id
        self._save_request(req)
        self._audit(actor.id, actor.username, "REQUEST_CANCELLED", "REQUEST", req.id, {"reason": reason, "force": force})

    def _notify(self, user_id: str, ntype: str, title: str, message: str):
        path = self._notif_file(user_id)
        data = self.db.read_json(path, {"user_id": user_id, "items": []})
        n = Notification(
            id=self._next_id("notifications", "n"),
            user_id=user_id,
            type=ntype,
            title=title,
            message=message,
            created_at=self.now_iso(),
        )
        data["items"].append(n.to_dict())
        self.db.write_json_atomic(path, data)

    def list_notifications(self, user_id: str):
        data = self.db.read_json(self._notif_file(user_id), {"user_id": user_id, "items": []})
        items = data.get("items", [])
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items

    def unread_notification_count(self, user_id: Optional[str]):
        if not user_id:
            return 0
        return len([x for x in self.list_notifications(user_id) if not x.get("read_at")])

    def mark_notification_read(self, user_id: str, notification_id: str):
        path = self._notif_file(user_id)
        data = self.db.read_json(path, {"user_id": user_id, "items": []})
        for item in data.get("items", []):
            if item.get("id") == notification_id:
                item["read_at"] = self.now_iso()
                self.db.write_json_atomic(path, data)
                return
        raise ValueError("Notificação não encontrada")

    def mark_all_notifications_read(self, user_id: str):
        path = self._notif_file(user_id)
        data = self.db.read_json(path, {"user_id": user_id, "items": []})
        for item in data.get("items", []):
            if not item.get("read_at"):
                item["read_at"] = self.now_iso()
        self.db.write_json_atomic(path, data)

    def approve_request(self, request_id: str, actor: User):
        req = self._load_request(request_id)
        if not req or req.status != REQ_PENDING:
            raise ValueError("Solicitação inválida")

        if self.find_conflicting_blocks(req.room_id, req.date, req.start, req.end):
            raise ValueError("Solicitação conflita com bloqueio ativo")

        conflicts = self.find_conflicting_active_bookings(req.room_id, req.date, req.start, req.end)
        if conflicts:
            raise ValueError("Conflito com reserva ativa. Ajuste o horário.")

        booking = Booking(
            id=self._next_id("bookings", "b"),
            room_id=req.room_id,
            date=req.date,
            start=req.start,
            end=req.end,
            sector=req.sector,
            created_by=req.requested_by,
            created_by_username=req.username,
            approved_by=actor.id,
            request_id=req.id,
            recurrence_group_id=req.recurrence_group_id,
            status=BOOK_ACTIVE,
            checkin_deadline_minutes=int(self.get_runtime_config()["checkin_grace_minutes"]),
            created_at=self.now_iso(),
            updated_at=self.now_iso(),
        )
        self._save_booking(booking)

        req.status = REQ_APPROVED
        req.decided_at = self.now_iso()
        req.decided_by = actor.id
        self._save_request(req)

        self._notify(req.requested_by, "REQUEST_APPROVED", "Solicitação aprovada", f"Reserva criada para {format_date_br(req.date)} {req.start}-{req.end}.")
        self._audit(actor.id, actor.username, "REQUEST_APPROVED", "REQUEST", req.id, {"booking_id": booking.id})
        return booking

    def deny_request(self, request_id: str, actor: User, reason: str):
        req = self._load_request(request_id)
        if not req or req.status != REQ_PENDING:
            raise ValueError("Solicitação inválida")
        req.status = REQ_DENIED
        req.decided_by = actor.id
        req.decided_at = self.now_iso()
        req.decision_reason = reason.strip()
        self._save_request(req)
        self._notify(req.requested_by, "REQUEST_DENIED", "Solicitação negada", f"Motivo: {reason or 'Não informado'}")
        self._audit(actor.id, actor.username, "REQUEST_DENIED", "REQUEST", req.id, {"reason": reason})

    def approve_request_group(self, recurrence_group_id: str, actor: User):
        reqs = [r for r in self.list_requests({"status": REQ_PENDING}) if r.recurrence_group_id == recurrence_group_id]
        approved = 0
        failed = 0
        for req in reqs:
            try:
                self.approve_request(req.id, actor)
                approved += 1
            except Exception:
                failed += 1
        for uid in sorted(set(r.requested_by for r in reqs)):
            self._notify(uid, "REQUEST_GROUP_APPROVED", "Recorrência processada", f"Grupo {recurrence_group_id}: {approved} aprovadas, {failed} falhas.")
        return {"total": len(reqs), "approved": approved, "failed": failed}

    def deny_request_group(self, recurrence_group_id: str, actor: User, reason: str):
        reqs = [r for r in self.list_requests({"status": REQ_PENDING}) if r.recurrence_group_id == recurrence_group_id]
        denied = 0
        for req in reqs:
            self.deny_request(req.id, actor, reason)
            denied += 1
        for uid in sorted(set(r.requested_by for r in reqs)):
            self._notify(uid, "REQUEST_GROUP_DENIED", "Recorrência negada", f"Grupo {recurrence_group_id}: {denied} negadas. Motivo: {reason}")
        return {"total": len(reqs), "denied": denied}

    def cancel_booking(self, booking_id: str, actor: User, reason: str, force: bool = False):
        booking = self.get_booking(booking_id)
        if not booking:
            raise ValueError("Reserva não encontrada")
        if booking.status not in (BOOK_ACTIVE, BOOK_IN_PROGRESS):
            raise ValueError("Somente reserva ativa/em andamento pode ser cancelada")
        if not reason.strip():
            raise ValueError("Motivo é obrigatório")

        if not force:
            if booking.created_by != actor.id:
                raise ValueError("Sem permissão")
            start_dt = datetime.strptime(f"{booking.date} {booking.start}", "%Y-%m-%d %H:%M")
            minutes_left = int((start_dt - self.now()).total_seconds() // 60)
            limit = int(self.get_runtime_config()["user_cancel_limit_minutes"])
            if minutes_left < limit:
                raise ValueError(f"Cancelamento permitido somente com {limit} min de antecedência")

        booking.status = BOOK_CANCELLED
        booking.cancel_reason = reason.strip()
        booking.cancelled_by = actor.id
        booking.updated_at = self.now_iso()
        self._save_booking(booking)

        self._notify(booking.created_by, "BOOKING_CANCELLED", "Reserva cancelada", f"Reserva {format_date_br(booking.date)} {booking.start}-{booking.end} cancelada.")
        self._audit(actor.id, actor.username, "BOOKING_CANCELLED", "BOOKING", booking.id, {"reason": reason, "force": force})

    def checkin(self, booking_id: str, actor: User):
        booking = self.get_booking(booking_id)
        if not booking:
            raise ValueError("Reserva não encontrada")
        if booking.created_by != actor.id:
            raise ValueError("Sem permissão")
        if booking.status not in (BOOK_ACTIVE, BOOK_IN_PROGRESS):
            raise ValueError("Reserva não está ativa")
        if booking.checked_in_at:
            raise ValueError("Check-in já realizado")

        start_dt = datetime.strptime(f"{booking.date} {booking.start}", "%Y-%m-%d %H:%M")
        deadline = start_dt + timedelta(minutes=int(booking.checkin_deadline_minutes or 15))
        now = self.now()
        if now < start_dt or now > deadline:
            raise ValueError("Check-in disponível somente entre início e +15 min")

        booking.checked_in_at = self.now_iso()
        booking.updated_at = self.now_iso()
        self._save_booking(booking)
        self._audit(actor.id, actor.username, "BOOKING_CHECKIN", "BOOKING", booking.id, {})

    def expire_due_checkins(self):
        expired_items = []
        now = self.now()
        for path in sorted((self.db.data_dir / "bookings").glob("*.txt")):
            data = self.db.read_json(path, {"items": []})
            dirty = False
            for item in data.get("items", []):
                b = self._booking_from_dict(item)
                if b.status not in (BOOK_ACTIVE, BOOK_IN_PROGRESS):
                    continue

                start_dt = datetime.strptime(f"{b.date} {b.start}", "%Y-%m-%d %H:%M")
                end_dt = datetime.strptime(f"{b.date} {b.end}", "%Y-%m-%d %H:%M")
                new_status = b.status

                if now < start_dt:
                    new_status = BOOK_ACTIVE
                elif start_dt <= now < end_dt:
                    new_status = BOOK_IN_PROGRESS
                else:
                    if b.requires_checkin and not b.checked_in_at:
                        new_status = BOOK_EXPIRED
                    else:
                        new_status = BOOK_DONE

                if new_status != b.status:
                    item["status"] = new_status
                    item["updated_at"] = self.now_iso()
                    dirty = True
                    if new_status == BOOK_EXPIRED:
                        expired_items.append((b.id, b.created_by, b.date, b.start, b.end))
            if dirty:
                self.db.write_json_atomic(path, data)

        for booking_id, user_id, date_iso, start, end in expired_items:
            self._notify(user_id, "BOOKING_EXPIRED", "Reserva expirada", f"Reserva em {format_date_br(date_iso)} {start}-{end} expirou por falta de check-in.")
            self._audit("system", "system", "BOOKING_EXPIRED_AUTO", "BOOKING", booking_id, {})

    def emergency_preview(self, room_id: str, date_iso: str, start: str, end: str):
        return self.find_conflicting_active_bookings(room_id, date_iso, start, end)

    def emergency_booking(self, room_id: str, date_iso: str, start: str, end: str, reason: str, actor: User):
        self.validate_booking_window(date_iso, start, end)
        if not reason.strip():
            raise ValueError("Motivo obrigatório")

        conflicts = self.find_conflicting_active_bookings(room_id, date_iso, start, end)
        impacted_ids = []
        for b in conflicts:
            b.status = BOOK_CANCELLED_EMERGENCY
            b.cancel_reason = reason.strip()
            b.cancelled_by = actor.id
            b.updated_at = self.now_iso()
            self._save_booking(b)
            impacted_ids.append(b.id)
            self._notify(b.created_by, "BOOKING_EMERGENCY", "Reserva cancelada por emergência", f"Sua reserva de {format_date_br(b.date)} {b.start}-{b.end} foi cancelada por emergência RH.")

        emergency = Booking(
            id=self._next_id("bookings", "b"),
            room_id=room_id,
            date=date_iso,
            start=start,
            end=end,
            sector=actor.sector,
            created_by=actor.id,
            created_by_username=actor.username,
            approved_by=actor.id,
            status=BOOK_ACTIVE,
            is_emergency=True,
            emergency_reason=reason.strip(),
            requires_checkin=False,
            created_at=self.now_iso(),
            updated_at=self.now_iso(),
        )
        self._save_booking(emergency)

        self._audit(
            actor.id,
            actor.username,
            "EMERGENCY_BOOKING_CREATED",
            "BOOKING",
            emergency.id,
            {"impacted": impacted_ids, "room_id": room_id, "date": date_iso, "start": start, "end": end},
        )
        return emergency, conflicts

    def _interval_taken(self, room_id: str, date_iso: str, start: str, end: str):
        if self.find_conflicting_active_bookings(room_id, date_iso, start, end):
            return True
        if self.find_conflicting_blocks(room_id, date_iso, start, end):
            return True
        return False

    def suggest_free_slots(self, room_id: str, date_iso: str, duration_minutes: int, limit: int = 5):
        cfg = self.get_runtime_config()
        step = int(cfg["slot_minutes"])
        start_min = time_to_minutes(cfg["business_start"])
        end_min = time_to_minutes(cfg["business_end"])
        out = []
        cur = start_min
        while cur + duration_minutes <= end_min and len(out) < limit:
            start = minutes_to_time(cur)
            end = minutes_to_time(cur + duration_minutes)
            if not self._interval_taken(room_id, date_iso, start, end):
                out.append({"start": start, "end": end})
            cur += step
        return out

    def schedule_for_room(self, room_id: str, date_iso: str, viewer: User):
        cfg = self.get_runtime_config()
        step = int(cfg["slot_minutes"])
        slots = []
        blocks = self.list_blocks(room_id=room_id, date_iso=date_iso, active_only=True)
        bookings = self.list_bookings({"room_id": room_id, "date": date_iso})

        cur = time_to_minutes(cfg["business_start"])
        end_limit = time_to_minutes(cfg["business_end"])
        while cur < end_limit:
            slot_start = minutes_to_time(cur)
            slot_end = minutes_to_time(cur + step)
            entry = {
                "time": slot_start,
                "status_key": "free",
                "status_label": "Livre",
                "badge": "success",
                "detail": "Livre",
            }

            matching_block = next((b for b in blocks if self._overlaps(slot_start, slot_end, b.start, b.end)), None)
            if matching_block:
                entry.update({"status_key": "blocked", "status_label": "Bloqueado", "badge": "dark", "detail": f"Bloqueio - {matching_block.reason}"})
            else:
                matching_booking = next((b for b in bookings if b.status in (BOOK_ACTIVE, BOOK_IN_PROGRESS) and self._overlaps(slot_start, slot_end, b.start, b.end)), None)
                if matching_booking:
                    is_mine = viewer and matching_booking.created_by == viewer.id
                    if viewer.role in (ROLE_ADMIN, ROLE_RH):
                        detail = f"Reservado - {matching_booking.created_by_username} ({matching_booking.sector})"
                    else:
                        detail = "Minha reserva" if is_mine else f"Reservado - {matching_booking.sector}"
                    entry.update({"status_key": "mine" if is_mine else "reserved", "status_label": "Reservado", "badge": "primary" if is_mine else "secondary", "detail": detail})
            slots.append(entry)
            cur += step
        return slots

    def my_dashboard(self, user: User):
        today = self.today_iso()
        bookings_today = [b for b in self.list_bookings({"created_by": user.id, "date": today}) if b.status in (BOOK_ACTIVE, BOOK_IN_PROGRESS)]
        upcoming = [b for b in self.list_bookings({"created_by": user.id}) if b.status == BOOK_ACTIVE and (b.date > today or (b.date == today and b.start >= self.now().strftime('%H:%M')))]
        pending = self.list_requests({"requested_by": user.id, "status": REQ_PENDING})
        notifications = self.list_notifications(user.id)[:5]
        return {
            "bookings_today": bookings_today,
            "upcoming": upcoming[:5],
            "pending": pending[:5],
            "notifications": notifications,
        }

    def admin_dashboard(self):
        today = self.today_iso()
        pending = len(self.list_requests({"status": REQ_PENDING}))
        conflicts = len([r for r in self.list_requests({"status": REQ_PENDING}) if r.has_conflict])
        no_show = len([b for b in self.list_bookings({"month": today[:7]}) if b.status == BOOK_EXPIRED])
        today_bookings = [b for b in self.list_bookings({"date": today}) if b.status in (BOOK_ACTIVE, BOOK_IN_PROGRESS)]
        by_room = {}
        for b in today_bookings:
            by_room[b.room_id] = by_room.get(b.room_id, 0) + 1
        return {
            "pending_requests": pending,
            "today_by_room": by_room,
            "conflicts_pending": conflicts,
            "no_show": no_show,
        }

    def group_requests_for_display(self, requests):
        groups = {}
        for req in requests:
            key = req.recurrence_group_id or req.id
            groups.setdefault(key, []).append(req)
        return groups

    def date_br_to_iso_or_today(self, value: str):
        if not value:
            return self.today_iso()
        return parse_date_br(value)
