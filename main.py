import discord
from discord.ext import commands
import asyncio
import random
import time
import logging
import os
from threading import Thread
from flask import Flask
from dotenv import load_dotenv 

load_dotenv() # Esto carga las variables del archivo .env

# =========================
# SERVIDOR WEB (KEEP ALIVE)
# =========================
app = Flask('')

@app.route('/')
def home():
    return "Mercader del Gremio Online"

def run():
    # Usamos el puerto que la mayoría de plataformas gratuitas asignan por defecto
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# =========================
# CONFIGURACIÓN DEL BOT
# =========================
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix="mu!", intents=intents)

# Evita que el sistema de eventos se inicie varias veces
eventos_iniciados = False

# =========================
# CONFIGURACIÓN GENERAL
# =========================

# Canales donde aparecerán eventos aleatoriamente
# Canales de prueba (ajustar a producción quitando los canales de prueba)
# CANALES_EVENTOS = [
#    1494443971550642337,
#    1494444543024693461,
#    1494444701653139706,
#    1494444792493506710
#]

# En producción, usar solo los canales reales y eliminar los de prueba
CANALES_EVENTOS = [
    884137988114767882,
    884135395342819348,
    956318972221984779,
    815023234721251418
]

# Rol para avisar que apareció un evento
ROL_AVISO_ID = 821974903896539156

# Rol del staff que entrega recompensas
ROL_STAFF_ID = 861651001303629856

# =========================
# SISTEMA DE EVENTOS
# =========================

EVENTOS = [
    {
        "titulo": "🤠 Aldeano en Apuros",
        "desc": (
            "Un aldeano aparece corriendo, visiblemente nervioso...\n\n"
            "📜 *\"¡Por favor, ayúdenme!\"*\n\n"
            "⚔️ **¿Quién ayudará?**\n"
            "Reacciona con 🐈‍⬛ para intervenir."
        ),
        "color": 0xD2B48C,
        "emoji": "🐈‍⬛",
        "min_k": 1000,
        "max_k": 2500,
        "falla": "💨 *El aldeano huyó aterrado...*",
        "imagen": "https://imgur.com/G6DnMBJ.gif"
    },

    {
        "titulo": "📦 Cofre Misterioso",
        "desc": (
            "Han encontrado un cofre sellado con runas antiguas.\n"
            "Parece vibrar con energía mágica...\n\n"
            "🗝️ **¿Quién intentará forzar la cerradura?**\n"
            "Reacciona con 🔓 para intentarlo."
        ),
        "color": 0x8B4513,
        "emoji": "🔓",
        "min_k": 1500,
        "max_k": 3500,
        "falla": "🌑 *Las runas perdieron su brillo y el cofre se hundió en la tierra...*",
        "imagen": "https://imgur.com/vX4VF2o.jpg"
    },

    {
        "titulo": "💰 Mercader Clandestino",
        "desc": (
            "Un mercader encapuchado te hace una seña desde un callejón.\n"
            "Tiene una bolsa pesada.\n\n"
            "🎒 *\"Tengo exceso de equipaje... ¿alguien quiere esto?\"*\n\n"
            "🤝 **¿Quién hará el trato?**\n"
            "Reacciona con 🪙 para acercarte."
        ),
        "color": 0x465473,
        "emoji": "🪙",
        "min_k": 2000,
        "max_k": 5000,
        "falla": "🥷 *La guardia de la ciudad apareció y el mercader escapó por los tejados...*",
        "imagen": "https://imgur.com/SSMBwCQ.jpg"
    }
]

# =========================
# SISTEMA AUTOMÁTICO
# =========================

async def sistema_eventos():
    await bot.wait_until_ready()
    logging.info("✅ Sistema de eventos iniciado")

    while not bot.is_closed():
        try: # 🟢 INICIO DEL ESCUDO

            # =========================
            # TIEMPO ALEATORIO
            # =========================

            # =========================
            # MODO PRUEBA
            # =========================

            # Entre 10 y 20 segundos
            # tiempo_espera = random.randint(10, 20)

            # =========================
            # PRODUCCIÓN
            # =========================

            # Entre 4 y 8 horas
            tiempo_espera = random.randint(10800, 21600)

            if tiempo_espera < 3600:
                logging.info(f"⏳ Próximo evento en {tiempo_espera} segundos")
            else:
                horas = round(tiempo_espera / 3600, 2)
                logging.info(f"⏳ Próximo evento en {horas} horas")

            await asyncio.sleep(tiempo_espera)

            # =========================
            # CANAL ALEATORIO
            # =========================

            canal_id = random.choice(CANALES_EVENTOS)
            canal = bot.get_channel(canal_id)

            if not canal:
                try:
                    canal = await bot.fetch_channel(canal_id)
                except:
                    logging.error(f"❌ No se pudo obtener el canal {canal_id}")
                    continue

            # =========================
            # EVENTO ALEATORIO
            # =========================

            evento = random.choice(EVENTOS)
            timestamp = int(time.time()) + 47
            
            embed = discord.Embed(
                title=evento["titulo"],
                description=f"{evento['desc']}\n\n⏳ Finaliza <t:{timestamp}:R>",
                color=evento["color"]
            )
            embed.set_image(url=evento["imagen"])
            embed.set_footer(
                text="Copyright (©) Casino Club",
                icon_url="https://i.imgur.com/ytopJtE.gif"
            )

            # =========================
            # ENVÍO DEL EVENTO
            # =========================

            mensaje = await canal.send(
                content=f"<@&{ROL_AVISO_ID}>",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(
                    roles=True
                )
            )

            await mensaje.add_reaction(evento["emoji"])

            logging.info(f"📨 Evento enviado en #{canal.name}")

            # =========================
            # TIEMPO DE REACCIÓN
            # =========================

            await asyncio.sleep(45)

            mensaje = await canal.fetch_message(mensaje.id)

            participantes = set()

            for reaction in mensaje.reactions:

                if str(reaction.emoji) == evento["emoji"]:

                    async for user in reaction.users():

                        if not user.bot:
                            participantes.add(user)

            # =========================
            # RESULTADO
            # =========================

            if participantes:

                ganador = random.choice(list(participantes))

                premio_kakera = random.randint(
                    evento["min_k"],
                    evento["max_k"]
                )

                embed_resultado = discord.Embed(
                    title="✨ ¡Misión Completada!",
                    description=(
                        "El destino ha hablado...\n\n"
                        f"🎉 **{ganador.mention}** completó el evento.\n"
                        f"💎 Recompensa: "
                        f"`{premio_kakera} Kakera` "
                        "<:ka_amarillo:1506025670734516406>"
                    ),
                    color=0xF1C40F
                )

                embed_resultado.set_thumbnail(
                    url=ganador.display_avatar.url
                )

                embed_resultado.set_footer(
                    text="Copyright (©) Casino Club",
                    icon_url="https://i.imgur.com/ytopJtE.gif"
                )

                await canal.send(
                    content=f"<@&{ROL_STAFF_ID}>",
                    embed=embed_resultado,
                    allowed_mentions=discord.AllowedMentions(
                        roles=True
                    )
                )

                logging.info(f"🏆 Ganador: {ganador}")

            else:

                await canal.send(evento["falla"])

                logging.warning("❌ Nadie participó")
        
        except discord.Forbidden:
            logging.error("❌ El bot no tiene permisos")

        except discord.HTTPException as e:
            logging.error(f"⚠️ Error HTTP de Discord: {e}")

        except Exception as e: # 🔴 QUÉ HACER SI HAY UN ERROR
            logging.error(f"⚠️ Error en el bucle de eventos: {e}")
            # Hacemos una pequeña pausa de 10 segundos antes de reintentar
            await asyncio.sleep(10)
        

# =========================
# BOT READY
# =========================

@bot.event
async def on_ready():
    global eventos_iniciados
    logging.info(f"✅ Bot conectado como {bot.user}")

    # Evita iniciar múltiples loops
    if not eventos_iniciados:
        bot.loop.create_task(sistema_eventos())
        eventos_iniciados = True
    
# =========================
# INICIAR BOT
# =========================
# Creamos el hilo de Flask como "daemon" para que se cierre limpiamente si el bot se detiene
t = Thread(target=run)
t.daemon = True
t.start()

# Ejecución única y correcta
bot.run(os.getenv("TOKEN"))