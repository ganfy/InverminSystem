"""
Service - Generación de Ticket PDF (RF-BAL-003)

Motor: xhtml2pdf (pisa) - puro Python, sin dependencias nativas.
Instalar: pip install xhtml2pdf

Funciones públicas:
    generar_ticket_html(db, sesion_id, lote_id)    → str    (preview en pestaña)
    generar_ticket_pdf(db, sesion_id, lote_id)     → bytes  (descarga PDF)
    generar_tickets_sesion_pdf(db, sesion_id)      → bytes  (todos los lotes)
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

_CONFIG_DEFAULTS = {
    "empresa_nombre": "INVERMIN PAITITI S.A.C.",
    "empresa_planta": "Planta El Dorado",
    "empresa_ruc": "20601910587",
}


# =============================================================================
# Configuración desde BD
# =============================================================================


def _get_config(db: Session) -> dict[str, str]:
    rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(_CONFIG_DEFAULTS.keys()))
        .all()
    )
    return {**_CONFIG_DEFAULTS, **{r.clave: r.valor for r in rows}}


# =============================================================================
# DTO interno - campos 1:1 con el ticket físico
# =============================================================================


@dataclass
class _TicketData:
    numero_ticket: str  # ID numérico del pesaje: "7141"
    placa: str
    carreta: str
    conductor: str  # puede incluir DNI entre [] como en el ticket físico
    transportista: str
    razon_social: str  # empresa propietaria del mineral (con RUC entre [])
    proveedor_razon_social: str
    proveedor_ruc: str
    acopiador_razon_social: str
    mostrar_acopiador: bool
    tipo_material: str  # PRODUCTO
    documento: str  # guia_remision preferida, fallback guia_transporte
    observaciones: str  # "IP-3173 LOTE-1 GRANEL PERCY MENDOZA"
    fecha_inicio: str  # del pesaje: "18/02/2026  13:40:09"
    fecha_fin: str
    peso_bruto: str  # peso_inicial del pesaje
    peso_tara: str  # peso_final del pesaje
    peso_neto: str  # calculado por BD


# =============================================================================
# Helpers
# =============================================================================


def _fmt(valor: Decimal | None) -> str:
    return f"{valor:.3f}" if valor is not None else "-"


def _fecha_fmt(dt: datetime | None) -> str:
    return dt.strftime("%d/%m/%Y  %H:%M:%S") if dt else "-"


def _val(valor: str | None, fallback: str = "-") -> str:
    """Devuelve valor limpio o fallback - evita que queden {{ }} en el HTML."""
    if valor is None:
        return fallback
    v = valor.strip()
    return v if v else fallback


# =============================================================================
# Builder
# =============================================================================


def _build_ticket_data(lote: Lote) -> _TicketData:
    sesion: SesionDescarga = lote.sesion
    provacop: ProveedorAcopiador = sesion.provacop
    proveedor = provacop.proveedor
    acopiador = provacop.acopiador
    es_propio = provacop.proveedor_id == provacop.acopiador_id
    pesaje = lote.pesajes[0] if lote.pesajes else None

    # Documento: guia de remisión primero, si no guia de transporte
    documento = _val(sesion.guia_remision or sesion.guia_transporte)

    # Observaciones: "IP-3173 LOTE-1 GRANEL" (o "20 SACOS")
    if pesaje and pesaje.granel:
        cantidad = "GRANEL"
    elif pesaje and pesaje.sacos:
        cantidad = f"{pesaje.sacos} SACOS"
    else:
        cantidad = ""
    obs_parts = [f"{lote.ip}", f"LOTE-{lote.numero_lote}"]
    if cantidad:
        obs_parts.append(cantidad)
    observaciones = " ".join(obs_parts)

    return _TicketData(
        numero_ticket=str(pesaje.id) if pesaje else "-",
        placa=_val(sesion.placa),
        carreta=_val(sesion.carreta, "0"),
        conductor=_val(sesion.conductor),
        transportista=_val(sesion.transportista),
        razon_social=_val(sesion.razon_social),
        proveedor_razon_social=_val(proveedor.razon_social),
        proveedor_ruc=_val(proveedor.ruc),
        acopiador_razon_social=_val(acopiador.razon_social),
        mostrar_acopiador=not es_propio,
        tipo_material=_val(lote.tipo_material, "-").upper(),
        documento=documento,
        observaciones=observaciones,
        fecha_inicio=_fecha_fmt(pesaje.fecha_inicio if pesaje else None),
        fecha_fin=_fecha_fmt(pesaje.fecha_fin if pesaje else None),
        peso_bruto=_fmt(pesaje.peso_inicial if pesaje else None),
        peso_tara=_fmt(pesaje.peso_final if pesaje else None),
        peso_neto=_fmt(pesaje.peso_neto if pesaje else None),
    )


# =============================================================================
# Render
# =============================================================================


def _render_template(data: _TicketData, config: dict[str, str]) -> str:
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")

    # Bloque acopiador condicional
    marker_if = "{% if acopiador_html %}"
    marker_end = "{% endif %}"
    if not data.mostrar_acopiador:
        start = template.find(marker_if)
        end = template.find(marker_end, start) + len(marker_end)
        if start != -1 and end > len(marker_end):
            template = template[:start] + template[end:]
    else:
        template = template.replace(marker_if + "\n", "")
        template = template.replace(marker_end + "\n", "")

    replacements = {
        # Empresa
        "{{ empresa_nombre }}": config["empresa_nombre"],
        "{{ empresa_planta }}": config["empresa_planta"],
        "{{ empresa_ruc }}": config["empresa_ruc"],
        # Encabezado
        "{{ numero_ticket }}": data.numero_ticket,
        "{{ placa }}": data.placa,
        "{{ carreta }}": data.carreta,
        # Filas de datos
        "{{ conductor }}": data.conductor,
        "{{ transportista }}": data.transportista,
        "{{ razon_social }}": data.razon_social,
        "{{ tipo_material }}": data.tipo_material,
        "{{ documento }}": data.documento,
        "{{ observaciones }}": data.observaciones,
        "{{ acopiador_razon_social }}": data.acopiador_razon_social,
        # Pesos y fechas
        "{{ fecha_inicio }}": data.fecha_inicio,
        "{{ fecha_fin }}": data.fecha_fin,
        "{{ peso_bruto }}": data.peso_bruto,
        "{{ peso_tara }}": data.peso_tara,
        "{{ peso_neto }}": data.peso_neto,
    }
    for ph, val in replacements.items():
        template = template.replace(ph, val)

    return template


# =============================================================================
# Motor PDF
# =============================================================================


def _html_to_pdf(html: str) -> bytes:
    try:
        from xhtml2pdf import pisa  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError("Ejecutar: pip install xhtml2pdf") from exc

    buf = io.BytesIO()
    result = pisa.CreatePDF(io.StringIO(html), dest=buf, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"Error al generar PDF: {result.err}") from None
    return buf.getvalue()


def _multi_html_to_pdf(html_pages: list[str]) -> bytes:
    if not html_pages:
        raise ValueError("No hay páginas")
    if len(html_pages) == 1:
        return _html_to_pdf(html_pages[0])

    first = html_pages[0]
    head_end = first.find("</head>") + len("</head>")
    head = first[:head_end]
    bodies = []
    for i, page in enumerate(html_pages):
        b = page[page.find("<body>") + len("<body>") : page.find("</body>")].strip()
        if i < len(html_pages) - 1:
            b += '\n<div style="page-break-after: always;"></div>'
        bodies.append(b)

    combined = head + "\n<body>\n" + "\n".join(bodies) + "\n</body>\n</html>"
    return _html_to_pdf(combined)


# =============================================================================
# Carga de lotes
# =============================================================================


def _eager_opts():
    return [
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
        .options(*_eager_opts())
        .filter(Lote.id == lote_id, Lote.sesion_id == sesion_id, Lote.eliminado == 0)
        .first()
    )
    if not lote:
        raise ValueError(f"Lote {lote_id} no encontrado en sesión {sesion_id}")
    return lote


def _cargar_lotes_sesion(db: Session, sesion_id: int) -> list[Lote]:
    lotes = (
        db.query(Lote)
        .options(*_eager_opts())
        .filter(Lote.sesion_id == sesion_id, Lote.eliminado == 0)
        .order_by(Lote.numero_lote)
        .all()
    )
    if not lotes:
        raise ValueError(f"Sesión {sesion_id} sin lotes activos")
    return lotes


# =============================================================================
# API pública
# =============================================================================


def generar_ticket_html(db: Session, sesion_id: int, lote_id: int) -> str:
    """HTML del ticket para preview en pestaña del navegador."""
    config = _get_config(db)
    lote = _cargar_lote(db, sesion_id, lote_id)
    return _render_template(_build_ticket_data(lote), config)


def generar_ticket_pdf(db: Session, sesion_id: int, lote_id: int) -> bytes:
    """Ticket PDF para un lote específico."""
    config = _get_config(db)
    lote = _cargar_lote(db, sesion_id, lote_id)
    return _html_to_pdf(_render_template(_build_ticket_data(lote), config))


def generar_tickets_sesion_pdf(db: Session, sesion_id: int) -> bytes:
    """PDF único con todos los tickets de la sesión (un lote por página)."""
    config = _get_config(db)
    lotes = _cargar_lotes_sesion(db, sesion_id)
    return _multi_html_to_pdf(
        [_render_template(_build_ticket_data(lote), config) for lote in lotes]
    )


def nombre_archivo_ticket(db: Session, lote_id: int) -> str:
    ip = db.query(Lote.ip).filter(Lote.id == lote_id).scalar()
    return f"ticket-{ip}.pdf" if ip else f"ticket-lote-{lote_id}.pdf"


def nombre_archivo_sesion(sesion_id: int) -> str:
    return f"tickets-sesion-{sesion_id}.pdf"
