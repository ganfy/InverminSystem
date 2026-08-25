from datetime import date, datetime

import requests
from bs4 import BeautifulSoup


def obtener_ultimo_valor_plata_noon() -> tuple[date, float] | None:
    """
    Obtiene el último valor disponible del 'Silver Noon' desde la página de LBMA Fix.
    Retorna una tupla (fecha, valor) o None si ocurre un error.
    """
    url = "https://goldsilver.com/price-charts/historical-london-fix/"

    # Usamos un User-Agent para simular un navegador web y evitar bloqueos básicos
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    try:
        # 1. Realizar la solicitud a la página web
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.raise_for_status()  # Verifica que la petición fue exitosa (código 200)

        # 2. Analizar el contenido HTML
        soup = BeautifulSoup(respuesta.text, "html.parser")

        # 3. Buscar todas las tablas en la página
        tablas = soup.find_all("table")

        for tabla in tablas:
            # Extraer los encabezados de la tabla para identificar la correcta
            encabezados = [th.text.strip() for th in tabla.find_all("th")]

            # Verificamos si es la tabla que contiene "Silver (Noon)"
            if "Silver (Noon)" in encabezados:
                # Obtenemos el índice de la columna Silver (Noon) para saber dónde buscar el dato
                indice_noon = encabezados.index("Silver (Noon)")

                # Extraemos las filas de datos
                cuerpo_tabla = tabla.find("tbody")
                filas = cuerpo_tabla.find_all("tr") if cuerpo_tabla else tabla.find_all("tr")[1:]

                # 4. Recorrer las filas desde la más reciente hasta la más antigua
                for fila in filas:
                    columnas = fila.find_all("td")

                    if len(columnas) > indice_noon:
                        valor_noon = columnas[indice_noon].text.strip()

                        if valor_noon and valor_noon != "-":
                            # Limpiar comas (si las hay) y convertir a número
                            valor_limpio = valor_noon.replace(",", "")
                            # Extraer y parsear la fecha (ej: "24 Aug 2026")
                            fecha_str = columnas[0].text.strip()
                            try:
                                fecha = datetime.strptime(fecha_str, "%d %b %Y").date()
                            except ValueError:
                                fecha = datetime.strptime(fecha_str, "%b %d, %Y").date()
                            return fecha, float(valor_limpio)

    except requests.exceptions.RequestException as e:
        print(f"Error de red al intentar acceder a la página: {e}")
    except Exception as e:
        print(f"Error durante el scraping del precio del plata: {e}")

    return None


# --- Bloque de prueba rápida ---
if __name__ == "__main__":
    resultado = obtener_ultimo_valor_plata_noon()
    if resultado:
        fecha, precio_plata = resultado
        print(
            f"¡Éxito! El último precio de la plata (Noon) es: ${precio_plata} para la fecha {fecha}"
        )
    else:
        print("No se pudo obtener el precio del plata.")
