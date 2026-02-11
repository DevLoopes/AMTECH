"""Rotas de autenticação.

Conecta UI (`templates/auth/*`) com regras de senha no `RoomFlowService`.
"""

from flask import flash, g, redirect, render_template, session, url_for, current_app

from . import bp
from .decorators import login_required
from .forms import ChangePasswordForm, LoginForm


def _dashboard_route_for(user):
    if user.role in ("ADMIN", "RH"):
        return "admin.dashboard"
    return "main.my_dashboard"


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for(_dashboard_route_for(g.user)))

    form = LoginForm()
    if form.validate_on_submit():
        service = current_app.roomflow
        user = service.authenticate(form.username.data.strip(), form.password.data)
        if not user:
            flash("Credenciais inválidas.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            flash("Login realizado com sucesso.", "success")
            if user.must_change_password:
                return redirect(url_for("auth.change_password"))
            return redirect(url_for(_dashboard_route_for(user)))
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("main.index"))


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            current_app.roomflow.change_own_password(g.user, form.current_password.data, form.new_password.data)
            flash("Senha alterada com sucesso.", "success")
            return redirect(url_for(_dashboard_route_for(g.user)))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("auth/change_password.html", form=form)
