"""Rotas administrativas.

Inclui dashboards, decisões de solicitação, gestão de reservas,
emergências, bloqueios, usuários, setores e auditoria.
"""

from datetime import datetime

from flask import current_app, flash, g, redirect, render_template, request, url_for

from app.auth.decorators import require_roles
from app.storage.services import REQ_PENDING, ROLE_ADMIN, ROLE_RH
from app.storage.validators import parse_date_br
from . import bp


@bp.route("/dashboard")
@require_roles([ROLE_ADMIN, ROLE_RH])
def dashboard():
    return render_template("admin/dashboard.html", metrics=current_app.roomflow.admin_dashboard())


@bp.route("/requests")
@require_roles([ROLE_ADMIN, ROLE_RH])
def requests_list():
    service = current_app.roomflow
    conflict_raw = request.args.get("conflict")
    has_conflict = None
    if conflict_raw == "yes":
        has_conflict = True
    elif conflict_raw == "no":
        has_conflict = False

    date_iso = None
    if request.args.get("date"):
        try:
            date_iso = parse_date_br(request.args.get("date"))
        except ValueError:
            flash("Data inválida no filtro. Use DD/MM/AAAA.", "warning")

    filters = {
        "status": request.args.get("status") or None,
        "room_id": request.args.get("room_id") or None,
        "sector": request.args.get("sector") or None,
        "date": date_iso,
        "has_conflict": has_conflict,
    }
    requests_data = service.list_requests(filters)
    groups = service.group_requests_for_display(requests_data)
    return render_template(
        "admin/requests.html",
        requests=requests_data,
        groups=groups,
        rooms=service.list_rooms(),
        sectors=service.list_sectors(),
    )


@bp.route("/requests/<request_id>/approve", methods=["POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def request_approve(request_id):
    try:
        current_app.roomflow.approve_request(request_id, g.user)
        flash("Solicitação aprovada.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.requests_list"))


@bp.route("/requests/<request_id>/deny", methods=["POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def request_deny(request_id):
    reason = request.form.get("reason", "")
    try:
        current_app.roomflow.deny_request(request_id, g.user, reason)
        flash("Solicitação negada.", "info")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.requests_list"))


@bp.route("/requests/group/<recurrence_group_id>/approve", methods=["POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def request_group_approve(recurrence_group_id):
    result = current_app.roomflow.approve_request_group(recurrence_group_id, g.user)
    flash(f"Grupo {recurrence_group_id}: {result['approved']} aprovadas, {result['failed']} falhas.", "success")
    return redirect(url_for("admin.requests_list"))


@bp.route("/requests/group/<recurrence_group_id>/deny", methods=["POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def request_group_deny(recurrence_group_id):
    reason = request.form.get("reason", "")
    result = current_app.roomflow.deny_request_group(recurrence_group_id, g.user, reason)
    flash(f"Grupo {recurrence_group_id}: {result['denied']} negadas.", "info")
    return redirect(url_for("admin.requests_list"))


@bp.route("/bookings")
@require_roles([ROLE_ADMIN, ROLE_RH])
def bookings_list():
    service = current_app.roomflow
    date_iso = None
    if request.args.get("date"):
        try:
            date_iso = parse_date_br(request.args.get("date"))
        except ValueError:
            flash("Data inválida no filtro. Use DD/MM/AAAA.", "warning")
    filters = {
        "room_id": request.args.get("room_id") or None,
        "sector": request.args.get("sector") or None,
        "status": request.args.get("status") or None,
        "date": date_iso,
        "is_emergency": True if request.args.get("emergency") == "yes" else (False if request.args.get("emergency") == "no" else None),
    }
    bookings = service.list_bookings(filters)
    return render_template("admin/bookings.html", bookings=bookings, rooms=service.list_rooms(), sectors=service.list_sectors())


@bp.route("/bookings/<booking_id>/cancel", methods=["POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def booking_cancel(booking_id):
    reason = request.form.get("reason", "").strip()
    try:
        current_app.roomflow.cancel_booking(booking_id, g.user, reason=reason, force=True)
        flash("Reserva cancelada.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.bookings_list"))


@bp.route("/emergency", methods=["GET", "POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def emergency():
    service = current_app.roomflow
    preview = []
    date_br = request.form.get("date") if request.method == "POST" else service.today_br()
    if request.method == "POST":
        room_id = request.form.get("room_id", "")
        start = request.form.get("start", "")
        end = request.form.get("end", "")
        reason = request.form.get("reason", "")
        action = request.form.get("action", "preview")
        try:
            date_iso = parse_date_br(date_br)
            preview = service.emergency_preview(room_id, date_iso, start, end)
            if action == "confirm":
                emergency_booking, impacted = service.emergency_booking(room_id, date_iso, start, end, reason, g.user)
                flash(f"Emergência criada ({emergency_booking.id}) com {len(impacted)} reservas impactadas.", "warning")
                return redirect(url_for("admin.bookings_list"))
        except Exception as exc:
            flash(str(exc), "danger")

    return render_template("admin/emergency.html", rooms=service.list_rooms(), preview=preview, date_br=date_br)


@bp.route("/blocks", methods=["GET", "POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def blocks():
    service = current_app.roomflow
    if request.method == "POST":
        try:
            room_id = request.form.get("room_id", "")
            start_date_br = request.form.get("start_date", "")
            end_date_br = request.form.get("end_date", "")
            start = request.form.get("start", "")
            end = request.form.get("end", "")
            reason = request.form.get("reason", "")
            weekdays = [int(x) for x in request.form.getlist("weekdays")]
            start_date_iso = parse_date_br(start_date_br)
            end_date_iso = parse_date_br(end_date_br)
            service.create_block(
                room_id=room_id,
                start_date_iso=start_date_iso,
                end_date_iso=end_date_iso,
                start=start,
                end=end,
                reason=reason,
                actor=g.user,
                weekdays=weekdays,
            )
            flash("Bloqueio criado.", "success")
            return redirect(url_for("admin.blocks"))
        except Exception as exc:
            flash(str(exc), "danger")

    room_id_filter = request.args.get("room_id")
    blocks_data = service.list_blocks(room_id=room_id_filter, active_only=False)
    return render_template("admin/blocks.html", rooms=service.list_rooms(), blocks=blocks_data, today_br=service.today_br())


@bp.route("/blocks/<block_id>/disable", methods=["POST"])
@require_roles([ROLE_ADMIN, ROLE_RH])
def blocks_disable(block_id):
    try:
        current_app.roomflow.disable_block(block_id, g.user)
        flash("Bloqueio desativado.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.blocks"))


@bp.route("/logs")
@require_roles([ROLE_ADMIN, ROLE_RH])
def logs():
    ym = request.args.get("month") or datetime.now().strftime("%Y-%m")
    action = request.args.get("action", "")
    events = current_app.roomflow.list_audit_events(ym, action=action)
    return render_template("admin/logs.html", events=events, month=ym, action=action)


@bp.route("/users")
@require_roles([ROLE_ADMIN])
def users_list():
    service = current_app.roomflow
    return render_template("admin/users.html", users=service.list_users(), sectors=service.list_sectors())


@bp.route("/users/new", methods=["GET", "POST"])
@require_roles([ROLE_ADMIN])
def users_new():
    service = current_app.roomflow
    if request.method == "POST":
        try:
            service.create_user(
                username=request.form.get("username", "").strip(),
                sector=request.form.get("sector", ""),
                role=request.form.get("role", ""),
                raw_password=request.form.get("password", ""),
                actor_username=g.user.username,
                actor_id=g.user.id,
            )
            flash("Usuário criado.", "success")
            return redirect(url_for("admin.users_list"))
        except Exception as exc:
            flash(str(exc), "danger")
    return render_template("admin/user_form.html", sectors=service.list_sectors(), user=None)


@bp.route("/users/<user_id>/edit", methods=["GET", "POST"])
@require_roles([ROLE_ADMIN])
def users_edit(user_id):
    service = current_app.roomflow
    user_obj = service.get_user(user_id)
    if not user_obj:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin.users_list"))
    if request.method == "POST":
        try:
            service.update_user_role_sector(user_obj.id, request.form.get("role", ""), request.form.get("sector", ""), g.user.id, g.user.username)
            flash("Usuário atualizado.", "success")
            return redirect(url_for("admin.users_list"))
        except Exception as exc:
            flash(str(exc), "danger")
    return render_template("admin/user_form.html", sectors=service.list_sectors(), user=user_obj)


@bp.route("/users/<user_id>/reset-password", methods=["POST"])
@require_roles([ROLE_ADMIN])
def users_reset_password(user_id):
    try:
        current_app.roomflow.reset_user_password(user_id, request.form.get("password", ""), g.user.id, g.user.username)
        flash("Senha resetada.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.users_list"))


@bp.route("/users/<user_id>/delete", methods=["POST"])
@require_roles([ROLE_ADMIN])
def users_delete(user_id):
    try:
        current_app.roomflow.delete_user(user_id, g.user)
        flash("Usuário excluído.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("admin.users_list"))


@bp.route("/sectors", methods=["GET", "POST"])
@require_roles([ROLE_ADMIN])
def sectors_list():
    service = current_app.roomflow
    if request.method == "POST":
        try:
            sector_name = request.form.get("sector_name", "")
            service.create_sector(sector_name, g.user)
            flash("Setor criado com sucesso.", "success")
            return redirect(url_for("admin.sectors_list"))
        except Exception as exc:
            flash(str(exc), "danger")

    sectors = service.list_sectors()
    sector_counts = {s: len(service.list_users_by_sector(s)) for s in sectors}
    return render_template("admin/sectors.html", sectors=sectors, sector_counts=sector_counts)


@bp.route("/sectors/<path:sector_name>")
@require_roles([ROLE_ADMIN])
def sector_detail(sector_name):
    service = current_app.roomflow
    try:
        sector = service.normalize_sector_name(sector_name)
    except Exception:
        flash("Setor inválido.", "danger")
        return redirect(url_for("admin.sectors_list"))

    if not service.sector_exists(sector):
        flash("Setor não encontrado.", "danger")
        return redirect(url_for("admin.sectors_list"))

    users = service.list_users_by_sector(sector)
    return render_template("admin/sector_detail.html", sector=sector, users=users, sectors=service.list_sectors())


@bp.route("/sectors/<path:sector_name>/users/<user_id>/update", methods=["POST"])
@require_roles([ROLE_ADMIN])
def sector_user_update(sector_name, user_id):
    service = current_app.roomflow
    return_sector = request.form.get("return_sector", sector_name)
    role = request.form.get("role", "")
    sector = request.form.get("sector", "")
    try:
        service.update_user_role_sector(user_id, role, sector, g.user.id, g.user.username)
        flash("Usuário atualizado.", "success")
        return redirect(url_for("admin.sector_detail", sector_name=sector))
    except Exception as exc:
        flash(str(exc), "danger")
        return redirect(url_for("admin.sector_detail", sector_name=return_sector))
