"""Funções de segurança de senha.

Implementa hash/verificação PBKDF2-HMAC com comparação segura.
"""

import base64
import hashlib
import hmac
import secrets


def hash_password(password: str, algorithm: str = "sha256", iterations: int = 220_000, salt_bytes: int = 16) -> dict:
    salt = secrets.token_bytes(salt_bytes)
    digest = hashlib.pbkdf2_hmac(algorithm, password.encode("utf-8"), salt, iterations)
    return {
        "algo": algorithm,
        "iterations": iterations,
        "salt": base64.b64encode(salt).decode("utf-8"),
        "hash": base64.b64encode(digest).decode("utf-8"),
    }


def verify_password(password: str, stored: dict) -> bool:
    algo = stored.get("algo", "sha256")
    iterations = int(stored.get("iterations", 220_000))
    salt = base64.b64decode(stored["salt"])
    expected = base64.b64decode(stored["hash"])
    digest = hashlib.pbkdf2_hmac(algo, password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest, expected)
