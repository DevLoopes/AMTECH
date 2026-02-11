"""Helpers de validação e conversão de data/hora."""

from datetime import datetime


def parse_date_br(value: str) -> str:
    if not value:
        raise ValueError("Data obrigatória")
    try:
        return datetime.strptime(value, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Data inválida. Use DD/MM/AAAA") from exc


def format_date_br(value_iso: str) -> str:
    if not value_iso:
        return ""
    try:
        return datetime.strptime(value_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return value_iso


def parse_time_hhmm(value: str) -> str:
    if not value:
        raise ValueError("Horário obrigatório")
    try:
        return datetime.strptime(value, "%H:%M").strftime("%H:%M")
    except ValueError as exc:
        raise ValueError("Hora inválida. Use HH:MM") from exc


def time_to_minutes(value: str) -> int:
    hhmm = parse_time_hhmm(value)
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def minutes_to_time(value: int) -> str:
    if value < 0 or value >= 24 * 60:
        raise ValueError("Minutos fora do intervalo diário")
    h = value // 60
    m = value % 60
    return f"{h:02d}:{m:02d}"


def weekday_pt(value: str) -> str:
    if not value:
        return ""
    weekdays = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            return weekdays[dt.weekday()]
        except ValueError:
            continue
    return ""
