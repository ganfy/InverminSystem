"""
=============================================================
  INVERMIN PAITITI S.A.C. — Diagnóstico de Balanza
  Ejecutar: python balanza_diagnostico.py
  Requisito: pip install pyserial
=============================================================
Este script detecta puertos COM disponibles, intenta leer
datos de la balanza y guarda un reporte para el desarrollador.
"""

import datetime
import json
import os
import sys
import time

import serial
import serial.tools.list_ports

REPORTE = "reporte_balanza.json"

# Configuraciones más comunes en balanzas industriales
CONFIGS_COMUNES = [
    {"baudrate": 9600, "bytesize": 8, "parity": "N", "stopbits": 1},
    {"baudrate": 4800, "bytesize": 8, "parity": "N", "stopbits": 1},
    {"baudrate": 19200, "bytesize": 8, "parity": "N", "stopbits": 1},
    {"baudrate": 2400, "bytesize": 8, "parity": "N", "stopbits": 1},
    {"baudrate": 9600, "bytesize": 7, "parity": "E", "stopbits": 1},  # Mettler Toledo
    {"baudrate": 9600, "bytesize": 8, "parity": "N", "stopbits": 2},
]

TIMEOUT_LECTURA = 3  # segundos esperando respuesta por intento
INTENTOS_LECTURA = 5  # líneas a leer por configuración


def separador(titulo=""):
    print("\n" + "=" * 55)
    if titulo:
        print(f"  {titulo}")
        print("=" * 55)


def listar_puertos():
    """Detecta todos los puertos COM disponibles en el sistema."""
    separador("PUERTOS COM DETECTADOS")
    puertos = list(serial.tools.list_ports.comports())

    if not puertos:
        print("No se encontraron puertos COM.")
        print("     Verifica que la balanza esté conectada por USB o RS-232.")
        return []

    info_puertos = []
    for p in puertos:
        print(f"     {p.device}")
        print(f"     Descripción : {p.description}")
        print(f"     Fabricante  : {p.manufacturer or 'Desconocido'}")
        print(f"     HWID        : {p.hwid}")
        print()
        info_puertos.append(
            {
                "puerto": p.device,
                "descripcion": p.description,
                "fabricante": p.manufacturer,
                "hwid": p.hwid,
            }
        )

    return info_puertos


def probar_puerto(puerto, config):
    """Intenta leer datos de un puerto con una configuración dada."""
    lecturas = []
    try:
        with serial.Serial(
            port=puerto,
            baudrate=config["baudrate"],
            bytesize=config["bytesize"],
            parity=config["parity"],
            stopbits=config["stopbits"],
            timeout=TIMEOUT_LECTURA,
        ) as ser:
            time.sleep(0.5)  # espera estabilización
            for _ in range(INTENTOS_LECTURA):
                linea = ser.readline()
                if linea:
                    # Intentar decodificar con varios encodings comunes
                    for enc in ["ascii", "utf-8", "latin-1"]:
                        try:
                            decoded = linea.decode(enc).strip()
                            if decoded:
                                lecturas.append(
                                    {
                                        "raw_hex": linea.hex(),
                                        "texto": decoded,
                                        "encoding": enc,
                                    }
                                )
                            break
                        except Exception:
                            continue
    except serial.SerialException as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

    return lecturas, None


def diagnosticar():
    separador("DIAGNÓSTICO DE BALANZA — INVERMIN PAITITI")
    print(f"  Fecha   : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Sistema : {sys.platform}")
    print(f"  Python  : {sys.version.split()[0]}")

    reporte = {
        "fecha": datetime.datetime.now().isoformat(),
        "sistema": sys.platform,
        "python": sys.version.split()[0],
        "puertos": [],
        "resultados": [],
        "conclusion": "",
    }

    # 1. Listar puertos
    puertos_info = listar_puertos()
    reporte["puertos"] = puertos_info

    if not puertos_info:
        reporte["conclusion"] = "Sin puertos COM detectados."
        guardar_reporte(reporte)
        return

    # 2. Probar cada puerto con cada configuración
    separador("INTENTANDO LEER DATOS DE BALANZA")
    exitoso = False

    for info in puertos_info:
        puerto = info["puerto"]
        print(f"\n  🔌 Probando puerto: {puerto}")
        resultado_puerto = {"puerto": puerto, "configs_probadas": []}

        for cfg in CONFIGS_COMUNES:
            cfg_str = f"{cfg['baudrate']}-{cfg['bytesize']}{cfg['parity']}{cfg['stopbits']}"
            print(f"     Config {cfg_str:15s} ... ", end="", flush=True)

            lecturas, error = probar_puerto(puerto, cfg)

            if error:
                print(f"Error: {error[:60]}")
                resultado_puerto["configs_probadas"].append(
                    {
                        "config": cfg_str,
                        "exito": False,
                        "error": error,
                    }
                )
                continue

            if lecturas:
                print(f"¡DATOS RECIBIDOS! ({len(lecturas)} lecturas)")
                for i, lecture in enumerate(lecturas):
                    print(
                        f"        [{i+1}] '{lecture['texto']}'  (hex: {lecture['raw_hex'][:30]}...)"
                    )
                resultado_puerto["configs_probadas"].append(
                    {
                        "config": cfg_str,
                        "exito": True,
                        "lecturas": lecturas,
                        **cfg,
                    }
                )
                exitoso = True
            else:
                print("Sin respuesta (timeout)")
                resultado_puerto["configs_probadas"].append(
                    {
                        "config": cfg_str,
                        "exito": False,
                        "error": "Timeout — sin datos",
                    }
                )

        reporte["resultados"].append(resultado_puerto)

    # 3. Conclusión
    separador("CONCLUSIÓN")
    if exitoso:
        print("Se detectaron datos de la balanza.")
        print("     Revisar reporte para ver configuración correcta.")
        reporte["conclusion"] = "Lectura exitosa. Ver configs_probadas con exito=true."
    else:
        print("No se recibieron datos de ningún puerto.")
        print()
        print("  Posibles causas:")
        print("  1. La balanza no está enviando datos continuamente.")
        print("     → Algunos modelos solo envían al presionar una tecla (modo petición).")
        print("     → Mientras corre el script, presiona el botón PRINT o SEND en la balanza.")
        print("  2. Cable RS-232 desconectado o adaptador USB-Serial sin driver.")
        print("  3. La balanza usa protocolo propietario (ej: Mettler MT-SICS).")
        print()
        print("Comparte el archivo reporte_balanza.json con el desarrollador.")
        reporte["conclusion"] = "Sin lectura. Ver puertos detectados y errores."

    guardar_reporte(reporte)


def guardar_reporte(reporte):
    separador("REPORTE GUARDADO")
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), REPORTE)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    print(f"Archivo: {ruta}")
    print()
    print("Envía este archivo al desarrollador para continuar.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    try:
        import serial
    except ImportError:
        print("\nFalta instalar pyserial.")
        print("   Ejecuta: pip install pyserial\n")
        sys.exit(1)

    diagnosticar()
    input("\nPresiona ENTER para cerrar...")
