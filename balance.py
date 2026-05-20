# =========================
# balance.py — Persistencia de balances por instancia
# =========================

import json
import logging
import os

BALANCE_FILE = "kakera_balances.json"

# Estructura: { "user_id_str": { "i1": int, "i2": int, "i3": int } }
balances: dict[str, dict[str, int]] = {}

INSTANCIAS = ("i1", "i2", "i3")


def cargar_balances():
    """Carga los balances desde el archivo JSON al iniciar el bot."""
    global balances
    if os.path.exists(BALANCE_FILE):
        try:
            with open(BALANCE_FILE, "r") as f:
                balances = json.load(f)
            logging.info(f"💾 Balances cargados: {len(balances)} usuarios registrados")
        except Exception as e:
            logging.error(f"⚠️ Error al cargar balances: {e}")
            balances = {}
    else:
        logging.info("💾 No se encontró archivo de balances, empezando vacío")
        balances = {}


def guardar_balances():
    """Persiste el dict de balances en el archivo JSON."""
    try:
        with open(BALANCE_FILE, "w") as f:
            json.dump(balances, f, indent=2)
        logging.info("💾 Balances guardados correctamente")
    except Exception as e:
        logging.error(f"⚠️ Error al guardar balances: {e}")


def balance_global(user_id: int) -> int | None:
    """
    Suma los balances de todas las instancias registradas para un usuario.
    Devuelve None si el usuario no tiene ningún dato registrado.
    """
    datos = balances.get(str(user_id))
    if datos is None:
        return None
    return sum(datos.get(inst, 0) for inst in INSTANCIAS)


def balance_por_instancia(user_id: int) -> dict[str, int]:
    """
    Devuelve el desglose por instancia de un usuario.
    Instancias sin dato aparecen como 0.
    """
    datos = balances.get(str(user_id), {})
    return {inst: datos.get(inst, 0) for inst in INSTANCIAS}


def set_balance_instancia(user_id: int, instancia: str, cantidad: int):
    """
    Actualiza el balance de una instancia específica para un usuario.
    Crea la entrada si no existe.
    """
    uid = str(user_id)
    if uid not in balances:
        balances[uid] = {}
    balances[uid][instancia] = cantidad
    guardar_balances()
