"""Blueprint de autenticação.

Expõe rotas de login/logout/troca de senha.
"""

from flask import Blueprint

bp = Blueprint("auth", __name__)

from . import routes  # noqa: E402,F401
