"""
app/services/balanza_documentos.py
Servicio de documentos adjuntos a sesiones de balanza.

Extracción por OCR. Los documentos de campo son escaneados con CamScanner
y no tienen texto embebido, por lo que se requiere OCR completo.

Fuentes de datos por prioridad:
  1. Ticket propio INVERMIN  → placa, conductor, transportista, razon_social, ruc, guia
  2. GRR electrónica SUNAT   → transportista, placa, conductor, peso, guia (fallback)
  3. GRT (escaneado)         → guia_transporte como fallback
  4. Licencia de conducir    → solo detección de tipo

━━━ INSTALACIÓN (solo pip, sin binarios extra en Linux/producción) ━━━━━━━━

    pip install pymupdf pytesseract pillow

  pymupdf (fitz):
    Wheel pre-compilado con MuPDF embebido. Convierte PDFs a imágenes
    SIN necesitar poppler. Funciona en Windows/Linux/Mac con solo pip.

  tesseract (motor OCR - único binario requerido):
    Linux/servidor : apt install tesseract-ocr
    Windows dev    : instalar desde https://github.com/UB-Mannheim/tesseract/wiki
                     Luego añadir al .env:
                     TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from app.core.config import get_settings as _get_settings
from app.models.models import SesionDocumento  # ajusta a tu modelo real
from fastapi import UploadFile
from sqlalchemy.orm import Session

# ─── Configuración ────────────────────────────────────────────────────────────
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "storage"))
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
TIPOS_PERMITIDOS = {"pdf", "jpg", "jpeg", "png"}
OCR_LANG = "eng"  # cambiar a "spa" si instalas tesseract-ocr-spa
OCR_CONFIG = "--psm 6"
OCR_DPI = 300  # usado por pymupdf para el render (zoom = DPI/72)


# Leer TESSERACT_PATH desde pydantic Settings (que sí parsea el .env correctamente).
# os.getenv() NO funciona aquí porque pydantic-settings carga el .env internamente
# sin inyectarlo en os.environ.
def _configurar_tesseract() -> None:
    try:
        import pytesseract as _pt

        ruta = _get_settings().tesseract_path
        if ruta:
            _pt.pytesseract.tesseract_cmd = ruta
            print(f"[OCR] Tesseract configurado: {ruta}")
        else:
            print("[OCR] Tesseract en PATH del sistema (TESSERACT_PATH no definido)")
    except ImportError:
        pass


_configurar_tesseract()


# ═══════════════════════════════════════════════════════════════════════════════
#  CRUD de documentos
# ═══════════════════════════════════════════════════════════════════════════════


def subir_documento(
    db: Session, sesion_id: int, archivo: UploadFile, tipo_documento: str, usuario_id: int
) -> SesionDocumento:
    contenido = archivo.file.read()
    if len(contenido) > MAX_FILE_SIZE:
        raise ValueError("El archivo supera los 10 MB permitidos")

    ext = Path(archivo.filename or "").suffix.lstrip(".").lower()
    if ext not in TIPOS_PERMITIDOS:
        raise ValueError(f"Tipo no permitido: .{ext}")

    ahora = datetime.now()
    carpeta = STORAGE_PATH / "sesiones" / str(ahora.year) / f"{ahora.month:02d}" / str(sesion_id)
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre_guardado = f"{uuid.uuid4().hex}.{ext}"
    ruta = carpeta / nombre_guardado
    ruta.write_bytes(contenido)

    doc = SesionDocumento(
        sesion_id=sesion_id,
        nombre_original=archivo.filename or nombre_guardado,
        ruta_archivo=str(ruta),
        tipo_documento=tipo_documento,
        creado_por=usuario_id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def listar_documentos(db: Session, sesion_id: int) -> list[SesionDocumento]:
    return (
        db.query(SesionDocumento)
        .filter(SesionDocumento.sesion_id == sesion_id)
        .order_by(SesionDocumento.id)
        .all()
    )


def obtener_archivo(db: Session, sesion_id: int, doc_id: int) -> tuple[Path, str]:
    doc = (
        db.query(SesionDocumento)
        .filter(SesionDocumento.id == doc_id, SesionDocumento.sesion_id == sesion_id)
        .first()
    )
    if not doc:
        raise ValueError("Documento no encontrado")

    ruta_real = Path(doc.ruta_archivo)
    if not ruta_real.exists():
        raise ValueError("El archivo físico no se encuentra en el servidor")

    return ruta_real, doc.nombre_original


def eliminar_documento(db: Session, sesion_id: int, doc_id: int) -> None:
    doc = (
        db.query(SesionDocumento)
        .filter(
            SesionDocumento.id == doc_id,
            SesionDocumento.sesion_id == sesion_id,
        )
        .first()
    )
    if not doc:
        raise ValueError("Documento no encontrado")
    doc.eliminado = True
    db.commit()


def eliminar_documento_físico(db: Session, sesion_id: int, doc_id: int) -> None:
    doc = (
        db.query(SesionDocumento)
        .filter(SesionDocumento.id == doc_id, SesionDocumento.sesion_id == sesion_id)
        .first()
    )
    if not doc:
        raise ValueError("Documento no encontrado")

    ruta_real = Path(doc.ruta_archivo)
    if ruta_real.exists():
        try:
            ruta_real.unlink()
        except OSError:
            pass

    db.delete(doc)
    db.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  OCR - extracción de texto
#
#  PDF → imagen : pymupdf  (pip install pymupdf)
#                 Wheel pre-compilado, incluye MuPDF. Sin poppler.
#                 Funciona en Windows/Linux/Mac con solo pip.
#
#  Imagen → texto: pytesseract  (pip install pytesseract)
#                 Requiere tesseract instalado en el sistema:
#                   Linux  : apt install tesseract-ocr
#                   Windows: https://github.com/UB-Mannheim/tesseract/wiki
#                            + TESSERACT_PATH en .env si no está en PATH
# ═══════════════════════════════════════════════════════════════════════════════


def _pdf_a_imagenes_pil(ruta: Path) -> list:
    """
    Renderiza cada página del PDF como imagen PIL usando pymupdf.
    No requiere poppler ni ningún binario externo.
    """
    try:
        import fitz  # pymupdf
    except ImportError as e:
        raise RuntimeError(
            "Instala pymupdf: pip install pymupdf\n"
            "(reemplaza a pdf2image+poppler - no requiere binarios externos)"
        ) from e

    doc = fitz.open(str(ruta))
    imagenes = []
    # matrix escala el render: 300 DPI ≈ zoom 4.17 (72 DPI base de PDF)
    zoom = OCR_DPI / 72
    mat = fitz.Matrix(zoom, zoom)

    for pagina in doc:
        pix = pagina.get_pixmap(matrix=mat, alpha=False)
        # Convertir pixmap de fitz a bytes PNG y luego a PIL Image
        import io

        from PIL import Image

        img_bytes = pix.tobytes("png")
        imagenes.append(Image.open(io.BytesIO(img_bytes)))

    doc.close()
    return imagenes


def _ocr_imagen_pil(img) -> str:
    """Aplica OCR a una imagen PIL. Tesseract debe estar instalado."""
    try:
        import pytesseract
    except ImportError as e:
        raise RuntimeError("Instala pytesseract: pip install pytesseract") from e

    try:
        return pytesseract.image_to_string(img, lang=OCR_LANG, config=OCR_CONFIG)
    except pytesseract.TesseractNotFoundError as e:
        raise ValueError(
            "Tesseract OCR no encontrado. "
            "Linux: apt install tesseract-ocr  |  "
            "Windows: instala desde https://github.com/UB-Mannheim/tesseract/wiki "
            "y añade TESSERACT_PATH=C:\\Program Files\\Tesseract-OCR\\tesseract.exe al .env"
        ) from e


def _obtener_textos(ruta: Path) -> list[str]:
    """Extrae texto OCR de un archivo. PDF → una entrada por página. Imagen → una entrada."""
    ext = ruta.suffix.lstrip(".").lower()
    if ext == "pdf":
        imagenes = _pdf_a_imagenes_pil(ruta)
        return [_ocr_imagen_pil(img) for img in imagenes]
    elif ext in ("jpg", "jpeg", "png"):
        from PIL import Image

        return [_ocr_imagen_pil(Image.open(str(ruta)))]
    return []


# ═══════════════════════════════════════════════════════════════════════════════
#  Detectores de tipo de documento
# ═══════════════════════════════════════════════════════════════════════════════


def _es_ticket_invermin(texto: str) -> bool:
    """
    Ticket generado por el sistema propio de INVERMIN.
    Tiene formato tabulado muy limpio con campos clave.
    """
    t = texto.upper()
    return (
        "INVERMIN PAITITI" in t
        and ("RAZON SOCIAL" in t or "RAZON SOCIAL" in texto)
        and ("PESO NETO" in t or "PESO BRUTO" in t)
        and "PLANTA EL DORADO" in t
    )


def _es_grr(texto: str) -> bool:
    """
    Guía de Remisión Electrónica SUNAT (GRR / GURE).
    Palabras clave que aparecen siempre en estos documentos.
    """
    t = texto.upper()
    return (
        sum(
            1
            for k in [
                "GUIA DE REMISION ELECTRONICA",
                "GUIA DE REMISIÓN ELECTRÓNICA",
                "REMITENTE",
                "DATOS DEL DESTINATARIO",
                "DATOS DEL TRANSPORTISTA",
                "NUMERO DE PLACA",
            ]
            if k in t
        )
        >= 3
    )


def _es_grt(texto: str) -> bool:
    """Guía de Remisión - Transportista (papel, escaneado)."""
    t = texto.upper()

    return (
        "TRANSPORTISTA"
        or "TRANSPORTE" in t
        and ("RMTC" in t or "N° DE R.U.C" in t or "PUNTO DE PARTIDA" in t)
        and "REMITENTE" not in t  # distinguir de GRR
        and "DECLARACION" not in t  # distinguir de declaración jurada de transporte
    )


def _es_licencia(texto: str) -> bool:
    t = texto.upper()
    return ("LICENCIA DE CONDUCIR" in t or "MINISTERIO DE TRANSPORTES" in t) and ("MTC" in t)


# ═══════════════════════════════════════════════════════════════════════════════
#  Extractores por tipo
# ═══════════════════════════════════════════════════════════════════════════════


def _normalizar_placa(raw: str) -> str:
    """
    Normaliza placas peruanas:
      "C9P908"  → "C9P-908"
      "C9P 908" → "C9P-908"
      "AB1234"  → "AB-1234"  (placa antigua)
    """
    s = raw.upper().replace(" ", "").replace("-", "")
    # Formato moderno: 3 alfanum + 3 num  →  ABC-123 o C9P-908
    m = re.match(r"^([A-Z0-9]{3})([0-9]{3})$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    # Formato antiguo: 2 letras + 4 num
    m = re.match(r"^([A-Z]{2})(\d{4})$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return raw.strip()


def _normalizar_guia(serie: str, numero: str) -> str:
    """
    Normaliza número de guía corrigiendo artefactos OCR en la serie.
      "EG07"  + "00000306" → "EG07-00000306"
      "EGO7"  + "00000306" → "EG07-00000306"  (O confundida con 0 por OCR)
    Los ceros a la izquierda del número se conservan tal como están en el documento.
    """
    # Corregir O→0 en posición numérica dentro de la serie
    # Ej: EGO7 → EG07  (la O está entre G y 7, debe ser 0)
    serie_norm = re.sub(r"(?<=[A-Z])O(?=[0-9])|(?<=[0-9])O(?=[0-9])", "0", serie.upper())
    return f"{serie_norm}-{numero}"


def _extraer_de_ticket_invermin(texto: str) -> dict:
    """
    Extrae del ticket propio de INVERMIN PAITITI.
    Formato muy estructurado - OCR excelente en esta página.
    Ejemplo real:
        Placa       : C9P-908  Carreta : 0
        Conductor   : [Q22094676] MENDOZA CAJAMARCA PERCY MARTIN
        Transportista : MENDOZA GARRIAZO MARTIN OSMAR
        Razon Social  : [20612921866] EMPRESA MINERA GRUPO GARIBAY ESCUDERO E.I.R.L.
        Documento     : EG07-306
    """
    r: dict = {}

    # Placa: "Placa : C9P-908"
    m = re.search(r"[Pp]laca\s*:\s*([A-Z0-9]{2,3}[\s\-]?[A-Z0-9]{3,4})", texto)
    if m:
        r["placa"] = _normalizar_placa(m.group(1).strip())

    # Carreta: "Carreta : 7" (ignorar 0 o guion = sin carreta)
    m = re.search(r"[Cc]arreta\s*:\s*(\S+)", texto)
    if m and m.group(1) not in ("0", "-", "-"):
        r["carreta"] = m.group(1).strip()

    # Conductor: "Conductor : [Q22094676] MENDOZA CAJAMARCA PERCY MARTIN"
    # El DNI aparece entre corchetes con primera letra a veces OCR-izada
    m = re.search(r"[Cc]onductor\s*:\s*\[[^\]]*\]\s+(.+)", texto)
    if m:
        r["conductor"] = m.group(1).strip()

    # Transportista: "Transportista : MENDOZA GARRIAZO MARTIN OSMAR"
    m = re.search(r"[Tt]ransportista\s*:\s*(.+)", texto)
    if m:
        val = m.group(1).strip()
        # Evitar capturar la línea de "Razon Social" si hay contaminación
        val = re.split(r"\n|[Rr]azon", val)[0].strip()
        r["transportista"] = val

    # Razón social + RUC: "Razon Social : [20612921866] EMPRESA MINERA..."
    m = re.search(r"[Rr]azon\s+[Ss]ocial\s*[:\>]+\s*\[(\d{8,12})\]\s+(.+)", texto)
    if m:
        r["ruc_proveedor"] = m.group(1)
        rs = m.group(2).strip()
        # Limpiar artefactos OCR comunes
        rs = re.sub(r"\s+", " ", rs).strip()
        r["razon_social"] = rs

    # Guía de remisión: "Documento : EG07-306"
    # OCR frecuentemente confunde 0 con O en la serie: "EGO7-306" en lugar de "EG07-306"
    # Solución: aceptar letras Y dígitos mezclados en la parte de la serie ([A-Z0-9])
    m = re.search(r"[Dd]ocumento\s*:\s*([A-Z][A-Z0-9]{2,8}[-–][0-9]+)", texto)
    if m:
        raw = m.group(1).strip().replace("–", "-")
        partes = raw.split("-", 1)
        if len(partes) == 2:
            r["guia_remision"] = _normalizar_guia(partes[0], partes[1])
        else:
            r["guia_remision"] = raw

    return r


def _extraer_de_grr(texto: str) -> dict:
    """
    Extrae de la GRR Electrónica SUNAT (imagen escaneada o impresa).
    El OCR funciona bien en estas páginas (tipografía estándar).

    Campos objetivo:
      - Número de guía: "N° EG07 - 00000306"
      - Transportista:  "MENDOZA GARRIAZO MARTIN OSMAR - REGISTRO ÚNICO..."
      - Placa:          "Número de placa: C9P908"
      - Conductor:      "Principal: MENDOZA CAJAMARCA... - DOCUMENTO NACIONAL..."
      - Peso bruto TM:  "Peso Bruto total de la carga: 9.5"
    """
    r: dict = {}

    # ── Número de guía ────────────────────────────────────────────────────────
    # "N° EG07 - 00000306"  o  "N° EGO7 - 00000306" (OCR confunde 0/O en la serie)
    # Aceptar letras Y dígitos mezclados con [A-Z0-9] en toda la serie
    m = re.search(r"N[°oO\u00ba]\s*([A-Z][A-Z0-9]{2,8})\s*[-–]\s*(\d{4,10})", texto, re.IGNORECASE)
    if m:
        r["guia_remision"] = _normalizar_guia(m.group(1), m.group(2))

    # ── Transportista ─────────────────────────────────────────────────────────
    # Aparece en "Datos del transportista:" seguido de NOMBRE - REGISTRO ÚNICO...
    m = re.search(
        r"[Dd]atos del transportista[:\s]*\n([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\-]+?)\s*[-–]\s*REGISTRO\s*[ÚU]NICO",
        texto,
        re.IGNORECASE,
    )
    if m:
        r["transportista"] = re.sub(r"\s+", " ", m.group(1)).strip()

    # ── Placa ─────────────────────────────────────────────────────────────────
    # "Número de placa:  C9P908"
    m = re.search(
        r"[Nn]umero de placa[:\s]+([A-Z0-9]{2,3}[\s\-]?[A-Z0-9]{3,4})", texto, re.IGNORECASE
    )
    if m:
        r["placa"] = _normalizar_placa(m.group(1).strip())

    # ── Conductor ─────────────────────────────────────────────────────────────
    # "Principal:   MENDOZA CAJAMARCA PERCY MARTIN - DOCUMENTO NACIONAL..."
    m = re.search(
        r"[Pp]rincipal[:\s]+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]+?)\s*[-–]\s*DOCUMENTO\s*NACIONAL",
        texto,
        re.IGNORECASE,
    )
    if m:
        r["conductor"] = re.sub(r"\s+", " ", m.group(1)).strip()

    # ── Peso bruto declarado (TM) ─────────────────────────────────────────────
    # "Peso Bruto total de la carga: 9.5"
    m = re.search(r"Peso Bruto total de la carga[:\s]+([\d]+(?:[.,]\d+)?)", texto, re.IGNORECASE)
    if m:
        try:
            r["peso_declarado_tm"] = float(m.group(1).replace(",", "."))
        except ValueError:
            pass

    # ── RUC del proveedor (fallback si no hay ticket) ─────────────────────────
    # En la GRR el RUC del encabezado suele corromperse por OCR.
    # Buscamos el RUC en la línea de "Datos del Destinatario" como ancla
    # y tomamos el RUC que NO sea de INVERMIN (20601910587)
    todos_ruc = re.findall(r"\b((?:10|20)\d{9})\b", texto)
    ruc = "20601910587"
    externos = [r for r in todos_ruc if r != ruc]
    if externos:
        # El primer RUC externo de 20xxxxxxxx es el proveedor (persona jurídica)
        proveedores = [r for r in externos if r.startswith("20")]
        if proveedores:
            r["ruc_proveedor"] = proveedores[0]

    return r


def _extraer_de_grt(texto: str) -> dict:
    """
    GRT (Guía de Remisión Transportista) - escaneada, OCR variable.
    Extrae guia_transporte y confirma placa/conductor como fallback.

    Ejemplo real: "0002  N° 0004072"
    """
    r: dict = {}

    # Guía de transporte: "0002  N° 0004072"
    # Formato: SERIE(4 dígitos) + correlativo
    m = re.search(r"\b(\d{4})\s+N[°oO]?\s*(\d{4,8})\b", texto)
    if m:
        serie = m.group(1).zfill(4)
        num = str(int(m.group(2)))
        r["guia_transporte"] = f"{serie}-{num}"

    # Placa desde GRT: "Unidad de Transporte ... ISUZU C9P 908"
    m = re.search(
        r"[Uu]nidad de [Tt]ransporte[^\n]+?([A-Z0-9]{2,3}[\s\-]?[A-Z0-9]{3,4})\s*$",
        texto,
        re.MULTILINE,
    )
    if m:
        r["placa_grt"] = _normalizar_placa(m.group(1).strip())

    return r


# ═══════════════════════════════════════════════════════════════════════════════
#  Función principal - extracción desde rutas guardadas
# ═══════════════════════════════════════════════════════════════════════════════


def extraer_datos_sesion(db: Session, sesion_id: int) -> dict:
    """
    Lee todos los documentos de la sesión, aplica OCR y extrae los campos.
    Prioridad: ticket INVERMIN > GRR > GRT.
    """
    docs = listar_documentos(db, sesion_id)
    archivos = [(Path(doc.ruta), doc.tipo_documento) for doc in docs if Path(doc.ruta).exists()]

    if not archivos:
        raise ValueError("No hay documentos adjuntos en esta sesión")

    return _procesar_archivos(archivos)


def extraer_datos_archivos_directos(archivos_upload: list[UploadFile]) -> dict:
    """
    Variante stateless: recibe UploadFile[], procesa en /tmp, retorna datos
    sin guardar nada en disco ni en BD.
    Usado en el formulario de registro antes de crear la sesión.
    """
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        pares: list[tuple[Path, str]] = []
        for uf in archivos_upload:
            ext = Path(uf.filename or "").suffix.lstrip(".").lower()
            if ext not in TIPOS_PERMITIDOS:
                continue
            ruta_tmp = tmp_dir / f"{uuid.uuid4().hex}.{ext}"
            contenido = uf.file.read()
            uf.file.seek(0)
            ruta_tmp.write_bytes(contenido)
            pares.append((ruta_tmp, "DESCONOCIDO"))

        if not pares:
            raise ValueError("No se encontraron archivos válidos (PDF, JPG, PNG).")

        return _procesar_archivos(pares)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  Núcleo de procesamiento multi-archivo
# ═══════════════════════════════════════════════════════════════════════════════


def _procesar_archivos(pares: list[tuple[Path, str]]) -> dict:
    """
    Dado una lista de (Path, tipo_guardado), extrae OCR de cada página,
    detecta el tipo real del documento y combina resultados por prioridad.
    """
    resultado: dict = {
        "placa": None,
        "carreta": None,
        "conductor": None,
        "transportista": None,
        "razon_social": None,
        "ruc_proveedor": None,
        "guia_remision": None,
        "guia_transporte": None,
        "peso_declarado_tm": None,
        "documentos_detectados": [],
    }

    # Recopilar todos los textos con su tipo detectado
    bloques: list[tuple[str, str]] = []  # (texto, tipo_detectado)

    for ruta, _ in pares:
        textos = _obtener_textos(ruta)
        for texto in textos:
            if not texto.strip():
                continue
            if _es_ticket_invermin(texto):
                bloques.append((texto, "TICKET_INVERMIN"))
            elif _es_grr(texto):
                bloques.append((texto, "GUIA_REMISION"))
            elif _es_grt(texto):
                bloques.append((texto, "GUIA_TRANSPORTE"))
            elif _es_licencia(texto):
                bloques.append((texto, "LICENCIA_CONDUCIR"))
            else:
                bloques.append((texto, "OTRO"))

    if not bloques:
        raise ValueError(
            "No se pudo extraer texto de los documentos. "
            "Asegúrate de subir PDFs o imágenes legibles."
        )

    # Registrar tipos detectados (únicos)
    resultado["documentos_detectados"] = list(dict.fromkeys(t for _, t in bloques if t != "OTRO"))

    # ── Aplicar por prioridad ──────────────────────────────────────────────────
    # 1. Ticket INVERMIN - fuente más confiable para todos los campos
    for texto, tipo in bloques:
        if tipo != "TICKET_INVERMIN":
            continue
        datos = _extraer_de_ticket_invermin(texto)
        for k in (
            "placa",
            "carreta",
            "conductor",
            "transportista",
            "razon_social",
            "ruc_proveedor",
            "guia_remision",
        ):
            if datos.get(k) and not resultado[k]:
                resultado[k] = datos[k]

    # 2. GRR - complementa o rellena lo que falta
    for texto, tipo in bloques:
        if tipo != "GUIA_REMISION":
            continue
        datos = _extraer_de_grr(texto)
        for k in (
            "placa",
            "conductor",
            "transportista",
            "ruc_proveedor",
            "guia_remision",
            "peso_declarado_tm",
        ):
            if datos.get(k) and not resultado[k]:
                resultado[k] = datos[k]

    # 3. GRT - solo guia_transporte y placa como último recurso
    for texto, tipo in bloques:
        if tipo != "GUIA_TRANSPORTE":
            continue
        datos = _extraer_de_grt(texto)
        if datos.get("guia_transporte") and not resultado["guia_transporte"]:
            resultado["guia_transporte"] = datos["guia_transporte"]
        if datos.get("placa_grt") and not resultado["placa"]:
            resultado["placa"] = datos["placa_grt"]

    # ── Validación mínima ──────────────────────────────────────────────────────
    campos_clave = [resultado["placa"], resultado["conductor"], resultado["guia_remision"]]
    if not any(campos_clave):
        raise ValueError(
            "No se encontraron datos reconocibles en los documentos. "
            "Verifica que los archivos sean legibles (no muy oscuros o borrosos)."
        )

    return resultado
