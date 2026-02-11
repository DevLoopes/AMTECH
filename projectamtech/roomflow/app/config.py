"""Configuração central do RoomFlow.

Define paths, segurança de senha e regras de negócio padrão
(expediente, check-in, janela de cancelamento e lock de arquivos).
"""

from pathlib import Path


class Config:
    SECRET_KEY = "change-this-in-production"
    BASE_DIR = Path(__file__).resolve().parents[1]
    DATA_DIR = BASE_DIR / "data"

    PASSWORD_ALGORITHM = "sha256"
    PASSWORD_ITERATIONS = 220_000
    PASSWORD_SALT_BYTES = 16

    BUSINESS_START = "07:00"
    BUSINESS_END = "18:30"
    MIN_BOOKING_MINUTES = 15
    USER_CANCEL_LIMIT_MINUTES = 30
    CHECKIN_GRACE_MINUTES = 15

    LOCK_TIMEOUT_SECONDS = 5
    LOCK_STALE_SECONDS = 20
