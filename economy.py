# =========================
# economy.py — Sistema Anti-Monopolio
# =========================

from config import (
    TIER_CUSPIDE_MIN, TIER_ELITE_MIN, TIER_MEDIO_MIN,
    MULTIPLICADOR_CUSPIDE, MULTIPLICADOR_ELITE, MULTIPLICADOR_MEDIO,
    MULTIPLICADOR_PUEBLO, MULTIPLICADOR_NEUTRO
)
from balance import balance_global

TIERS = {
    "cuspide": {
        "nombre":        "Cúspide",
        "emoji":         "👑",
        "multiplicador": MULTIPLICADOR_CUSPIDE,
        "descripcion":   "Impuesto del 50% (Piraña Suprema)",
        "color":         0x9B59B6,  # Púrpura Imperial
        "min":           TIER_CUSPIDE_MIN
    },
    "elite": {
        "nombre":        "Élite",
        "emoji":         "💎",
        "multiplicador": MULTIPLICADOR_ELITE,
        "descripcion":   "Impuesto del 25%",
        "color":         0xE74C3C,  # Rojo
        "min":           TIER_ELITE_MIN
    },
    "medio": {
        "nombre":        "Clase Media",
        "emoji":         "⚖️",
        "multiplicador": MULTIPLICADOR_MEDIO,
        "descripcion":   "Sin modificaciones (0%)",
        "color":         0xF39C12,  # Naranja
        "min":           TIER_MEDIO_MIN
    },
    "pueblo": {
        "nombre":        "Pueblo",
        "emoji":         "🌱",
        "multiplicador": MULTIPLICADOR_PUEBLO,
        "descripcion":   "Subsidio del +30%",
        "color":         0x2ECC71,  # Verde
        "min":           0
    },
    "neutro": {
        "nombre":        "Sin Registro",
        "emoji":         "❓",
        "multiplicador": MULTIPLICADOR_NEUTRO,
        "descripcion":   "Sin modificador",
        "color":         0x95A5A6,
        "min":           None
    }
}


def _clasificar(user_id: int) -> str:
    """Clasifica al usuario según su balance global (suma de instancias 1-3)."""
    total = balance_global(user_id)

    if total is None:
        return "neutro"
    if total >= TIER_CUSPIDE_MIN:
        return "cuspide"
    if total >= TIER_ELITE_MIN:
        return "elite"
    if total >= TIER_MEDIO_MIN:
        return "medio"
    return "pueblo"


def get_tier_info(user_id: int) -> dict:
    """Devuelve la metadata completa del tier del usuario."""
    return TIERS[_clasificar(user_id)]


def aplicar_impuesto(user_id: int, premio_base: int) -> tuple[int, float]:
    """
    Aplica el multiplicador económico al premio base.
    Devuelve (premio_final, multiplicador_aplicado).
    """
    tier          = get_tier_info(user_id)
    multiplicador = tier["multiplicador"]
    premio_final  = round(premio_base * multiplicador)
    return premio_final, multiplicador