"""
Service: Generacion del PDF de Liquidacion (RF-LIQ-004)
Motor: xhtml2pdf (pisa) - mismo que balanza_pdf.py y certificado_ley_pdf.py
"""

from __future__ import annotations

import base64
import io
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from app.models.models import (
    Liquidacion,
    LiquidacionLote,
    ParametrosComerciales,
    ProveedorAcopiador,
)
from sqlalchemy.orm import Session, joinedload


def _img_b64(filename: str) -> str:
    filepath = os.path.join(os.path.dirname(__file__), "..", "assets", filename)
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = filename.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{encoded}"


def _fmt_d(val, decimals: int = 2) -> str:
    if val is None:
        return "-"
    return f"{float(val):,.{decimals}f}"


def _fmt_date(d) -> str:
    if d is None:
        return "-"
    if isinstance(d, datetime):
        return d.strftime("%d/%m/%Y")
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    return str(d)


_TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "liquidacion.html"


def _build_fila(ll: LiquidacionLote) -> str:
    ip = ll.lote.ip if ll.lote else "-"
    return f"""
    <tr>
      <td>{ip}</td>
      <td>{_fmt_date(ll.fecha_recepcion_lote)}</td>
      <td>{_fmt_d(ll.tmh_snapshot, 3)}</td>
      <td>{_fmt_d(ll.humedad_snapshot, 2)}</td>
      <td>{_fmt_d(ll.tms_snapshot, 3)}</td>
      <td>{ll.sacos_snapshot or '-'}</td>
      <td>{_fmt_d(ll.oz_tc_promedio, 4)}</td>
      <td>{_fmt_d(ll.porcentaje_rec_liquido, 1)}</td>
      <td>{_fmt_d(ll.spot_usd_snapshot, 2)}</td>
      <td>{_fmt_d(ll.maquila_aplicada, 2)}</td>
      <td>{_fmt_d(ll.riesgo_aplicado, 2)}</td>
      <td>1.1023</td>
      <td>{_fmt_d(ll.insumos_liquidacion, 2)}</td>
      <td>{_fmt_d(ll.precio_x_tms, 4)}</td>
      <td><b>{_fmt_d(ll.total_usd, 2)}</b></td>
    </tr>"""


def _get_guias(liq: Liquidacion) -> tuple[str, str]:
    """Intenta obtener GRR/GRT de la sesion del primer lote."""
    try:
        sesion = liq.liquidacion_lotes[0].lote.sesion
        return (sesion.guia_remision or "-", sesion.guia_transporte or "-")
    except (IndexError, AttributeError):
        return "-", "-"


def _get_params(liq: Liquidacion) -> ParametrosComerciales | None:
    try:
        return liq.provacop.parametros
    except AttributeError:
        return None


def generar_liquidacion_pdf(db: Session, liquidacion_id: int) -> bytes:
    """Genera el PDF de liquidacion y retorna bytes."""
    liq = (
        db.query(Liquidacion)
        .options(
            joinedload(Liquidacion.provacop).joinedload(ProveedorAcopiador.proveedor),
            joinedload(Liquidacion.provacop).joinedload(ProveedorAcopiador.acopiador),
            joinedload(Liquidacion.provacop).joinedload(ProveedorAcopiador.parametros),
            joinedload(Liquidacion.liquidacion_lotes).joinedload(LiquidacionLote.lote),
        )
        .filter(Liquidacion.id == liquidacion_id)
        .first()
    )
    if not liq:
        raise ValueError(f"Liquidacion {liquidacion_id} no encontrada")

    prov = liq.provacop.proveedor if liq.provacop else None
    acop = liq.provacop.acopiador if liq.provacop else None
    params = _get_params(liq)

    # Datos de cabecera
    proveedor_rs = prov.razon_social if prov else "-"
    proveedor_ruc = prov.ruc if prov else "-"
    acopiador_nombre = acop.razon_social if acop else "-"

    # GRR/GRT del primer lote
    grr, grt = _get_guias(liq)

    # Fecha de entrega = fecha recepcion del primer lote
    fecha_entrega = "-"
    if liq.liquidacion_lotes:
        ll0 = liq.liquidacion_lotes[0]
        fecha_entrega = _fmt_date(ll0.fecha_recepcion_lote)

    # Notas de ley: lim_inferior y superior del proveedor
    lim_inf = _fmt_d(params.lim_ley_inferior, 3) if params and params.lim_ley_inferior else "0.040"
    lim_sup = _fmt_d(params.lim_ley_superior, 3) if params and params.lim_ley_superior else "0.099"

    # Filas de lotes
    filas = "".join(_build_fila(ll) for ll in liq.liquidacion_lotes)

    # Totales
    total_tms = sum((ll.tms_snapshot or Decimal("0")) for ll in liq.liquidacion_lotes)
    total_usd = liq.valor_total_usd or Decimal("0")

    # Imagenes
    logo_b64 = _img_b64("logo invermin.png")
    membrete_b64 = _img_b64("membrete invermin.png")
    membrete_tag = (
        f'<img src="{membrete_b64}" style="width:170px"/>'
        if membrete_b64
        else "<b>INVERMIN PAITITI S.A.C.</b>"
    )

    template = _TEMPLATE_PATH.read_text(encoding="utf-8")
    html = template.format(
        logo_b64=logo_b64,
        membrete_tag=membrete_tag,
        numero_liquidacion=liq.numero_liquidacion or "-",
        fecha_liquidacion=_fmt_date(liq.creado_en),
        proveedor_razon_social=proveedor_rs,
        proveedor_ruc=proveedor_ruc,
        acopiador_nombre=acopiador_nombre,
        fecha_entrega=fecha_entrega,
        guia_remision=grr,
        guia_transporte=grt,
        filas_lotes=filas,
        total_tms=_fmt_d(total_tms, 3),
        total_usd=_fmt_d(total_usd, 2),
        lim_ley_inferior=lim_inf,
        lim_ley_superior=lim_sup,
    )

    from xhtml2pdf import pisa

    buf = io.BytesIO()
    result = pisa.CreatePDF(io.StringIO(html), dest=buf, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"Error generando PDF de liquidacion: {result.err}")
    return buf.getvalue()


def guardar_pdf_liquidacion(db: Session, liquidacion_id: int, storage_path: str = "storage") -> str:
    """Genera y guarda el PDF en disco. Retorna la ruta relativa."""
    import os

    pdf_bytes = generar_liquidacion_pdf(db, liquidacion_id)
    directorio = os.path.join(storage_path, "liquidaciones")
    os.makedirs(directorio, exist_ok=True)
    nombre = f"LIQ-{liquidacion_id:06d}.pdf"
    ruta = os.path.join(directorio, nombre)
    with open(ruta, "wb") as f:
        f.write(pdf_bytes)
    return ruta
