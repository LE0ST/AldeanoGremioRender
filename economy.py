# =========================
# economy.py — Sistema Anti-Monopolio Adaptativo
# =========================

from config import (
    TIER_CUSPIDE_MIN, TIER_ELITE_MIN, TIER_MEDIO_MIN,
    MULTIPLICADOR_CUSPIDE, MULTIPLICADOR_ELITE, MULTIPLICADOR_MEDIO,
    MULTIPLICADOR_PUEBLO, MULTIPLICADOR_NEUTRO
)
from balance import balance_global, balance_por_instancia

TIERS = {
    "cuspide": {
        "nombre":        "Cúspide",
        "emoji":         "👑",
        "multiplicador": MULTIPLICADOR_CUSPIDE,
        "descripcion":   "Tasa Aduanera del 35%",
        "color":         0x9B59B6,  # Púrpura Imperial
        "min":           TIER_CUSPIDE_MIN
    },
    "elite": {
        "nombre":        "Élite",
        "emoji":         "💎",
        "multiplicador": MULTIPLICADOR_ELITE,
        "descripcion":   "Impuesto de Operación del 15%",
        "color":         0xE74C3C,  # Rojo
        "min":           TIER_ELITE_MIN
    },
    "medio": {
        "nombre":        "Clase Media",
        "emoji":         "⚖️",
        "multiplicador": MULTIPLICADOR_MEDIO,
        "descripcion":   "Licencia de Libre Comercio (0%)",
        "color":         0xF39C12,  # Naranja
        "min":           TIER_MEDIO_MIN
    },
    "pueblo": {
        "nombre":        "Pueblo",
        "emoji":         "🌱",
        "multiplicador": MULTIPLICADOR_PUEBLO,
        "descripcion":   "Incentivo de Desarrollo (+15%)",
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
    """Clasifica al usuario según su balance global centralizado."""
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


def aplicar_impuesto_adaptativo(user_id: int, premio_base: int, instancia_actual: str) -> tuple[int, float]:
    """
    Aplica el multiplicador económico mitigando el impacto si el usuario
    es rico a nivel global pero se encuentra en una instancia nueva en desarrollo.
    """
    tier_key = _clasificar(user_id)
    tier = TIERS[tier_key]
    multiplicador = tier["multiplicador"]

    # ALGORITMO DE ATENUACIÓN: Si es Cúspide o Élite global, pero en ESTA instancia
    # tiene menos de 15,000 Kakeras (Clase Media Mínima), reducimos el impuesto a la mitad.
    if tier_key in ("cuspide", "elite"):
        desglose_local = balance_por_instancia(user_id)
        balance_local = desglose_local.get(instancia_actual, 0)
        
        if balance_local < TIER_MEDIO_MIN:
            impuesto_original = 1.0 - multiplicador
            impuesto_mitigado = impuesto_original / 2
            multiplicador = round(1.0 - impuesto_mitigado, 2)

    premio_final = round(premio_base * multiplicador)
    return premio_final, multiplicador