# =========================
# events.py — Catálogo de eventos
# =========================

EVENTOS_SIMPLES = [
    {
        "tipo":   "simple",
        "titulo": "🤠 Aldeano en Apuros",
        "desc": (
            "Un aldeano aparece corriendo, visiblemente nervioso...\n\n"
            "📜 *\"¡Por favor, ayúdenme!\"*\n\n"
            "⚔️ **¿Quién ayudará?**\n"
            "Reacciona con 🐈‍⬛ para intervenir."
        ),
        "color":  0xD2B48C,
        "emoji":  "🐈‍⬛",
        "falla":  "💨 *El aldeano huyó aterrado...*",
        "imagen": "https://imgur.com/G6DnMBJ.gif",
        "min_k":  1000,   
        "max_k":  2500,   
    },
    {
        "tipo":   "simple",
        "titulo": "📦 Cofre Misterioso",
        "desc": (
            "Han encontrado un cofre sellado con runas antiguas.\n"
            "Parece vibrar con energía mágica...\n\n"
            "🗝️ **¿Quién intentará forzar la cerradura?**\n"
            "Reacciona con 🔓 para intentarlo."
        ),
        "color":  0x8B4513,
        "emoji":  "🔓",
        "falla":  "🌑 *Las runas perdieron su brillo y el cofre se hundió en la tierra...*",
        "imagen": "https://imgur.com/vX4VF2o.jpg",
        "min_k":  1000,   
        "max_k":  2500, 
    },
    {
        "tipo":   "simple",
        "titulo": "💰 Mercader Clandestino",
        "desc": (
            "Un mercader encapuchado te hace una seña desde un callejón.\n"
            "Tiene una bolsa pesada.\n\n"
            "🎒 *\"Tengo exceso de equipaje... ¿alguien quiere esto?\"*\n\n"
            "🤝 **¿Quién hará el trato?**\n"
            "Reacciona con 🪙 para acercarte."
        ),
        "color":  0x465473,
        "emoji":  "🪙",
        "falla":  "🥷 *La guardia de la ciudad apareció y el mercader escapó por los tejados...*",
        "imagen": "https://imgur.com/SSMBwCQ.jpg",
        "min_k":  1500,   
        "max_k":  3000, 
    }
]

EVENTO_MAZMORRA = {
    "tipo":   "mazmorra",  # Usa el resolver genérico, la lógica de modos la maneja resolver_incursion
    "titulo": "⚔️ Llamado de la Mazmorra",
    "desc": (
        "Las puertas de una mazmorra olvidada se han abierto...\n"
        "Se escuchan rugidos desde la oscuridad.\n\n"
        "🗡️ **¿Quién responde al llamado?**\n"
        "Reacciona con ⚔️ para unirte a la expedición.\n\n"
        "*(3 aventureros o más activan el **Raid Cooperativo**)*"
    ),
    "color":  0x2C2F33,
    "emoji":  "⚔️",
    "falla":  "🕯️ *Nadie se atrevió a entrar... la mazmorra cerró sus puertas.*",
    "imagen": "https://imgur.com/tJCk9pq.gif"
}

TODOS_LOS_EVENTOS = EVENTOS_SIMPLES + [EVENTO_MAZMORRA]
