# =========================
# config.py — Configuración central del bot
# =========================

import os
from dotenv import load_dotenv

load_dotenv()

DEV_MODE = os.getenv("ENV") == "dev"

# =========================
# CANALES
# =========================

CANALES_EVENTOS = (
    [
        919819565414903808,
        920686951546355764,
        1506727323179942039   
    ]
    if DEV_MODE else
    [
        884137988114767882,
        884135395342819348,
        956318972221984779
    ]
)

# =========================
# ROLES
# =========================

ROL_AVISO_ID = (
    980103356875948102         
    if DEV_MODE else
    821974903896539156
)

ROL_STAFF_ID = (
    778414374296617041         
    if DEV_MODE else
    861651001303629856
)

# =========================
# TIEMPOS DE ESPERA (REDUCIDOS)
# =========================
TIEMPO_MIN = 10    if DEV_MODE else 5400   # dev: 10s  | prod: 1.5 horas
TIEMPO_MAX = 20    if DEV_MODE else 10800  # dev: 20s  | prod: 3.0 horas

# =========================
# ESTÉTICA
# =========================

FOOTER_TEXT  = "Copyright (©) Casino Club"
FOOTER_ICON  = "https://i.imgur.com/ytopJtE.gif"
EMOJI_KAKERA = "<:ka_amarillo:1506025670734516406>"

# =========================
# PREMIOS POR MODO
# =========================

INCURSION_MIN_K = 3000   # Cooperativa (3+ jugadores) — botín total
INCURSION_MAX_K = 8000

DUELO_MIN_K     = 1500   # Duelo 1v1 — premio para el ganador
DUELO_MAX_K     = 2500

SOLO_MIN_K      = 600    # Solitario — premio reducido
SOLO_MAX_K      = 1200

# =========================
# SISTEMA ANTI-MONOPOLIO (4 TIERS)
# =========================
TIER_CUSPIDE_MIN = 200_000  # > 200k global → Los dueños del server
TIER_ELITE_MIN   =  60_000  # 60k–200k → Farmeadores fuertes
TIER_MEDIO_MIN   =  25_000  # 25k–60k → Jugador activo promedio
                             # < 25k → Pueblo / Recién llegados

MULTIPLICADOR_CUSPIDE = 0.50  # -50% impuesto aduanero
MULTIPLICADOR_ELITE   = 0.75  # -25% impuesto de control
MULTIPLICADOR_MEDIO   = 1.00  # Libre comercio (0% cambios)
MULTIPLICADOR_PUEBLO  = 1.30  # +30% de subsidio de apoyo
MULTIPLICADOR_NEUTRO  = 1.00
