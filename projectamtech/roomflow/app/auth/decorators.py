"""Decorators de autenticação/autorização.

Integra com `flask.session` e com `RoomFlowService.get_user`.
"""

from functools import wraps

from flask import current_app, flash, g, redirect, session, url_for


def load_logged_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id:
        g.user = current_app.roomflow.get_user(user_id)


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Faça login para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return wrapped


def require_roles(roles: list[str]):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if g.user is None:
                flash("Faça login para continuar.", "warning")
                return redirect(url_for("auth.login"))
            if g.user.role not in roles:
                flash("Sem permissão para acessar esta área.", "danger")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)

        return wrapped

    return decorator
