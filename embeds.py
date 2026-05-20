# =========================
# embeds.py — Constructores de embeds
# =========================

import discord
from config import FOOTER_TEXT, FOOTER_ICON, EMOJI_KAKERA, ROL_STAFF_ID


def _footer(embed: discord.Embed) -> discord.Embed:
    embed.set_footer(text=FOOTER_TEXT, icon_url=FOOTER_ICON)
    return embed

def _formato_multiplicador(multiplicador: float) -> str:
    """Devuelve una cadena legible del modificador económico."""
    if multiplicador > 1:
        return f"+{round((multiplicador - 1) * 100)}%"
    elif multiplicador < 1:
        return f"-{round((1 - multiplicador) * 100)}%"
    else:
        return "±0%"

def _generar_texto_recibo(premio_base: int, premio_final: int, multiplicador: float) -> str:
    """Genera el texto detallado del cálculo económico."""
    mod_str = _formato_multiplicador(multiplicador)
    if multiplicador == 1.0:
        return f"💎 **A Cobrar:** `{premio_final:,} Kakera` {EMOJI_KAKERA}"
    elif multiplicador > 1.0:
        bono = premio_final - premio_base
        return (f"💎 Base: `{premio_base:,}`\n"
                f"📈 Subsidio ({mod_str}): `+{bono:,}`\n"
                f"💰 **A Cobrar:** `{premio_final:,} Kakera` {EMOJI_KAKERA}")
    else:
        impuesto = premio_base - premio_final
        return (f"💎 Base: `{premio_base:,}`\n"
                f"📉 Impuesto ({mod_str}): `-{impuesto:,}`\n"
                f"💰 **A Cobrar:** `{premio_final:,} Kakera` {EMOJI_KAKERA}")

# =========================
# EMBED DE EVENTO (ANUNCIO)
# =========================

def embed_evento(evento: dict, timestamp: int) -> discord.Embed:
    embed = discord.Embed(
        title=evento["titulo"],
        description=f"{evento['desc']}\n\n⏳ Finaliza <t:{timestamp}:R>",
        color=evento["color"]
    )
    embed.set_image(url=evento["imagen"])
    return _footer(embed)

# =========================
# EMBEDS DE RESULTADO
# =========================

def embed_resultado_incursion(resultados: list, botín_total: int) -> discord.Embed:
    """
    resultados: lista de (member, premio_final, tier_info, multiplicador)
    """
    lines = []
    for jugador, p_base, p_final, tier, mult in resultados:
        mod_str = _formato_multiplicador(mult)
        if mult == 1.0:
            detalle = f"`{p_final:,} KA`"
        else:
            detalle = f"`{p_base:,}` → `{p_final:,} KA` *({mod_str})*"

        lines.append(f"{tier['emoji']} {jugador.mention}: {detalle}")

    desc = (
        f"🛡️ **{len(resultados)} aventureros** saquearon la mazmorra.\n"
        f"💰 Botín total: `{botín_total:,} Kakera` — dividido entre el grupo.\n\n"
        + "\n".join(lines)
    )

    embed = discord.Embed(
        title="🏆 ¡Incursión Completada!",
        description=desc,
        color=0x57F287
    )
    return _footer(embed)


def embed_resultado_duelo(ganador, perdedor, premio_base: int, premio_final: int, tier: dict, multiplicador: float):
    texto_recibo = _generar_texto_recibo(premio_base, premio_final, multiplicador)

    if perdedor:
        desc = (
            f"⚔️ Dos aventureros chocaron espadas...\n\n"
            f"🏆 **{ganador.mention}** venció a {perdedor.mention}\n"
            f"{tier['emoji']} Tier: **{tier['nombre']}**\n\n"
            f"{texto_recibo}"
        )
        titulo = "⚔️ ¡Duelo Resuelto!"
    else:
        desc = (
            f"El destino ha hablado...\n\n"
            f"🎉 **{ganador.mention}** completó el evento.\n"
            f"{tier['emoji']} Tier: **{tier['nombre']}**\n\n"
            f"{texto_recibo}"
        )
        titulo = "✨ ¡Misión Completada!"

    embed = discord.Embed(title=titulo, description=desc, color=tier["color"])
    embed.set_thumbnail(url=ganador.display_avatar.url)
    return _footer(embed)

def embed_resultado_solitario(jugador, premio_base: int, premio_final: int, tier: dict, multiplicador: float) -> discord.Embed:
    texto_recibo = _generar_texto_recibo(premio_base, premio_final, multiplicador)
    
    desc = (
        f"🕯️ **{jugador.mention}** exploró en solitario...\n"
        f"Sobrevivió y regresó con algo de valor.\n\n"
        f"{tier['emoji']} Tier: **{tier['nombre']}**\n\n"
        f"{texto_recibo}"
    )

    embed = discord.Embed(
        title="🗡️ ¡Exploración Completada!",
        description=desc,
        color=tier["color"]
    )
    embed.set_thumbnail(url=jugador.display_avatar.url)
    return _footer(embed)

# =========================
# EMBED DE AYUDA (RPG)
# =========================

def embed_help() -> discord.Embed:
    embed = discord.Embed(
        title="📜 Leyes del Gremio",
        description=(
            "*Bienvenido, aventurero. Aquí aprenderás las reglas del Gremio\n"
            "y cómo funcionan las Incursiones Dinámicas.*"
        ),
        color=0x465473
    )

    embed.add_field(
        name="🤠 Eventos Simples (Aldeano, Cofre, Mercader)",
        value=(
            "Aparecen de forma aleatoria en los canales de juego.\n"
            "• **Mecánica:** Reacciona con el emoji indicado dentro de los 45s.\n"
            "• **Resultado:** Se elige a **un único ganador al azar** entre todos los participantes para llevarse todo el botín."
        ),
        inline=False
    )

    embed.add_field(
        name="⚔️ Eventos de Mazmorra (Incursiones)",
        value=(
            "Son desafíos especiales que requieren cooperación comunitaria.\n"
            "El resultado final **cambia por completo** según cuántos participen:\n\n"
            "🛡️ **3 o más** → Raid Cooperativo *(todos ganan, botín dividido)*\n"
            "⚔️ **2 exactos** → Duelo 1v1 *(combate a muerte, solo el ganador cobra)*\n"
            "🗡️ **1 solo** → Exploración individual *(sobrevives, pero con premio reducido)*"
        ),
        inline=False
    )

    embed.add_field(
        name="⚖️ Sistema de Impuestos del Gremio",
        value=(
            "El Gremio aplica modificadores según tu riqueza total en Kakera:\n\n"
            "👑 **Cúspide** (>200k) → Impuesto del **50%** *(×0.50)*\n"
            "💎 **Élite** (60k–200k) → Impuesto del **25%** *(×0.75)*\n"
            "⚖️ **Clase Media** (25k–60k) → Mercado Libre *(×1.00)*\n"
            "🌱 **Pueblo** (<25k) → Subsidio del **+30%** *(×1.30)*"
        ),
        inline=False
    )

    embed.add_field(
        name="🔧 Comandos",
        value=(
            "`mu!help` → Este menú\n"
            "`mu!balance [@usuario]` → Consulta tu tier económico\n"
            "`mu!spawn` → *(Staff)* Invoca un evento manual\n"
            "`mu!spawn simple | mazmorra` → *(Staff)* Elige el tipo\n"
            "`mu!setinstancia <i1|i2|i3>` → *(Staff)* Carga masiva del Ladder\n"
            "`mu!setbalance @usuario <i1|i2|i3> <cantidad>` → *(Staff)* Ajuste manual"
        ),
        inline=False
    )

    return _footer(embed)
