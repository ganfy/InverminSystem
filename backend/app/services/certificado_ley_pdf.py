"""
Service: Generación del Certificado de Ley de Planta (formato Invermin Paititi)
Motor: xhtml2pdf (pisa) - igual que balanza_pdf.py

Flujo:
  Comercial aplica reglas de parametros_comerciales sobre ley_planta
  → sistema genera PDF "Informe de Ensayo" con ley_comercial resultante
  → se entrega al proveedor
"""

from __future__ import annotations

import base64
import os
from datetime import datetime

from app.models.models import (
    Lote,
    ParametrosComerciales,
    ProveedorAcopiador,
    SesionDescarga,
    Usuario,
)
from app.services.laboratorio import calcular_ley_comercial
from app.services.pruebas import calcular_ley_planta
from sqlalchemy.orm import Session, joinedload


def _get_image_b64(filename: str) -> str:
    """Convierte una imagen local a Base64 para incrustarla sin problemas de rutas en el PDF."""
    filepath = os.path.join(os.path.dirname(__file__), "..", "assets", filename)
    if not os.path.exists(filepath):
        return ""

    with open(filepath, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
        ext = filename.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        return f"data:{mime};base64,{encoded}"


# -- TEMPLATE PARA CERTIFICADO DE LEY COMERCIAL (CLIENTE) --
_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{
      size: A4;
      margin: 20mm 18mm;
      background-image: url('{membrete_b64}');
      background-size: cover;
  }}
  body {{ font-family: Arial, sans-serif; font-size: 11px; color: #222; }}

  .watermark-pattern {{
      position: fixed;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      z-index: -50;

      /*
         1. linear-gradient es una capa blanca al 95% de opacidad (rgba = 0.95).
         2. url() es la capa de tu logo que va debajo de esa capa blanca. */
      background-image:
          linear-gradient(rgba(255, 255, 255, 0.50), rgba(255, 255, 255, 0.50)),
          url('{logo_b64}');

      background-repeat: repeat;
      background-size: 100px;         /* TAMAÑO DEL LOGO: baja este número para hacerlos más chiquitos (ej. 80px) */
      background-position: center;
      transform: rotate(-30deg);      /* Inclinación */
  }}

  .logo-header {{ width: 140px; margin-bottom: 10px; }}
  .empresa-nombre {{ font-size: 16px; font-weight: bold; color: #c8a84b; }}
  .empresa-sub {{ font-size: 10px; color: #555; font-style: italic; }}
  .linea-gold {{ border: none; border-top: 3px solid #c8a84b; margin: 8px 0; }}
  .titulo-cert {{ text-align: center; font-size: 14px; font-weight: bold; letter-spacing: 1px; margin: 10px 0 2px; }}
  .n-cert {{ text-align: center; color: #c8a84b; font-size: 11px; font-weight: bold; margin-bottom: 12px; }}
  .seccion {{ margin-bottom: 10px; }}
  .kv-row {{ display: table; width: 100%; margin-bottom: 4px; }}
  .kv-label {{ display: table-cell; width: 160px; color: #555; }}
  .kv-val {{ display: table-cell; font-weight: bold; }}

  table.detalle {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
  table.detalle th {{ background: #e8e0cc; font-size: 10px; padding: 6px; border: 1px solid #bbb; }}
  table.detalle td {{ padding: 8px; border: 1px solid #ccc; text-align: center; font-family: monospace; font-size: 12px; }}

  .firma-bloque {{ margin-top: 60px; text-align: center; }}
  .firma-linea {{ display: inline-block; width: 220px; border-top: 1px solid #333; padding-top: 4px; font-weight: bold; font-size: 10px; }}
  .pie {{ font-size: 9px; color: #555; margin-top: 30px; border-top: 1px solid #ccc; padding-top: 8px; }}
</style>
</head>
<body>

<div class="watermark-pattern"></div>

<div class="logo-row">
  <img src="{logo_b64}" class="logo-header" />
  <div class="empresa-nombre">{empresa_nombre}</div>
  <div class="empresa-sub">{empresa_sub}</div>
</div>
<hr class="linea-gold"/>

<div class="titulo-cert">INFORME DE ENSAYO</div>
<div class="n-cert">N&deg; LQ {n_lq}</div>

<div class="seccion">
  <div class="kv-row"><span class="kv-label">Cliente</span><span class="kv-val">: {cliente}</span></div>
  <div class="kv-row"><span class="kv-label">Referencia</span><span class="kv-val">: {referencia}</span></div>
  <div class="kv-row"><span class="kv-label">Solicitud de Ensayo</span><span class="kv-val">: Análisis por Au</span></div>
</div>
<hr class="linea-gold"/>
<div class="seccion">
  <div class="kv-row"><span class="kv-label">Fecha de Recepcion</span><span class="kv-val">: {fecha_recepcion}</span></div>
  <div class="kv-row"><span class="kv-label">Termino de Analisis</span><span class="kv-val">: {fecha_termino}</span></div>
</div>

<table class="detalle">
  <thead><tr><th>N&deg;</th><th>CÓDIGO</th><th>Ley Au Oz/Tc</th></tr></thead>
  <tbody>{filas_detalle}</tbody>
</table>

{bloque_notas}

<div class="firma-bloque">
  <span class="firma-linea">{analista}<br/>Responsable de Laboratorio</span>
</div>

<div class="pie">
    Los resultados obtenidos corresponden a FIRE ASSAY (análisis gravimétrico).<br/>
    <strong>{empresa_nombre}</strong> - {empresa_direccion}
</div>

</body>
</html>
"""

# -- TEMPLATE PARA INFORME DE RECUPERACIÓN --
_TEMPLATE_RECUPERACION = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{ size: A4; margin: 20mm 18mm; background-image: url('{membrete_b64}'); }}
  body {{ font-family: Arial, sans-serif; font-size: 11px; color: #222; }}
  .watermark {{ position: absolute; top: 30%; left: 15%; width: 70%; opacity: 0.08; z-index: -1; }}
  .logo-header {{ width: 140px; margin-bottom: 8px; }}
  .empresa-nombre {{ font-size: 16px; font-weight: bold; color: #c8a84b; }}
  .linea-gold {{ border: none; border-top: 3px solid #c8a84b; margin: 6px 0; }}
  .titulo-cert {{ text-align: center; font-size: 14px; font-weight: bold; margin: 15px 0; }}
  table.detalle {{ width: 100%; border-collapse: collapse; }}
  table.detalle th {{ background: #e8e0cc; padding: 6px; border: 1px solid #bbb; }}
  table.detalle td {{ padding: 6px; border: 1px solid #ccc; text-align: center; font-family: monospace; }}
  .firma-bloque {{ margin-top: 60px; text-align: center; }}
  .firma-linea {{ display: inline-block; width: 220px; border-top: 1px solid #333; padding-top: 4px; font-weight: bold; }}
</style>
</head>
<body>
<img src="{logo_b64}" class="watermark" />
<img src="{logo_b64}" class="logo-header" />
<div class="empresa-nombre">{empresa_nombre}</div>
<hr class="linea-gold"/>
<div class="titulo-cert">INFORME DE RECUPERACIÓN</div>
<div class="kv-row"><strong>CIP:</strong> {n_ensayo} | <strong>Laboratorio:</strong> {laboratorio} | <strong>Fecha:</strong> {fecha}</div>
<table class="detalle" style="margin-top:20px">
  <thead><tr><th>N°</th><th>CIP</th><th>Ley Cabeza</th><th>Ley Cola</th><th>Ley Líquido</th><th>% Rec.</th></tr></thead>
  <tbody>{filas_detalle}</tbody>
</table>
<div class="firma-bloque">
  <span class="firma-linea">{analista}<br/>Analista Responsable</span>
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
    from app.models.models import AnalisisLey, Configuracion, Usuario

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

    analista_nombre = "CONTROL DE CALIDAD"  # Valor por defecto
    ultimo_analisis = (
        db.query(AnalisisLey)
        .filter(AnalisisLey.lote_id == lote.id, AnalisisLey.vigente)
        .order_by(AnalisisLey.id.desc())
        .first()
    )
    if ultimo_analisis and ultimo_analisis.creado_por:
        user = db.query(Usuario).get(ultimo_analisis.creado_por)
        if user:
            analista_nombre = user.nombre_completo

    # CARGAR IMÁGENES
    logo_b64 = _get_image_b64("logo invermin.png")
    membrete_b64 = _get_image_b64("membrete invermin.png")

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

    fila = (
        f"<tr>"
        f"<td>1</td>"
        f'<td class="codigo">{ip_lote}</td>'
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
        logo_b64=logo_b64,
        membrete_b64=membrete_b64,
        analista=analista_nombre,
    )

    return _html_to_pdf(html)


_TEMPLATE_ENSAYO = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{ size: A4; margin: 20mm 18mm; }}
  body {{ font-family: Arial, sans-serif; font-size: 10px; color: #222; background-color: #ffffff; }}
  .cab {{ display: table; width: 100%; margin-bottom: 5px; }}
  .cab-left {{ display: table-cell; vertical-align: middle; }}
  .cab-right {{ display: table-cell; text-align: right; vertical-align: middle; font-size: 9px; color: #555; }}
  .logo-header {{ width: 110px; margin-bottom: 5px; }}
  .lab-titulo {{ font-size: 13px; font-weight: bold; color: #c8a84b; }}
  .lab-sub {{ font-size: 9px; color: #777; }}
  .linea-gold {{ border: none; border-top: 2px solid #c8a84b; margin: 5px 0; }}
  .titulo-cert {{ text-align: center; font-size: 12px; font-weight: bold; margin: 10px 0; }}
  table.det {{ width: 100%; border-collapse: collapse; font-size: 9.5px; }}
  table.det th {{ background: #e8e0cc; padding: 4px; border: 1px solid #bbb; }}
  table.det td {{ padding: 4px; border: 1px solid #ddd; text-align: center; font-family: monospace; }}
  .firma-bloque {{ margin-top: 50px; text-align: center; }}
  .firma-linea {{ display: inline-block; width: 180px; border-top: 1px solid #333; padding-top: 4px; font-weight: bold; }}
</style>
</head>
<body>
<div class="cab">
  <div class="cab-left">
    <img src="{logo_b64}" class="logo-header" />
    <div class="lab-titulo">{empresa_nombre}</div>
    <div class="lab-sub">{empresa_sub}</div>
  </div>
  <div class="cab-right">{empresa_direccion}</div>
</div>
<hr class="linea-gold"/>

<div class="titulo-cert">CERTIFICADO DE ENSAYO - NEWMONT - PROCESO - Au</div>
<div class="n-cert">N&deg;{n_ensayo}</div>

<!-- METADATOS -->
<div class="meta-grid">
  <div class="meta-row">
    <span class="meta-label">Fecha Ingreso:</span><span class="meta-val">{fecha_ingreso}</span>
  </div>
  <div class="meta-row">
    <span class="meta-label">Fecha Entrega:</span><span class="meta-val">{fecha_entrega}</span>
  </div>
  <div class="meta-row">
    <span class="meta-label">PARA:</span><span class="meta-val">PLANTA</span>
  </div>
  <div class="meta-row">
    <span class="meta-label">Solicitud de ensayo:</span><span class="meta-val">Análisis de sólidos por Au y Ag</span>
  </div>
  <div class="meta-row">
    <span class="meta-label">Recepción de muestras:</span><span class="meta-val">Mineral de 0.5 Kg aproximado</span>
  </div>
  <div class="meta-row">
    <span class="meta-label">Descripción:</span><span class="meta-val">PROCESO</span>
  </div>
  <div class="meta-row">
    <span class="meta-label">Tipo de análisis:</span><span class="meta-val">Fire Assay - Gravimétrico</span>
  </div>
  <div class="meta-row">
    <span class="meta-label">Laboratorio:</span><span class="meta-val">{laboratorio}</span>
  </div>
</div>

<hr class="linea-gold"/>

<!-- ANÁLISIS POR ORO (Au) -->
<div class="seccion-titulo">ANÁLISIS POR ORO</div>
<table class="det">
  <thead>
    <tr>
      <th rowspan="2">ITEM</th>
      <th rowspan="2">CÓDIGO</th>
      <th colspan="2">LEY Oz/Tc</th>
      <th rowspan="2">Au Oz/Tc</th>
      <th rowspan="2">LEY Au Gr/TM</th>
    </tr>
    <tr>
      <th>+140</th>
      <th>-140</th>
    </tr>
  </thead>
  <tbody>{filas_au}</tbody>
</table>

{bloque_ag}

<!-- TOTALES / PIE -->
<div class="meta-grid" style="margin-top:10px">
  <div class="meta-row">
    <span class="meta-label">Total muestras analizadas:</span>
    <span class="meta-val">{total_muestras}</span>
  </div>
</div>

<div class="firma-bloque">
  <span class="firma-linea">Reportado por<br/>{reportado_por}<br/></span>
  <span class="firma-linea">Analista<br/>{analista}</span>
</div>

<div class="pie">
  Los resultados obtenidos y consignados en el presente informe corresponden a análisis
  FIRE ASSAY (gravimétrico) en las muestras recepcionadas.<br/>
  <strong>{empresa_nombre}</strong> &mdash; {empresa_direccion}
</div>

</body>
</html>
"""


def generar_certificado_ensayo_cip_pdf(db: Session, cip_code: str) -> bytes:
    """Certificado de ensayo Fire Assay para laboratorista (por CIP, sin revelar IP)."""
    from app.models.models import AnalisisLey, Configuracion, MapeoCIP

    cip = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == cip_code).first()
    if not cip:
        raise ValueError(f"CIP {cip_code} no encontrado")

    analisis_list = (
        db.query(AnalisisLey)
        .filter(AnalisisLey.cip == cip_code, AnalisisLey.vigente == True)  # noqa: E712
        .order_by(AnalisisLey.id)
        .all()
    )
    if not analisis_list:
        raise ValueError(f"No hay análisis de ley vigentes para CIP {cip_code}")

    analista_nombre = ""
    primer_analisis = analisis_list[0]
    if primer_analisis.creado_por:
        usuario = db.query(Usuario).filter(Usuario.id == primer_analisis.creado_por).first()
        if usuario:
            analista_nombre = usuario.nombre_completo

    cfg_rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(["empresa_nombre", "empresa_planta", "empresa_direccion"]))
        .all()
    )
    cfg = {r.clave: r.valor for r in cfg_rows}
    empresa_nombre = cfg.get("empresa_nombre", "INVERMIN PAITITI S.A.C.")
    empresa_sub = cfg.get("empresa_planta", "Inversiones Mineras con Responsabilidad Social")
    empresa_dir = cfg.get(
        "empresa_direccion", "Otr.Las Terrazas KM.2 - Chala - Caraveli - Arequipa"
    )

    # Filas Au: +140 = ley_grueso, -140 = ley_fino (convención del Excel de planta)
    filas_au = ""
    for i, a in enumerate(analisis_list, 1):
        filas_au += (
            f"<tr>"
            f"<td>{i}</td>"
            f"<td style='font-family:monospace;color:#b8860b'>{cip_code}</td>"
            f"<td>{_fmt_oz(float(a.ley_grueso) if a.ley_grueso else None)}</td>"
            f"<td>{_fmt_oz(float(a.ley_fino) if a.ley_fino else None)}</td>"
            f"<td><strong>{_fmt_oz(float(a.ley_final) if a.ley_final else None)}</strong></td>"
            f"<td>{_fmt_oz(float(a.ley_gr_tm) if a.ley_gr_tm else None)}</td>"
            f"</tr>"
        )

    # Bloque Ag: solo si hay análisis con ley_gr_tm (proxy de que hay dato Ag registrado)
    # Por ahora se omite si no hay datos de Ag — la sección queda reservada para futuro
    bloque_ag = ""

    fecha_analisis = analisis_list[-1].fecha_analisis
    hoy = datetime.now()
    fecha_ingreso = _fmt_date(
        datetime.combine(fecha_analisis, datetime.min.time()) if fecha_analisis else None
    )
    fecha_entrega = hoy.strftime("%d-%m-%y")

    logo_b64 = _get_image_b64("logo invermin.png")
    membrete_b64 = _get_image_b64("membrete invermin.png")

    html = _TEMPLATE_ENSAYO.format(
        empresa_nombre=empresa_nombre,
        empresa_sub=empresa_sub,
        empresa_direccion=empresa_dir,
        n_ensayo=cip_code,
        laboratorio=analisis_list[0].laboratorio if analisis_list else "-",
        fecha_ingreso=fecha_ingreso,
        fecha_entrega=fecha_entrega,
        filas_au=filas_au,
        bloque_ag=bloque_ag,
        total_muestras=len(analisis_list),
        reportado_por=analista_nombre,  # <-- Inyectando el nombre
        analista=analista_nombre,  # <-- Inyectando el nombre
        logo_b64=logo_b64,  # <-- Imagen de Logo
        membrete_b64=membrete_b64,
    )
    return _html_to_pdf(html)


_TEMPLATE_RECUPERACION = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  @page {{ size: A4; margin: 20mm 18mm; }}
  body {{ font-family: Arial, sans-serif; font-size: 11px; color: #222; }}
  .empresa-nombre {{ font-size: 16px; font-weight: bold; color: #c8a84b; }}
  .empresa-sub {{ font-size: 10px; color: #555; font-style: italic; }}
  .linea-gold {{ border: none; border-top: 3px solid #c8a84b; margin: 6px 0; }}
  .titulo-cert {{ text-align: center; font-size: 14px; font-weight: bold; margin: 10px 0 2px; }}
  .n-cert {{ text-align: center; color: #c8a84b; font-size: 11px; font-weight: bold; margin-bottom: 12px; }}
  .kv-row {{ display: table; width: 100%; margin-bottom: 4px; }}
  .kv-label {{ display: table-cell; width: 160px; color: #555; }}
  .kv-val {{ display: table-cell; font-weight: bold; }}
  table.detalle {{ width: 100%; border-collapse: collapse; margin-top: 6px; }}
  table.detalle th {{ background: #e8e0cc; font-size: 10px; padding: 5px 8px; border: 1px solid #bbb; }}
  table.detalle td {{ padding: 5px 8px; border: 1px solid #ccc; text-align: center; font-family: monospace; }}
  .pie {{ font-size: 9px; color: #555; margin-top: 24px; border-top: 1px solid #ccc; padding-top: 6px; }}
</style>
</head>
<body>
<div><div class="empresa-nombre">{empresa_nombre}</div><div class="empresa-sub">{empresa_sub}</div></div>
<hr class="linea-gold"/>
<div class="titulo-cert">INFORME DE RECUPERACIÓN</div>
<div class="n-cert">CIP: {n_ensayo}</div>
<div class="kv-row"><span class="kv-label">Laboratorio</span><span class="kv-val">: {laboratorio}</span></div>
<div class="kv-row"><span class="kv-label">Fecha análisis</span><span class="kv-val">: {fecha}</span></div>
<hr class="linea-gold"/>
<table class="detalle">
  <thead>
    <tr><th>N°</th><th>CIP</th><th>Ley Cabeza</th><th>Ley Cola</th><th>Ley Líquido</th><th>% Recuperación</th></tr>
  </thead>
  <tbody>{filas_detalle}</tbody>
</table>
<div class="pie">
<br/>
  <strong>{empresa_nombre}</strong> &mdash; {empresa_direccion}
</div>
</body>
</html>
"""


def generar_certificado_recuperacion_cip_pdf(db: Session, cip_code: str) -> bytes:
    from app.models.models import AnalisisRecuperacion, Configuracion, MapeoCIP

    cip = db.query(MapeoCIP).filter(MapeoCIP.codigo_cip == cip_code).first()
    if not cip:
        raise ValueError(f"CIP {cip_code} no encontrado")

    analista_nombre = "DEPARTAMENTO TÉCNICO"

    analisis_list = (
        db.query(AnalisisRecuperacion)
        .filter(AnalisisRecuperacion.cip == cip_code, AnalisisRecuperacion.vigente)
        .order_by(AnalisisRecuperacion.id)
        .all()
    )
    if analisis_list and analisis_list[0].creado_por:
        usuario = db.query(Usuario).filter(Usuario.id == analisis_list[0].creado_por).first()
        if usuario:
            analista_nombre = usuario.nombre_completo

    if not analisis_list:
        raise ValueError(f"No hay análisis vigentes para CIP {cip_code}")

    cfg_rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(["empresa_nombre", "empresa_planta", "empresa_direccion"]))
        .all()
    )
    cfg = {r.clave: r.valor for r in cfg_rows}

    filas = ""
    for i, a in enumerate(analisis_list, 1):
        filas += (
            f"<tr><td>{i}</td><td>{cip_code}</td>"
            f"<td>{_fmt_oz(float(a.ley_cabeza) if a.ley_cabeza is not None else None)}</td>"
            f"<td>{_fmt_oz(float(a.ley_cola) if a.ley_cola is not None else None)}</td>"
            f"<td>{_fmt_oz(float(a.ley_liquido) if a.ley_liquido is not None else None)}</td>"
            f"<td><strong>{float(a.recuperacion):.2f}%</strong></td></tr>"
        )

    fecha_analisis = analisis_list[-1].fecha_analisis
    fecha = _fmt_date(
        datetime.combine(fecha_analisis, datetime.min.time()) if fecha_analisis else None
    )

    html = _TEMPLATE_RECUPERACION.format(
        empresa_nombre=cfg.get("empresa_nombre", "INVERMIN PAITITI S.A.C."),
        empresa_sub=cfg.get("empresa_planta", "Inversiones Mineras con Responsabilidad Social"),
        empresa_direccion=cfg.get("empresa_direccion", ""),
        n_ensayo=cip_code,
        laboratorio=analisis_list[0].laboratorio or "-",
        fecha=fecha,
        filas_detalle=filas,
        analista_nombre=analista_nombre,
    )
    return _html_to_pdf(html)


def _html_to_pdf(html: str) -> bytes:
    try:
        from weasyprint import HTML
    except ImportError as e:
        raise RuntimeError("Ejecutar: pip install weasyprint (o instalar GTK en Windows)") from e

    return HTML(string=html).write_pdf()
