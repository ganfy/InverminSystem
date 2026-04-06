"""
=============================================================
  INVERMIN PAITITI S.A.C. - Agente Local de Balanza
  Versión: 1.0

  Instalación (una sola vez):
      pip install pyserial websockets python-dotenv

  Ejecución:
      python balanza_agent.py

  Configuración: archivo .env en la misma carpeta.
  El agente arranca al encender la PC (ver README_INSTALACION.txt).
=============================================================
"""

import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path

import serial
import serial.tools.list_ports
import websockets
from dotenv import load_dotenv

# ── Configuración ─────────────────────────────────────────
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

COM_PORT = os.getenv("BALANZA_COM_PORT", "COM3")
BAUD_RATE = int(os.getenv("BALANZA_BAUD_RATE", "9600"))
BYTE_SIZE = int(os.getenv("BALANZA_BYTE_SIZE", "8"))
PARITY = os.getenv("BALANZA_PARITY", "N")
STOP_BITS = int(os.getenv("BALANZA_STOP_BITS", "1"))
DECIMAL_PLACES = int(os.getenv("BALANZA_DECIMAL_PLACES", "3"))
WS_HOST = os.getenv("BALANZA_WS_HOST", "localhost")
WS_PORT = int(os.getenv("BALANZA_WS_PORT", "8765"))
RECONNECT_DELAY_SEC = int(os.getenv("BALANZA_RECONNECT_SEC", "3"))
STABILITY_THRESHOLD = float(os.getenv("BALANZA_STABILITY_THRESHOLD", "0.005"))
# ──────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "balanza_agent.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("balanza")

# Estado compartido entre el hilo serial y los clientes WS
state: dict = {
    "peso_raw": None,  # float, kg
    "peso_display": None,  # str, ej: "12.500"
    "unidad": "KG",
    "estable": False,
    "conectado_serial": False,
    "ultimo_cambio": None,
    "error": None,
}

# Set de clientes WebSocket conectados
clientes: set = set()

# ── Parser de trama ────────────────────────────────────────
# Trama detectada: STX(02) SP [7 dígitos] "KG" SP CR LF
# Ejemplo hex: 02 20 30 30 31 32 35 30 30 4b 47 20 0d 0a
#              STX SP  0  0  1  2  5  0  0  K  G  SP CR LF
#
# También soporta formatos comunes de otras balanzas:
#   "ST,GS,  +  12.500 kg\r\n"  (Mettler Toledo)
#   "  12500 KG\r\n"             (sin STX)
# ──────────────────────────────────────────────────────────

# Patrón 1: trama con STX (la detectada en el diagnóstico)
PATTERN_STX = re.compile(rb"\x02\s*([\d]{5,9})\s*KG\s*", re.IGNORECASE)
# Patrón 2: Mettler Toledo / Ohaus texto plano
PATTERN_PLAIN = re.compile(rb"[+\-]?\s*([\d]+[.,]?[\d]*)\s*KG?", re.IGNORECASE)


def parse_trama(raw_bytes: bytes) -> tuple[float | None, bool]:
    """
    Devuelve (peso_kg: float | None, estable: bool).
    `estable` es True cuando la trama confirma lectura fija
    (prefijo ST en Mettler, o lectura repetida en protocolo Paititi).
    """
    # Intentar patrón STX (protocolo propio de la balanza detectada)
    m = PATTERN_STX.search(raw_bytes)
    if m:
        digits = m.group(1).decode("ascii")
        # Los 7 dígitos enteros se convierten usando DECIMAL_PLACES
        # Ejemplo: DECIMAL_PLACES=3 → "0012500" → 12.500 KG
        entero = int(digits)
        peso = entero / (10**DECIMAL_PLACES)
        return peso, True  # este protocolo no tiene flag de estabilidad explícito

    # Fallback: patrón texto plano (Mettler Toledo, Ohaus, genérico)
    m = PATTERN_PLAIN.search(raw_bytes)
    if m:
        num_str = m.group(1).decode("ascii").replace(",", ".")
        try:
            peso = float(num_str)
        except ValueError:
            return None, False
        # "ST," al inicio indica estable en Mettler
        estable = b"ST," in raw_bytes
        return peso, estable

    return None, False


def formatear_peso(peso_kg: float) -> str:
    return f"{peso_kg:.{DECIMAL_PLACES}f}"


# ── Hilo de lectura serial (sync, en thread separado) ──────


def leer_serial(loop: asyncio.AbstractEventLoop):
    """
    Corre en un thread daemon. Lee bytes del puerto serial,
    parsea la trama y actualiza `state`. Broadcast asíncrono
    se dispara vía loop.call_soon_threadsafe.
    """
    log.info(f"Iniciando lectura serial en {COM_PORT} @ {BAUD_RATE}-{BYTE_SIZE}{PARITY}{STOP_BITS}")

    peso_anterior: float | None = None

    while True:
        try:
            with serial.Serial(
                port=COM_PORT,
                baudrate=BAUD_RATE,
                bytesize=BYTE_SIZE,
                parity=PARITY,
                stopbits=STOP_BITS,
                timeout=2,
            ) as ser:
                state["conectado_serial"] = True
                state["error"] = None
                log.info(f"Puerto {COM_PORT} abierto correctamente.")

                while True:
                    linea = ser.readline()
                    if not linea:
                        continue

                    peso, estable = parse_trama(linea)
                    if peso is None:
                        continue

                    # Detectar estabilidad por umbral (cuando el protocolo
                    # no tiene flag explícito)
                    if peso_anterior is not None:
                        diff = abs(peso - peso_anterior)
                        if diff <= STABILITY_THRESHOLD:
                            estable = True

                    peso_anterior = peso
                    state["peso_raw"] = peso
                    state["peso_display"] = formatear_peso(peso)
                    state["estable"] = estable
                    state["ultimo_cambio"] = datetime.now().isoformat()

                    # Broadcast al loop asyncio sin bloquear este thread
                    loop.call_soon_threadsafe(asyncio.ensure_future, broadcast_peso())

        except serial.SerialException as e:
            state["conectado_serial"] = False
            state["error"] = str(e)
            log.warning(f"Error serial: {e}. Reintentando en {RECONNECT_DELAY_SEC}s…")
            loop.call_soon_threadsafe(asyncio.ensure_future, broadcast_error(str(e)))
            time.sleep(RECONNECT_DELAY_SEC)

        except Exception as e:
            state["conectado_serial"] = False
            state["error"] = str(e)
            log.error(f"Error inesperado: {e}")
            time.sleep(RECONNECT_DELAY_SEC)


# ── Broadcast WebSocket ────────────────────────────────────


def build_mensaje() -> str:
    return json.dumps(
        {
            "tipo": "peso",
            "peso": state["peso_raw"],
            "peso_display": state["peso_display"],
            "unidad": state["unidad"],
            "estable": state["estable"],
            "conectado": state["conectado_serial"],
            "ts": state["ultimo_cambio"],
        }
    )


async def broadcast_peso():
    if not clientes:
        return
    msg = build_mensaje()
    await asyncio.gather(
        *[ws.send(msg) for ws in list(clientes)],
        return_exceptions=True,
    )


async def broadcast_error(motivo: str):
    if not clientes:
        return
    msg = json.dumps(
        {
            "tipo": "error",
            "mensaje": motivo,
            "conectado": False,
        }
    )
    await asyncio.gather(
        *[ws.send(msg) for ws in list(clientes)],
        return_exceptions=True,
    )


# ── Servidor WebSocket ─────────────────────────────────────


async def handler(websocket):
    """Maneja un cliente WebSocket nuevo."""
    clientes.add(websocket)
    log.info(f"Cliente conectado: {websocket.remote_address}. Total: {len(clientes)}")

    # Enviar estado actual al conectar (no esperar la próxima trama)
    await websocket.send(
        json.dumps(
            {
                "tipo": "estado_inicial",
                "peso": state["peso_raw"],
                "peso_display": state["peso_display"],
                "unidad": state["unidad"],
                "estable": state["estable"],
                "conectado": state["conectado_serial"],
                "config": {
                    "puerto": COM_PORT,
                    "baudrate": BAUD_RATE,
                    "decimal_places": DECIMAL_PLACES,
                },
            }
        )
    )

    try:
        async for mensaje in websocket:
            # El frontend puede enviar comandos futuros (ej: "tara", "capturar")
            try:
                cmd = json.loads(mensaje)
                await procesar_comando(websocket, cmd)
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clientes.discard(websocket)
        log.info(f"Cliente desconectado. Total: {len(clientes)}")


async def procesar_comando(ws, cmd: dict):
    """Procesa comandos enviados desde el frontend."""
    tipo = cmd.get("tipo")

    if tipo == "ping":
        await ws.send(json.dumps({"tipo": "pong", "ts": datetime.now().isoformat()}))

    elif tipo == "capturar":
        # El frontend pide el peso actual (para captura manual)
        await ws.send(
            json.dumps(
                {
                    "tipo": "captura",
                    "peso": state["peso_raw"],
                    "peso_display": state["peso_display"],
                    "estable": state["estable"],
                    "ts": datetime.now().isoformat(),
                }
            )
        )

    elif tipo == "status":
        await ws.send(
            json.dumps(
                {
                    "tipo": "status",
                    "conectado": state["conectado_serial"],
                    "error": state["error"],
                    "config": {
                        "puerto": COM_PORT,
                        "baudrate": BAUD_RATE,
                        "decimal_places": DECIMAL_PLACES,
                    },
                }
            )
        )


# ── Main ───────────────────────────────────────────────────


async def main():
    log.info("=" * 55)
    log.info("  INVERMIN PAITITI - Agente Balanza v1.0")
    log.info(f"  Puerto : {COM_PORT} @ {BAUD_RATE} baud")
    log.info(f"  WS     : ws://{WS_HOST}:{WS_PORT}")
    log.info(f"  Decimales configurados: {DECIMAL_PLACES}")
    log.info("=" * 55)

    loop = asyncio.get_event_loop()

    # Arrancar hilo serial (daemon = muere solo al cerrar el proceso)
    import threading

    t = threading.Thread(target=leer_serial, args=(loop,), daemon=True)
    t.start()

    # Arrancar servidor WebSocket
    async with websockets.serve(handler, WS_HOST, WS_PORT):
        log.info(f"WebSocket escuchando en ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()  # correr indefinidamente


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Agente detenido por el usuario.")
