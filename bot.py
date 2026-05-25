import discord
from discord.ext import commands
import asyncio
import random
import time
import logging
import os
import re
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
from typing import Optional

from config  import (
    CANALES_EVENTOS, ROL_AVISO_ID, ROL_STAFF_ID,
    FOOTER_TEXT, FOOTER_ICON, EMOJI_KAKERA,
    INCURSION_MIN_K, INCURSION_MAX_K,
    DUELO_MIN_K, DUELO_MAX_K,
    SOLO_MIN_K, SOLO_MAX_K,
    TIEMPO_MIN, TIEMPO_MAX,
    DEV_MODE
)
from economy import aplicar_impuesto_adaptativo, get_tier_info
from events  import TODOS_LOS_EVENTOS, EVENTOS_SIMPLES, EVENTO_MAZMORRA
from embeds  import (
    embed_evento,
    embed_resultado_incursion,
    embed_resultado_duelo,
    embed_resultado_solitario,
    embed_help,
    _footer
)
from balance import (
    cargar_balances, guardar_balances, balances,
    balance_global, balance_por_instancia, set_balance_instancia,
    INSTANCIAS
)

# =========================
# KEEP ALIVE
# =========================
app = Flask('')

@app.route('/')
def home():
    return "Mercader del Gremio Online"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# =========================
# BOT
# =========================
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="mu!", intents=intents)
bot.remove_command("help")  # Removemos el help por defecto de discord.py

eventos_iniciados = False

# =========================
# HELPERS
# =========================

# Mapeador estricto para detectar en qué entorno se ejecutó el evento automático
MAPA_CANAL_A_INSTANCIA = (
    {
        919819565414903808: "i1",
        920686951546355764: "i2",
        1506727323179942039: "i3"
    }
    if DEV_MODE else
    {
        884137988114767882: "i1",
        884135395342819348: "i2",
        956318972221984779: "i3"
    }
)

def obtener_codigo_instancia(canal_id: int) -> str:
    """Devuelve 'i1', 'i2' o 'i3' según el canal, defaltea a 'i1' si es manual."""
    return MAPA_CANAL_A_INSTANCIA.get(canal_id, "i1")


async def obtener_canal(canal_id: int) -> discord.TextChannel | None:
    canal = bot.get_channel(canal_id)
    if not canal:
        try:
            canal = await bot.fetch_channel(canal_id)
        except Exception:
            logging.error(f"❌ No se pudo obtener el canal {canal_id}")
            return None

    if isinstance(canal, discord.TextChannel):
        return canal

    logging.error(f"❌ El canal {canal_id} no es un canal de texto")
    return None


async def recoger_participantes(mensaje: discord.Message, emoji: str) -> list:
    participantes = []
    for reaction in mensaje.reactions:
        if str(reaction.emoji) == emoji:
            async for user in reaction.users():
                if not user.bot:
                    participantes.append(user)

    return participantes

# =========================
# RESOLUCIÓN DE INCURSIONES
# =========================

async def resolver_simple(canal: discord.TextChannel, participantes: list, evento: dict):
    if not participantes:
        await canal.send(evento["falla"])
        return

    instancia = obtener_codigo_instancia(canal.id)
    ganador     = random.choice(participantes)
    premio_base = random.randint(evento["min_k"], evento["max_k"])
    
    # Inyectamos la instancia para el cálculo atenuado
    premio_final, multiplicador = aplicar_impuesto_adaptativo(ganador.id, premio_base, instancia)
    tier        = get_tier_info(ganador.id)

    embed = embed_resultado_duelo(ganador, None, premio_base, premio_final, tier, multiplicador)
    await canal.send(
        content=f"<@&{ROL_STAFF_ID}>",
        embed=embed,
        allowed_mentions=discord.AllowedMentions(roles=True)
    )
    logging.info(f"🏆 Ganador Simple: {ganador} — Instancia: {instancia.upper()} — Base: {premio_base} | Final: {premio_final}")

async def resolver_incursion(canal: discord.TextChannel, participantes: list, evento: dict):
    n = len(participantes)
    instancia = obtener_codigo_instancia(canal.id)

    if n == 0:
        await canal.send(evento["falla"])
        return

    # --- Modo Incursión Cooperativa (3+) ---
    if n >= 3:
        botín_total = random.randint(INCURSION_MIN_K, INCURSION_MAX_K)
        premio_base = botín_total // n

        resultados_temporales = []
        suma_premios_finales = 0

        # Paso 1: Procesamiento y cálculo adaptativo individual
        for jugador in participantes:
            premio_final, multiplicador = aplicar_impuesto_adaptativo(jugador.id, premio_base, instancia)
            tier = get_tier_info(jugador.id)
            resultados_temporales.append([jugador, premio_base, premio_final, tier, multiplicador])
            suma_premios_finales += premio_final

        # Paso 2: Blindaje Deficitario (Anti-Inflación de Raids)
        # Si la inyección global es superior al botín total configurado debido a los subsidios,
        # comprimimos proporcionalmente para cuidar el dinero inorgánico.
        if suma_premios_finales > botín_total:
            factor_reduccion = botín_total / suma_premios_finales
            for res in resultados_temporales:
                res[2] = round(res[2] * factor_reduccion)

        # Reestructuramos a tu formato original de tuplas para mantener compatibilidad con embeds.py
        resultados_finales = [(r[0], r[1], r[2], r[3], r[4]) for r in resultados_temporales]

        embed = embed_resultado_incursion(resultados_finales, botín_total)
        await canal.send(
            content=f"<@&{ROL_STAFF_ID}>",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        logging.info(f"🛡️ Raid Balanceado en {instancia.upper()} — {n} jugadores — Botín Real: {botín_total}")

    # --- Modo Duelo Competitivo (2) ---
    elif n == 2:
        ganador  = random.choice(participantes)
        perdedor = next(u for u in participantes if u != ganador)

        premio_base = random.randint(DUELO_MIN_K, DUELO_MAX_K)
        premio_final, multiplicador = aplicar_impuesto_adaptativo(ganador.id, premio_base, instancia)
        tier = get_tier_info(ganador.id)

        embed = embed_resultado_duelo(ganador, perdedor, premio_base, premio_final, tier, multiplicador)
        await canal.send(
            content=f"<@&{ROL_STAFF_ID}>",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        logging.info(f"⚔️ Duelo en {instancia.upper()} — Ganador: {ganador} — Base: {premio_base} | Final: {premio_final}")

    # --- Modo Solitario (1) ---
    else:
        jugador = participantes[0]
        premio_base = random.randint(SOLO_MIN_K, SOLO_MAX_K)
        premio_final, multiplicador = aplicar_impuesto_adaptativo(jugador.id, premio_base, instancia)
        tier = get_tier_info(jugador.id)

        embed = embed_resultado_solitario(jugador, premio_base, premio_final, tier, multiplicador)
        await canal.send(
            content=f"<@&{ROL_STAFF_ID}>",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        logging.info(f"🗡️ Solitario en {instancia.upper()} — {jugador} — Base: {premio_base} | Final: {premio_final}")

# =========================
# LANZADOR CENTRAL
# =========================

async def lanzar_evento(canal: discord.TextChannel, evento: dict | None = None):
    """Orquesta el ciclo completo de un evento en el canal dado."""
    if evento is None:
        evento = random.choice(TODOS_LOS_EVENTOS)

    timestamp = int(time.time()) + 47
    embed     = embed_evento(evento, timestamp)

    mensaje = await canal.send(
        content=f"<@&{ROL_AVISO_ID}>",
        embed=embed,
        allowed_mentions=discord.AllowedMentions(roles=True)
    )
    await mensaje.add_reaction(evento["emoji"])
    logging.info(f"📨 Evento '{evento['titulo']}' en #{canal.name}")

    tiempo_restante = timestamp - int(time.time())
    await asyncio.sleep(max(tiempo_restante, 0))

    try:
        mensaje = await canal.fetch_message(mensaje.id)
    except discord.NotFound:
        logging.warning("⚠️ Mensaje eliminado antes de resolverse")
        return

    participantes = await recoger_participantes(mensaje, evento["emoji"])
    
    if evento["tipo"] == "mazmorra":
        await resolver_incursion(canal, participantes, evento)
    else:
        await resolver_simple(canal, participantes, evento)

# =========================
# LOOP AUTOMÁTICO
# =========================

async def sistema_eventos():
    await bot.wait_until_ready()
    logging.info("✅ Sistema de eventos iniciado")

    while not bot.is_closed():
        try:
            tiempo_espera = random.randint(TIEMPO_MIN, TIEMPO_MAX)
            if DEV_MODE:
                logging.info(f"⏳ [DEV] Próximo evento en {tiempo_espera} segundos")
            else:
                logging.info(f"⏳ Próximo evento en {round(tiempo_espera / 3600, 2)} horas")
            await asyncio.sleep(tiempo_espera)

            canal_id = random.choice(CANALES_EVENTOS)
            canal    = await obtener_canal(canal_id)
            if canal:
                await lanzar_evento(canal)

        except discord.Forbidden:
            logging.error("❌ Sin permisos en ese canal")
        except discord.HTTPException as e:
            logging.error(f"⚠️ Error HTTP: {e}")
        except Exception as e:
            logging.error(f"⚠️ Error en el loop: {e}")
            await asyncio.sleep(10)

# =========================
# COMANDOS
# =========================

@bot.command(name="spawn")
@commands.has_role(ROL_STAFF_ID)
async def spawn(ctx, tipo: Optional[str] = None):
    """
    Invoca un evento manualmente sin alterar el reloj automático.
    Uso:
      mu!spawn              → evento aleatorio
      mu!spawn simple       → evento simple aleatorio
      mu!spawn mazmorra     → evento de mazmorra
    """
    await ctx.message.delete()

    if tipo == "mazmorra":
        evento = EVENTO_MAZMORRA
    elif tipo == "simple":
        evento = random.choice(EVENTOS_SIMPLES)
    else:
        evento = random.choice(TODOS_LOS_EVENTOS)

    await lanzar_evento(ctx.channel, evento)

@bot.command(name="setinstancia")
@commands.has_role(ROL_STAFF_ID)
async def set_instancia(ctx, instancia: str):
    """
    Carga todos los balances de una instancia pegando el output de Mudae.
    Uso: mu!setinstancia i1
    (luego pegás la lista de Mudae en el mismo mensaje, en líneas separadas)
    Formato esperado por línea:
    username (user_id) - kakera_actual / kakera_total
    """
    if instancia not in INSTANCIAS:
        await ctx.send(f"⚠️ Instancia inválida. Usa `i1`, `i2` o `i3`.", delete_after=8)
        return

    # Extraemos el contenido después del comando
    contenido = ctx.message.content
    lineas = contenido.split("\n")[1:]  # Saltamos la primera línea (el comando)

    if not lineas:
        await ctx.send(
            f"⚠️ No se encontraron datos. Pega la lista de Mudae debajo del comando.\n"
            f"Ejemplo:\n```mu!setinstancia i1\n pochonclo (333102198328131595) - 37.557 / 144.807```",
            delete_after=15
        )
        return

    # Regex: captura (user_id) y el kakera TOTAL (segundo número)
    patron = re.compile(r'\((\d+)\).*?/\s*([\d.]+)')
    registrados = []
    errores = []

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue

        match = patron.search(linea)
        if not match:
            errores.append(f"❌ No se pudo parsear: `{linea[:50]}`")
            continue

        user_id = int(match.group(1))
        # Los puntos son separadores de miles en el output de Mudae
        kakera = int(match.group(2).replace(".", ""))

        set_balance_instancia(user_id, instancia, kakera)
        tier = get_tier_info(user_id)

        # Intentamos obtener el nombre del usuario desde Discord
        miembro = ctx.guild.get_member(user_id)
        nombre = miembro.display_name if miembro else str(user_id)

        registrados.append(f"{tier['emoji']} **{nombre}** → `{kakera:,}` {instancia.upper()}")

    # Embed de resultado
    embed = discord.Embed(
        title=f"💾 Instancia {instancia.upper()} actualizada",
        color=0x465473
    )

    if registrados:
        # Dividimos si hay más de 25 usuarios (límite de fields en Discord) o el string es muy largo
        # Para tu lista actual de 26, lo metemos todo en el Description o dividimos en chunks si excede 1024 caracteres
        chunks = [registrados[x:x+15] for x in range(0, len(registrados), 15)]
        for i, chunk in enumerate(chunks):
            embed.add_field(
                name=f"✅ Usuarios Registrados (Parte {i+1})" if i == 0 else "\u200b",
                value="\n".join(chunk),
                inline=False
            )

    if errores:
        embed.add_field(
            name=f"⚠️ {len(errores)} líneas no parseadas",
            value="\n".join(errores),
            inline=False
        )

    _footer(embed) # <--- Llamamos a tu función _footer
    await ctx.send(embed=embed)
    logging.info(f"💾 Instancia {instancia} — {len(registrados)} usuarios cargados")

@bot.command(name="setbalance")
@commands.has_role(ROL_STAFF_ID)
async def set_balance(ctx, miembro: discord.Member, instancia: str, cantidad: int):
    """
    Actualiza el balance de una instancia específica de un usuario.
    Uso: mu!setbalance @usuario <i1|i2|i3> <cantidad>
    Ejemplo: mu!setbalance @pochonclo i1 144577
    """
    if instancia not in INSTANCIAS:
        await ctx.send(
            f"⚠️ Instancia inválida. Usá `i1`, `i2` o `i3`.",
        )
        return

    set_balance_instancia(miembro.id, instancia, cantidad)

    total = balance_global(miembro.id)
    tier  = get_tier_info(miembro.id)
    desglose = balance_por_instancia(miembro.id)

    await ctx.send(
        f"✅ **{miembro.display_name}** — {instancia.upper()} actualizada a `{cantidad:,} Kakera`\n"
        f"📊 Global: `{total:,}` "
        f"(I1: {desglose['i1']:,} · I2: {desglose['i2']:,} · I3: {desglose['i3']:,})\n"
        f"Tier: {tier['emoji']} **{tier['nombre']}** (×{tier['multiplicador']})",
    )
    logging.info(f"💾 {miembro} → {instancia}={cantidad:,} | global={total:,}")


@bot.command(name="balance")
async def ver_balance(ctx, miembro: Optional[discord.Member] = None):
    """
    Muestra el balance por instancia y tier económico de un usuario.
    Uso: mu!balance [@usuario]
    """
    objetivo = miembro or ctx.author
    total    = balance_global(objetivo.id)

    if total is None:
        await ctx.send(
            f"⚠️ **{objetivo.display_name}** no tiene balance registrado. "
            f"Un Staff puede usar `mu!setbalance @usuario <i1|i2|i3> <cantidad>`.",
        )
        return

    tier     = get_tier_info(objetivo.id)
    desglose = balance_por_instancia(objetivo.id)

    await ctx.send(
        f"🏦 **{objetivo.display_name}**\n"
        f"I1: `{desglose['i1']:,}` · I2: `{desglose['i2']:,}` · I3: `{desglose['i3']:,}`\n"
        f"📊 Global: `{total:,} Kakera`\n"
        f"Tier: {tier['emoji']} **{tier['nombre']}** — {tier['descripcion']} (×{tier['multiplicador']})",
    )


@bot.command(name="help")
async def ayuda(ctx):
    """Muestra el menú de ayuda con estética RPG."""
    await ctx.send(embed=embed_help())


# =========================
# ON READY
# =========================

@bot.event
async def on_ready():
    global eventos_iniciados
    logging.info(f"✅ Bot conectado como {bot.user}")
    if not eventos_iniciados:
        bot.loop.create_task(sistema_eventos())
        eventos_iniciados = True

# =========================
# INICIO
# =========================

cargar_balances()

t = Thread(target=run)
t.daemon = True
t.start()

token = os.getenv("TOKEN")
if token is None:
    raise RuntimeError("Environment variable TOKEN is required")

bot.run(token)
