"""
Service: Generación del Certificado de Ley de Planta (formato Invermin Paititi)
Motor: xhtml2pdf (pisa) - igual que balanza_pdf.py

Flujo:
  Comercial aplica reglas de parametros_comerciales sobre ley_planta
  → sistema genera PDF "Informe de Ensayo" con ley_comercial resultante
  → se entrega al proveedor
"""

from __future__ import annotations

import io
from datetime import datetime

from app.models.models import (
    Lote,
    ParametrosComerciales,
    ProveedorAcopiador,
    SesionDescarga,
)
from app.services.laboratorio import calcular_ley_comercial
from app.services.pruebas import calcular_ley_planta
from sqlalchemy.orm import Session, joinedload

_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{ size: A4; margin: 20mm 18mm; }}
  body {{ font-family: Arial, sans-serif; font-size: 11px; color: #222; }}
  .logo-row {{ display: table; width: 100%; margin-bottom: 6px; }}
  .logo-cell {{ display: table-cell; vertical-align: middle; }}
  .empresa-nombre {{ font-size: 16px; font-weight: bold; color: #1a3c6b; }}
  .empresa-sub {{ font-size: 10px; color: #555; font-style: italic; }}
  .linea-gold {{ border: none; border-top: 3px solid #c8a84b; margin: 6px 0; }}
  .titulo-cert {{ text-align: center; font-size: 14px; font-weight: bold;
                  letter-spacing: 1px; margin: 10px 0 2px; }}
  .n-cert {{ text-align: center; color: #c8a84b; font-size: 11px;
             font-weight: bold; margin-bottom: 12px; }}
  .seccion {{ margin-bottom: 10px; }}
  .seccion-titulo {{ font-size: 10px; font-weight: bold; letter-spacing: .5px;
                     border-bottom: 1px solid #ccc; padding-bottom: 3px;
                     margin-bottom: 6px; text-transform: uppercase; }}
  .kv-row {{ display: table; width: 100%; margin-bottom: 4px; }}
  .kv-label {{ display: table-cell; width: 160px; color: #555; }}
  .kv-val {{ display: table-cell; font-weight: bold; }}
  table.detalle {{ width: 100%; border-collapse: collapse; margin-top: 6px; }}
  table.detalle th {{ background: #e8e0cc; font-size: 10px; padding: 5px 8px;
                      text-align: center; border: 1px solid #bbb; }}
  table.detalle td {{ padding: 5px 8px; border: 1px solid #ccc;
                      text-align: center; font-family: monospace; }}
  table.detalle td.codigo {{ text-align: left; font-family: Arial; }}
  .pie {{ font-size: 9px; color: #555; margin-top: 24px;
          border-top: 1px solid #ccc; padding-top: 6px; }}
</style>
</head>
<body>

<!-- CABECERA -->
<div class="logo-row">
  <div class="logo-cell">
    <div class="empresa-nombre">{empresa_nombre}</div>
    <div class="empresa-sub">{empresa_sub}</div>
  </div>
</div>
<hr class="linea-gold"/>

<div class="titulo-cert">INFORME DE ENSAYO</div>
<div class="n-cert">N&deg; LQ {n_lq}</div>

<!-- DATOS DEL CLIENTE -->
<div class="seccion">
  <div class="kv-row"><span class="kv-label">Cliente</span><span class="kv-val">: {cliente}</span></div>
  <div class="kv-row"><span class="kv-label">Referencia</span><span class="kv-val">: {referencia}</span></div>
  <div class="kv-row"><span class="kv-label">Solicitud de Ensayo</span><span class="kv-val">: Analisis por Au</span></div>
</div>

<hr class="linea-gold"/>

<!-- RECEPCIÓN DE MUESTRAS -->
<div class="seccion">
  <div class="seccion-titulo">Recepción de Muestras</div>
  <div class="kv-row"><span class="kv-label">Cantidad</span><span class="kv-val">: 1</span></div>
  <div class="kv-row"><span class="kv-label">Descripción</span><span class="kv-val">: Polveado</span></div>
  <div class="kv-row"><span class="kv-label">Envase</span><span class="kv-val">: Bolsa de plastico</span></div>
  <div class="kv-row"><span class="kv-label">Fecha de Recepcion</span><span class="kv-val">: {fecha_recepcion}</span></div>
  <div class="kv-row"><span class="kv-label">Termino de Analisis</span><span class="kv-val">: {fecha_termino}</span></div>
  <div class="kv-row"><span class="kv-label">Metodo de Ensayo</span><span class="kv-val">: Newmont</span></div>
</div>

<hr class="linea-gold"/>

<!-- DETALLE -->
<div class="seccion">
  <div class="seccion-titulo">Detalle del Informe</div>
  <table class="detalle">
    <thead>
      <tr>
        <th>N&deg;</th>
        <th>CODIGO</th>
        <th>Ley Au Oz/Tc</th>
        <th>Descuento/Ajuste</th>
        <th>Ley Comercial Oz/Tc</th>
      </tr>
    </thead>
    <tbody>
      {filas_detalle}
    </tbody>
  </table>
</div>

{bloque_notas}

<!-- PIE -->
<div class="pie">
  Los resultados obtenidos y que se consigna en el presente informe corresponde FIRE ASSAY
  o analisis gravimetrico en las muestras recepcionadas por el cliente.<br/>
  <strong>{empresa_nombre}</strong><br/>
  {empresa_direccion}
</div>

</body>
</html>
"""


def _fmt_oz(v: float | None) -> str:
    if v is None:
        return "-"
    return f"{v:.4f}"


def _fmt_date(dt: datetime | None) -> str:
    if not dt:
        return "-"
    return dt.strftime("%d-%m-%y")


def _n_lq(lote_id: int, extra: str = "") -> str:
    """Genera número de informe: LQ {año}{mes}{dia}-{lote_id:04d}"""
    hoy = datetime.now()
    base = f"{hoy.strftime('%y%m%d')}-{lote_id:04d}"
    return f"{base}{extra}"


def generar_certificado_ley_comercial_pdf(db: Session, ip_lote: str) -> bytes:
    """
    Genera el PDF de certificado de ley comercial (formato Paititi) para un lote.
    Aplica las reglas de parametros_comerciales del proveedor-acopiador.
    Retorna bytes del PDF listo para descarga.
    """
    from app.models.models import Configuracion

    lote = (
        db.query(Lote)
        .options(
            joinedload(Lote.sesion)
            .joinedload(SesionDescarga.provacop)
            .joinedload(ProveedorAcopiador.proveedor),
            joinedload(Lote.mapeo_cip),
        )
        .filter(Lote.ip == ip_lote, ~Lote.eliminado)
        .first()
    )
    if not lote:
        raise ValueError(f"Lote {ip_lote} no encontrado")

    # Config empresa
    cfg_rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(["empresa_nombre", "empresa_planta", "empresa_direccion"]))
        .all()
    )
    cfg = {r.clave: r.valor for r in cfg_rows}
    empresa_nombre = cfg.get("empresa_nombre", "INVERMIN PAITITI S.A.C.")
    empresa_sub = cfg.get("empresa_planta", "Inversiones Mineras con Responsabilidad Social")
    empresa_dir = cfg.get(
        "empresa_direccion",
        "Otr.Las Terrazas KM.2 Otr. Quebrada El Totoral - Chala - Caraveli - Arequipa",
    )

    # Proveedor / cliente
    try:
        proveedor = lote.sesion.provacop.proveedor
        cliente_nombre = proveedor.razon_social or "-"
        referencia = proveedor.referencia or f"IP-{lote.ip}"
    except AttributeError:
        cliente_nombre = "-"
        referencia = lote.ip

    # Fecha recepcion del lote
    pesaje = lote.pesajes[0] if lote.pesajes else None
    fecha_recepcion = _fmt_date(pesaje.fecha_fin if pesaje else None)

    # Ley planta calculada
    ley_planta = calcular_ley_planta(db, lote.id)
    if ley_planta is None:
        raise ValueError("El lote no tiene análisis de ley vigentes para calcular ley planta")

    # Parámetros comerciales
    provacop = lote.sesion.provacop
    params = (
        db.query(ParametrosComerciales)
        .filter(ParametrosComerciales.provacop_id == provacop.id)
        .first()
    )

    calc = calcular_ley_comercial(ley_planta, params)
    ley_comercial = calc["ley_comercial"]
    descuento = calc["descuento_aplicado"]
    factor = calc["factor_aplicado"]

    # Descripcion del ajuste para la celda de tabla
    if calc["sin_parametros"]:
        ajuste_str = "Sin parametros"
    elif descuento or factor != 1.0 or calc["ajuste_rango"]:
        partes = []
        if descuento:
            partes.append(f"Dscto -{descuento:.4f}")
        if calc["ajuste_rango"]:
            partes.append("Ajuste rango")
        if factor != 1.0:
            partes.append(f"x{factor:.3f}")
        ajuste_str = " | ".join(partes) if partes else "-"
    else:
        ajuste_str = "Sin ajuste"

    fila = (
        f"<tr>"
        f"<td>1</td>"
        f'<td class="codigo">{ip_lote}</td>'
        f"<td>{_fmt_oz(float(ley_planta))}</td>"
        f"<td>{ajuste_str}</td>"
        f"<td><strong>{_fmt_oz(ley_comercial)}</strong></td>"
        f"</tr>"
    )

    # Notas si hubo descarte / dirimencia
    notas = ""
    if lote.dirimencia:
        notas = '<div style="font-size:9px;color:#666;margin-top:8px;">* Ley determinada por análisis de dirimencia.</div>'

    html = _TEMPLATE.format(
        empresa_nombre=empresa_nombre,
        empresa_sub=empresa_sub,
        empresa_direccion=empresa_dir,
        n_lq=_n_lq(lote.id),
        cliente=cliente_nombre,
        referencia=referencia,
        fecha_recepcion=fecha_recepcion,
        fecha_termino=_fmt_date(datetime.now()),
        filas_detalle=fila,
        bloque_notas=notas,
    )

    return _html_to_pdf(html)


def _html_to_pdf(html: str) -> bytes:
    try:
        from xhtml2pdf import pisa
    except ImportError as e:
        raise RuntimeError("Ejecutar: pip install xhtml2pdf") from e
    buf = io.BytesIO()
    result = pisa.CreatePDF(io.StringIO(html), dest=buf, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"Error al generar PDF: {result.err}")
    return buf.getvalue()
