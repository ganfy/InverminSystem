"""
Service — Generación de Ticket PDF (RF-BAL-003)

Responsabilidad única: recibir datos del lote y producir bytes PDF.
El template HTML vive en app/templates/ticket_balanza.html.
El motor de renderizado es WeasyPrint (declarado en pyproject.toml).

Uso desde el router:
    pdf_bytes = generar_ticket_pdf(db, sesion_id=1, lote_id=42)
    return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf")
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.models.models import Lote, ProveedorAcopiador, SesionDescarga
from sqlalchemy.orm import Session, joinedload

# Ruta al template — relativa al paquete app/
_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "ticket_balanza.html"


# =============================================================================
# DTO interno — datos planos para renderizar el template
# =============================================================================


@dataclass
class _TicketData:
    """Datos planos para renderizar ticket_balanza.html."""

    ip: str
    numero_lote: int
    numero_ticket: str
    estado: str
    tipo_material: str
    # Proveedor / Acopiador
    proveedor_razon_social: str
    proveedor_ruc: str
    acopiador_razon_social: str
    mostrar_acopiador: bool  # False cuando es_propio
    # Transporte
    placa: str
    conductor: str
    guia_remision: str
    guia_transporte: str
    # Pesaje
    sacos: str
    granel: str
    peso_bruto: str  # formateado: "21.500"
    peso_tara: str
    peso_neto: str
    # Fecha
    fecha_ingreso: str


def _fmt(valor: Decimal | None) -> str:
    """Formatea un Decimal a 3 decimales, o '-' si es None."""
    return f"{valor:.3f}" if valor is not None else "-"


def _fecha_fmt(dt: datetime | None) -> str:
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "-"


def _str(valor: str | None) -> str:
    return valor.strip() if valor else "-"


def _build_ticket_data(lote: Lote) -> _TicketData:
    """Extrae y normaliza los datos del lote ORM hacia el DTO."""
    sesion: SesionDescarga = lote.sesion
    provacop: ProveedorAcopiador = sesion.provacop
    proveedor = provacop.proveedor
    acopiador = provacop.acopiador
    es_propio = provacop.proveedor_id == provacop.acopiador_id
    pesaje = lote.pesajes[0] if lote.pesajes else None

    return _TicketData(
        ip=lote.ip,
        numero_lote=lote.numero_lote,
        numero_ticket=pesaje.numero_ticket if pesaje else "-",
        estado=lote.estado,
        tipo_material=_str(lote.tipo_material),
        proveedor_razon_social=proveedor.razon_social,
        proveedor_ruc=_str(proveedor.ruc),
        acopiador_razon_social=acopiador.razon_social,
        mostrar_acopiador=not es_propio,
        placa=sesion.placa,
        conductor=_str(sesion.conductor),
        guia_remision=_str(sesion.guia_remision),
        guia_transporte=_str(sesion.guia_transporte),
        sacos=str(pesaje.sacos) if pesaje and pesaje.sacos else "-",
        granel="Sí" if pesaje and pesaje.granel else "No",
        peso_bruto=_fmt(pesaje.peso_final if pesaje else None),
        peso_tara=_fmt(pesaje.peso_inicial if pesaje else None),
        peso_neto=_fmt(pesaje.peso_neto if pesaje else None),
        fecha_ingreso=_fecha_fmt(sesion.creado_en),
    )


def _render_template(data: _TicketData) -> str:
    """
    Renderiza ticket_balanza.html con sustitución simple de variables.
    Usamos str.replace en lugar de Jinja2 para no agregar dependencias.
    El template usa {{ variable }} como marcadores.
    """
    template = _TEMPLATE_PATH.read_text(encoding="utf-8")

    # Bloque de acopiador — mostrar o vaciar según es_propio
    acopiador_block_marker = "{% if acopiador_html %}"
    acopiador_end_marker = "{% endif %}"
    if not data.mostrar_acopiador:
        # Eliminar el bloque completo (incluye las líneas de control)
        start = template.find(acopiador_block_marker)
        end = template.find(acopiador_end_marker, start) + len(acopiador_end_marker)
        if start != -1 and end != -1:
            template = template[:start] + template[end:]
    else:
        # Quitar solo las líneas de control, mantener el contenido
        template = template.replace(acopiador_block_marker + "\n", "")
        template = template.replace(acopiador_end_marker + "\n", "")

    replacements = {
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


def _html_to_pdf(html: str) -> bytes:
    """Convierte HTML a PDF usando WeasyPrint."""
    try:
        from weasyprint import HTML

        return HTML(string=html).write_pdf()
    except ImportError as exc:
        raise RuntimeError(
            "WeasyPrint no está instalado. "
            "Agregar 'weasyprint' a pyproject.toml y ejecutar: uv sync"
        ) from exc


# =============================================================================
# API pública del módulo
# =============================================================================


def generar_ticket_pdf(db: Session, sesion_id: int, lote_id: int) -> bytes:
    """
    Genera el ticket PDF para un lote específico (RF-BAL-003).

    Args:
        db:        Sesión de base de datos.
        sesion_id: ID de la sesión de descarga.
        lote_id:   ID del lote dentro de la sesión.

    Returns:
        bytes: PDF listo para StreamingResponse.

    Raises:
        ValueError:  Si el lote no existe en la sesión indicada.
        RuntimeError: Si WeasyPrint no está instalado.
    """
    lote = (
        db.query(Lote)
        .options(
            joinedload(Lote.sesion)
            .joinedload(SesionDescarga.provacop)
            .joinedload(ProveedorAcopiador.proveedor),
            joinedload(Lote.sesion)
            .joinedload(SesionDescarga.provacop)
            .joinedload(ProveedorAcopiador.acopiador),
            joinedload(Lote.pesajes),
        )
        .filter(Lote.id == lote_id, Lote.sesion_id == sesion_id)
        .first()
    )
    if not lote:
        raise ValueError(f"Lote {lote_id} no encontrado en sesión {sesion_id}")

    data = _build_ticket_data(lote)
    html = _render_template(data)
    return _html_to_pdf(html)


def nombre_archivo_ticket(db: Session, lote_id: int) -> str:
    """Retorna el nombre de archivo sugerido para la descarga: 'ticket-IP-0042.pdf'."""
    lote = db.query(Lote.ip).filter(Lote.id == lote_id).scalar()
    return f"ticket-{lote}.pdf" if lote else f"ticket-lote-{lote_id}.pdf"
