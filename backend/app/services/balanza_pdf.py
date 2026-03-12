"""
Service — Generación de Ticket PDF (RF-BAL-003)

Motor: xhtml2pdf (pisa) — puro Python, sin dependencias nativas.
Instalar: pip install xhtml2pdf

Funciones públicas:
    generar_ticket_pdf(db, sesion_id, lote_id) → bytes   (un lote)
    generar_tickets_sesion_pdf(db, sesion_id)  → bytes   (todos los lotes)
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.models.models import Configuracion, Lote, ProveedorAcopiador, SesionDescarga
from sqlalchemy.orm import Session, joinedload

_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "ticket_balanza.html"


# =============================================================================
# DTO interno
# =============================================================================


@dataclass
class _TicketData:
    ip: str
    numero_lote: int
    numero_ticket: str
    estado: str
    tipo_material: str
    proveedor_razon_social: str
    proveedor_ruc: str
    acopiador_razon_social: str
    mostrar_acopiador: bool
    placa: str
    conductor: str
    guia_remision: str
    guia_transporte: str
    sacos: str
    granel: str
    peso_bruto: str
    peso_tara: str
    peso_neto: str
    fecha_ingreso: str


# =============================================================================
# Helpers
# =============================================================================


def _fmt(valor: Decimal | None) -> str:
    return f"{valor:.3f}" if valor is not None else "-"


def _fecha_fmt(dt: datetime | None) -> str:
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "-"


def _val(valor: str | None, fallback: str = "-") -> str:
    """Devuelve el valor limpio, o fallback si está vacío/None — evita {{ }} en el HTML."""
    if valor is None:
        return fallback
    v = valor.strip()
    return v if v else fallback


def _str(valor: str | None) -> str:
    return valor.strip() if valor else "-"


def _build_ticket_data(lote: Lote) -> _TicketData:
    sesion: SesionDescarga = lote.sesion
    provacop: ProveedorAcopiador = sesion.provacop
    proveedor = provacop.proveedor
    acopiador = provacop.acopiador
    es_propio = provacop.proveedor_id == provacop.acopiador_id
    pesaje = lote.pesajes[0] if lote.pesajes else None

    documento = _val(sesion.guia_remision or sesion.guia_transporte)

    if pesaje and pesaje.granel:
        obs_tipo = "GRANEL"
    elif pesaje and pesaje.sacos:
        obs_tipo = f"{pesaje.sacos} SACOS"
    else:
        obs_tipo = ""
    observaciones = f"{lote.ip} LOTE-{lote.numero_lote}" + (f" {obs_tipo}" if obs_tipo else "")

    # Número de ticket: solo el ID numérico del pesaje
    numero_ticket = str(pesaje.id) if pesaje else "-"

    return _TicketData(
        numero_ticket=numero_ticket,
        placa=_val(sesion.placa),
        carreta=_val(sesion.carreta, "—"),
        conductor=_val(sesion.conductor),
        transportista=_val(sesion.transportista),
        razon_social=_val(sesion.razon_social),
        proveedor_razon_social=_val(proveedor.razon_social),
        proveedor_ruc=_val(proveedor.ruc),
        acopiador_razon_social=_val(acopiador.razon_social),
        mostrar_acopiador=not es_propio,
        tipo_material=_val(lote.tipo_material, "—").upper(),
        documento=documento,
        observaciones=observaciones,
        fecha_inicio=_fecha_fmt(pesaje.fecha_inicio if pesaje else None),
        fecha_fin=_fecha_fmt(pesaje.fecha_fin if pesaje else None),
        peso_bruto=_fmt(pesaje.peso_inicial if pesaje else None),
        peso_tara=_fmt(pesaje.peso_final if pesaje else None),
        peso_neto=_fmt(pesaje.peso_neto if pesaje else None),
    )


def _get_config(db: Session) -> dict[str, str]:
    """Lee parámetros de empresa desde configuraciones. Fallback a valores hardcodeados."""
    defaults = {
        "empresa_nombre": "INVERMIN PAITITI S.A.C.",
        "empresa_planta": "Planta El Dorado",
        "empresa_ruc": "20601910587",
    }
    rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(defaults.keys()))
        .all()
    )
    return {**defaults, **{r.clave: r.valor for r in rows}}


def _render_template(data: _TicketData, config: dict[str, str]) -> str:
    """Renderiza ticket_balanza.html con sustitución simple de variables."""
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")

    # Bloque acopiador condicional
    acopiador_block_marker = "{% if acopiador_html %}"
    acopiador_end_marker = "{% endif %}"
    if not data.mostrar_acopiador:
        start = template.find(acopiador_block_marker)
        end = template.find(acopiador_end_marker, start) + len(acopiador_end_marker)
        if start != -1 and end != -1:
            template = template[:start] + template[end:]
    else:
        template = template.replace(acopiador_block_marker + "\n", "")
        template = template.replace(acopiador_end_marker + "\n", "")

    replacements = {
        "{{ empresa_nombre }}": config["empresa_nombre"],
        "{{ empresa_planta }}": config["empresa_planta"],
        "{{ empresa_ruc }}": config["empresa_ruc"],
        "{{ ip }}": data.ip,
        "{{ numero_lote }}": str(data.numero_lote),
        "{{ numero_ticket }}": data.numero_ticket,
        "{{ estado }}": data.estado,
        "{{ tipo_material }}": data.tipo_material,
        "{{ proveedor_razon_social }}": data.proveedor_razon_social,
        "{{ proveedor_ruc }}": data.proveedor_ruc,
        "{{ acopiador_razon_social }}": data.acopiador_razon_social,
        "{{ placa }}": data.placa,
        "{{ conductor }}": data.conductor,
        "{{ guia_remision }}": data.guia_remision,
        "{{ guia_transporte }}": data.guia_transporte,
        "{{ sacos }}": data.sacos,
        "{{ granel }}": data.granel,
        "{{ peso_bruto }}": data.peso_bruto,
        "{{ peso_tara }}": data.peso_tara,
        "{{ peso_neto }}": data.peso_neto,
        "{{ fecha_ingreso }}": data.fecha_ingreso,
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)

    return template


# =============================================================================
# Motor PDF — xhtml2pdf (puro Python, sin GTK ni libgobject)
# pip install xhtml2pdf
# =============================================================================


def _html_to_pdf(html: str) -> bytes:
    """Convierte HTML a PDF usando xhtml2pdf (pisa)."""
    try:
        from xhtml2pdf import pisa  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError("xhtml2pdf no está instalado. Ejecutar: pip install xhtml2pdf") from exc

    buffer = io.BytesIO()
    result = pisa.CreatePDF(io.StringIO(html), dest=buffer, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"Error al generar PDF: {result.err}")
    return buffer.getvalue()


def _multi_html_to_pdf(html_pages: list[str]) -> bytes:
    """
    Combina varios tickets en un único PDF.
    Extrae el <head> del primero, concatena todos los <body> con saltos de página.
    """
    if not html_pages:
        raise ValueError("No hay páginas para generar el PDF")
    if len(html_pages) == 1:
        return _html_to_pdf(html_pages[0])

    first = html_pages[0]
    head_end = first.find("</head>") + len("</head>")
    head_section = first[:head_end]

    bodies: list[str] = []
    for i, page in enumerate(html_pages):
        body_start = page.find("<body>") + len("<body>")
        body_end = page.find("</body>")
        body_content = page[body_start:body_end].strip()
        if i < len(html_pages) - 1:
            body_content += '\n<div style="page-break-after: always;"></div>'
        bodies.append(body_content)

    combined = head_section + "\n<body>\n" + "\n".join(bodies) + "\n</body>\n</html>"
    return _html_to_pdf(combined)


# =============================================================================
# Carga de lotes (eager loading)
# =============================================================================

_EAGER_OPTS = lambda: [  # noqa: E731
    joinedload(Lote.sesion)
    .joinedload(SesionDescarga.provacop)
    .joinedload(ProveedorAcopiador.proveedor),
    joinedload(Lote.sesion)
    .joinedload(SesionDescarga.provacop)
    .joinedload(ProveedorAcopiador.acopiador),
    joinedload(Lote.pesajes),
]


def _cargar_lote(db: Session, sesion_id: int, lote_id: int) -> Lote:
    lote = (
        db.query(Lote)
        .options(*_EAGER_OPTS())
        .filter(Lote.id == lote_id, Lote.sesion_id == sesion_id, Lote.eliminado.is_(False))
        .first()
    )
    if not lote:
        raise ValueError(f"Lote {lote_id} no encontrado en sesión {sesion_id}")
    return lote


def _cargar_lotes_sesion(db: Session, sesion_id: int) -> list[Lote]:
    lotes = (
        db.query(Lote)
        .options(*_EAGER_OPTS())
        .filter(Lote.sesion_id == sesion_id, Lote.eliminado.is_(False))
        .order_by(Lote.numero_lote)
        .all()
    )
    if not lotes:
        raise ValueError(f"Sesión {sesion_id} no tiene lotes activos")
    return lotes


# =============================================================================
# API pública
# =============================================================================


def generar_ticket_pdf(db: Session, sesion_id: int, lote_id: int) -> bytes:
    """Genera el ticket PDF para un lote específico (RF-BAL-003)."""
    config = _get_config(db)
    lote = _cargar_lote(db, sesion_id, lote_id)
    data = _build_ticket_data(lote)
    html = _render_template(data, config)
    return _html_to_pdf(html)


def generar_tickets_sesion_pdf(db: Session, sesion_id: int) -> bytes:
    """
    Genera un único PDF con todos los tickets de la sesión,
    ordenados por número de lote. Para entregar al transportista.
    """
    config = _get_config(db)
    lotes = _cargar_lotes_sesion(db, sesion_id)
    html_pages = [_render_template(_build_ticket_data(lote), config) for lote in lotes]
    return _multi_html_to_pdf(html_pages)


def nombre_archivo_ticket(db: Session, lote_id: int) -> str:
    lote_ip = db.query(Lote.ip).filter(Lote.id == lote_id).scalar()
    return f"ticket-{lote_ip}.pdf" if lote_ip else f"ticket-lote-{lote_id}.pdf"


def nombre_archivo_sesion(sesion_id: int) -> str:
    return f"tickets-sesion-{sesion_id}.pdf"
