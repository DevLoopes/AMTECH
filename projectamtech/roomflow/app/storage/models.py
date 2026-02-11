"""Modelos de dados do domínio RoomFlow (dataclasses)."""

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class User:
    id: str
    username: str
    role: str
    sector: str
    password: dict
    created_at: str = ""
    updated_at: str = ""
    must_change_password: bool = False
    is_active: bool = True

    def to_dict(self):
        return asdict(self)


@dataclass
class Room:
    id: str
    name: str
    capacity_label: str
    capacity: int = 0
    created_at: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class BookingRequest:
    id: str
    requested_by: str
    username: str
    sector: str
    room_id: str
    date: str
    start: str
    end: str
    reason: str
    status: str
    created_at: str
    decided_at: Optional[str] = None
    decided_by: Optional[str] = None
    decision_reason: str = ""
    has_conflict: bool = False
    conflict_summary: str = ""
    recurrence_group_id: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Booking:
    id: str
    room_id: str
    date: str
    start: str
    end: str
    sector: str
    created_by: str
    created_by_username: str
    approved_by: str
    status: str
    request_id: Optional[str] = None
    is_emergency: bool = False
    emergency_reason: str = ""
    requires_checkin: bool = True
    checkin_deadline_minutes: int = 15
    checked_in_at: Optional[str] = None
    recurrence_group_id: Optional[str] = None
    cancel_reason: str = ""
    cancelled_by: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Block:
    id: str
    room_id: str
    date: Optional[str]
    weekday: Optional[int]
    start: str
    end: str
    reason: str
    created_by: str
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    weekdays: list[int] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Notification:
    id: str
    user_id: str
    type: str
    title: str
    message: str
    created_at: str
    read_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class AuditEvent:
    id: str
    actor_user_id: str
    actor_username: str
    action: str
    target_type: str
    target_id: str
    details: dict = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self):
        return asdict(self)
