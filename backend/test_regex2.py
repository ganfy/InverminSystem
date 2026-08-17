import re

text = """
W & M IMPORTACIONES DE CHALA
SOCIEDAD ANONIMA CERRADA
NRO. S/N OTR. D.M. JULISSA VII C.U. 010031805  - PULLO
PARINACOCHAS - AYACUCHO
OTR. LAS TERRAZAS KM. 2 OTR. QUEBRADA EL TOTORAL
(KILOMETRO 616 CARRETERA PANAMERICANA)  - CHALA
CARAVELI - AREQUIPA
RUC N°20606778890
"""

text2 = """
J & M SOLUCIONES MINERAS E.I.R.L.
Fecha de entrega de Bienes al  transportista:08/07/2026
Motivo de Traslado :Venta sujeta a confirmación del comprador
RUC N°20611329556
GUÍA DE REMISIÓN ELECTRÓNICA
REMITENTE
"""


def extract(texto):
    # Buscar hasta la primera mención de RUC
    lineas = texto.splitlines()
    lineas_cabecera = []

    for linea in lineas[:15]:
        linea = linea.strip()
        if not linea or len(linea) < 3:
            continue

        l_upper = linea.upper()
        if "INVERMIN" in l_upper or "ESTA ES UNA" in l_upper:
            continue

        # Si llegamos al RUC, cortamos
        if re.search(r"\bRUC\b", l_upper):
            # Agregar lo que esté antes del RUC en la misma línea
            parte_antes = re.split(r"(?i)\bRUC\b", linea)[0].strip()
            if parte_antes and not re.search(
                r"(?i)(fecha|motivo|punto|direcci|llegada|partida)", parte_antes
            ):
                lineas_cabecera.append(parte_antes)
            break

        # Ignorar líneas que parecen metadata o direcciones
        if re.search(
            r"(?i)^(fecha|motivo|punto|direcci|llegada|partida|referencia|nro\.|otr\.|mza\.|lote\.|av\.|jr\.|calle\.|carretera|kilometro)",
            l_upper,
        ):
            continue

        # Ignorar líneas que son solo provincias/departamentos si ya tenemos algo y no parecen nombres de empresa
        # Para ser conservadores, solo descartamos si tienen indicadores claros de dirección
        if re.search(
            r"(?i)(parinacochas|ayacucho|caraveli|arequipa|lima|ica|nazca|nasca|palpa|pisco|chincha)",
            l_upper,
        ) and not re.search(
            r"\b(E\.I\.R\.L|S\.A\.C|S\.A\.|EMPRESA|MINERA|TRANSPORT|CONSORCIO|COMERCIAL|SOCIEDAD|IMPORTACION)\b",
            l_upper,
        ):
            continue

        lineas_cabecera.append(linea)

    rs = " ".join(lineas_cabecera).strip()
    rs = re.sub(r"\s+", " ", rs)
    if len(rs) > 4:
        return rs
    return None


print("RS 1:", extract(text))
print("RS 2:", extract(text2))
