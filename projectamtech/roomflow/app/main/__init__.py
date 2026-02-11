"""Blueprint principal (área pública e usuário comum)."""

from flask import Blueprint

bp = Blueprint("main", __name__)

from . import routes  # noqa: E402,F401
