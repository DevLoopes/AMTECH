"""Rotas do usuário final.

Conecta templates `main/*` com os serviços de agenda, solicitação,
check-in, cancelamento e notificações.
"""

from datetime import datetime, timedelta

from flask import current_app, flash, g, redirect, render_template, request, url_for

from app.auth.decorators import login_required
from app.storage.services import BOOK_ACTIVE, REQ_PENDING, ROLE_ADMIN, ROLE_RH
from app.storage.validators import format_date_br, parse_date_br
from . import bp


@bp.route("/")
def index():
    if g.user:
        if g.user.role in (ROLE_ADMIN, ROLE_RH):
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("main.my_dashboard"))
    return render_template("main/index.html")


@bp.route("/rooms")
@login_required
def rooms():
    rooms = current_app.roomflow.list_rooms()
    return render_template("main/rooms.html", rooms=rooms)


@bp.route("/room/<room_id>/schedule")
@login_required
def room_schedule(room_id):
    service = current_app.roomflow
    room = service.get_room(room_id)
    if not room:
        flash("Sala inválida.", "danger")
        return redirect(url_for("main.rooms"))

    date_br = request.args.get("date", "") or service.today_br()
    try:
        date_iso = parse_date_br(date_br)
    except ValueError:
        date_iso = service.today_iso()
        date_br = format_date_br(date_iso)

    try:
        duration = int(request.args.get("duration", "30") or 30)
    except ValueError:
        duration = 30
    status_filter = request.args.get("status", "")
    schedule = service.schedule_for_room(room_id, date_iso, g.user)
    if status_filter:
        schedule = [s for s in schedule if s["status_key"] == status_filter]

    suggestions = service.suggest_free_slots(room_id, date_iso, duration, limit=5)

    prev_date_br = format_date_br((datetime.strptime(date_iso, "%Y-%m-%d").date() - timedelta(days=1)).strftime("%Y-%m-%d"))
    next_date_br = format_date_br((datetime.strptime(date_iso, "%Y-%m-%d").date() + timedelta(days=1)).strftime("%Y-%m-%d"))

    return render_template(
        "main/schedule_room.html",
        room=room,
        date_br=date_br,
        schedule=schedule,
        suggestions=suggestions,
        duration=duration,
        prev_date_br=prev_date_br,
        next_date_br=next_date_br,
        filter_status=status_filter,
    )


@bp.route("/room/<room_id>/request", methods=["GET", "POST"])
@login_required
def room_request(room_id):
    service = current_app.roomflow
    room = service.get_room(room_id)
    if not room:
        flash("Sala inválida.", "danger")
        return redirect(url_for("main.rooms"))

    date_br = request.args.get("date", "") or service.today_br()
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    reason = ""
    recurring_weeks = 0

    if request.method == "POST":
        date_br = request.form.get("date", "").strip()
        start = request.form.get("start", "").strip()
        end = request.form.get("end", "").strip()
        reason = request.form.get("reason", "").strip()
        recurring_weeks = int(request.form.get("recurring_weeks", "0") or 0)
        use_recurring = bool(request.form.get("use_recurring"))

        try:
            date_iso = parse_date_br(date_br)
            if use_recurring and recurring_weeks > 0:
                created = service.create_recurring_weekly_requests(
                    room_id=room_id,
                    start_date_iso=date_iso,
                    start=start,
                    end=end,
                    reason=reason,
                    user=g.user,
                    occurrences=recurring_weeks,
                )
                flash(f"{len(created)} solicitações recorrentes criadas.", "success")
            else:
                service.create_request(room_id=room_id, date_iso=date_iso, start=start, end=end, reason=reason, user=g.user)
                flash("Solicitação enviada com sucesso.", "success")
            return redirect(url_for("main.my_requests"))
        except Exception as exc:
            flash(str(exc), "danger")

    try:
        date_iso_preview = parse_date_br(date_br)
    except Exception:
        date_iso_preview = service.today_iso()
        date_br = format_date_br(date_iso_preview)

    semaphore = None
    if start and end:
        semaphore = service.get_semaphore(room_id, date_iso_preview, start, end)
    blocked_times = service.blocked_time_points(room_id, date_iso_preview)
    reserved_times = service.reserved_time_points(room_id, date_iso_preview)
    unavailable_times = blocked_times | reserved_times

    return render_template(
        "main/request_form.html",
        room=room,
        date_br=date_br,
        start=start,
        end=end,
        reason=reason,
        recurring_weeks=recurring_weeks,
        time_options=service.build_time_options(),
        blocked_times=blocked_times,
        reserved_times=reserved_times,
        unavailable_times=unavailable_times,
        semaphore=semaphore,
    )


@bp.route("/my")
@login_required
def my_dashboard():
    data = current_app.roomflow.my_dashboard(g.user)
    return render_template("main/my_dashboard.html", data=data)


@bp.route("/my/requests")
@login_required
def my_requests():
    service = current_app.roomflow
    reqs = service.list_requests(
        {
            "requested_by": g.user.id,
            "status": request.args.get("status") or None,
            "room_id": request.args.get("room_id") or None,
        }
    )
    return render_template("main/my_requests.html", requests=reqs)


@bp.route("/my/requests/<request_id>/cancel", methods=["POST"])
@login_required
def my_cancel_request(request_id):
    reason = request.form.get("reason", "Cancelamento pelo usuário")
    try:
        current_app.roomflow.cancel_request(request_id, g.user, reason=reason, force=False)
        flash("Solicitação cancelada.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("main.my_requests"))


@bp.route("/my/bookings")
@login_required
def my_bookings():
    service = current_app.roomflow
    date_from = None
    date_to = None
    try:
        date_from = parse_date_br(request.args.get("date_from")) if request.args.get("date_from") else None
    except ValueError:
        flash("Data inicial inválida. Use DD/MM/AAAA.", "warning")
    try:
        date_to = parse_date_br(request.args.get("date_to")) if request.args.get("date_to") else None
    except ValueError:
        flash("Data final inválida. Use DD/MM/AAAA.", "warning")

    filters = {
        "created_by": g.user.id,
        "room_id": request.args.get("room_id") or None,
        "status": request.args.get("status") or None,
        "date_from": date_from,
        "date_to": date_to,
    }
    bookings = service.list_bookings(filters)
    return render_template("main/my_bookings.html", bookings=bookings, now=datetime.now(), rooms=service.list_rooms())


@bp.route("/my/bookings/<booking_id>/cancel", methods=["POST"])
@login_required
def my_cancel_booking(booking_id):
    reason = request.form.get("reason", "").strip()
    try:
        current_app.roomflow.cancel_booking(booking_id, g.user, reason=reason, force=False)
        flash("Reserva cancelada.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("main.my_bookings"))


@bp.route("/booking/<booking_id>/checkin", methods=["POST"])
@login_required
def booking_checkin(booking_id):
    try:
        current_app.roomflow.checkin(booking_id, g.user)
        flash("Check-in confirmado.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("main.my_bookings"))


@bp.route("/my/notifications")
@login_required
def my_notifications():
    notifications = current_app.roomflow.list_notifications(g.user.id)
    return render_template("main/notifications.html", notifications=notifications)


@bp.route("/my/notifications/<notification_id>/read", methods=["POST"])
@login_required
def my_notification_read(notification_id):
    try:
        current_app.roomflow.mark_notification_read(g.user.id, notification_id)
        flash("Notificação marcada como lida.", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("main.my_notifications"))


@bp.route("/my/notifications/read-all", methods=["POST"])
@login_required
def my_notifications_read_all():
    current_app.roomflow.mark_all_notifications_read(g.user.id)
    flash("Todas as notificações foram marcadas como lidas.", "success")
    return redirect(url_for("main.my_notifications"))
