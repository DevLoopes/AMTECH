"""Blueprint administrativo.

Agrupa rotas de RH/Admin e rotas exclusivas do ADMIN.
"""

from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

from . import routes  # noqa: E402,F401
