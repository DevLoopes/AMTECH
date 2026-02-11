"""App Factory do RoomFlow.

Responsável por:
- carregar configuração;
- inicializar persistência TXT/JSON (`FileDB` + `RoomFlowService`);
- registrar blueprints (`auth`, `main`, `admin`);
- injetar helpers globais para templates.
"""

from flask import Flask, g, render_template

from .auth.decorators import load_logged_user
from .config import Config
from .storage.filedb import FileDB
from .storage.services import RoomFlowService
from .storage.validators import format_date_br, weekday_pt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db = FileDB(
        app.config["DATA_DIR"],
        lock_timeout=app.config["LOCK_TIMEOUT_SECONDS"],
        lock_stale=app.config["LOCK_STALE_SECONDS"],
    )
    app.roomflow = RoomFlowService(db, config_class)
    app.roomflow.ensure_seed()

    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def _load_user():
        load_logged_user()
        if getattr(g, "user", None):
            app.roomflow.expire_due_checkins()

    @app.context_processor
    def inject_globals():
        user = getattr(g, "user", None)
        unread = app.roomflow.unread_notification_count(user.id) if user else 0
        return {
            "current_user": user,
            "unread_notifications": unread,
            "format_date_br": format_date_br,
            "weekday_pt": weekday_pt,
            "runtime_config": app.roomflow.get_runtime_config(),
        }

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_e):
        return render_template("errors/500.html"), 500

    return app
