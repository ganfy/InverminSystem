"""
Permisos RBAC (desde seed.py):
  LABORATORIO VIEW   → Laboratorista, Comercial, Gerencia, Admin
  LABORATORIO CREATE → Laboratorista, Comercial, Admin
  LABORATORIO UPDATE → Comercial, Admin  (certificados, completar pendientes, enviar a recuperación)
  LABORATORIO DELETE → Comercial, Gerencia, Admin  (descartar)

Separación de vistas:
  GET /laboratorio/cips           → Laboratorista/todos (no incluye IP por defecto)
  GET /laboratorio/lotes          → Comercial+ (incluye IP, organizado por lote)
  GET /laboratorio/lotes/{ip}     → Comercial+ (detalle completo por lote)

Flujo de recuperación interna:
  POST /laboratorio/lotes/{ip}/enviar-recuperacion  → Comercial crea PENDIENTE con snapshot ley_cabeza
  PATCH /laboratorio/recuperacion/{id}/completar    → Laboratorista ingresa ley_cola + ley_liquido
"""

import io
import os
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

from app.core.database import get_db
from app.core.deps import check_permiso
from app.models.enums import EstadoRecuperacion, RolSistema, TipoAnalisis
from app.models.models import AnalisisLey, AnalisisRecuperacion, Lote, ParametrosComerciales
from app.schemas.laboratorio import (
    AnalisisAgCreate,
    AnalisisAgOut,
    AnalisisLeyCreate,
    AnalisisLeyOut,
    AnalisisLeyPorIPCreate,
    AnalisisRecuperacionCreate,
    AnalisisRecuperacionOut,
    CIPAnalisisOut,
    CompletarRecuperacionRequest,
    DescartarRequest,
    EnviarRecuperacionInternaRequest,
    LoteLabOut,
    SyncLaboratorioRequest,
    SyncLaboratorioResponse,
)
from app.services import certificado_ley_pdf as cert_svc
from app.services import laboratorio as svc
from app.services.pruebas import calcular_ley_planta
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi import UploadFile as FastAPIFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])

_ROLES_COMERCIAL = {
    RolSistema.ADMIN,
    RolSistema.GERENCIA,
    RolSistema.COMERCIAL,
    RolSistema.JEFE_COMERCIAL,
}


def _puede_ver_ip(current_user) -> bool:
    rol = current_user.rol.codigo if current_user.rol else None
    return rol in {r.value for r in _ROLES_COMERCIAL}


# ── Vista por CIP (Laboratorista y Comercial) ────────────────────────────────


@router.get("/cips", response_model=list[CIPAnalisisOut])
def listar_cips(
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Lista todos los CIPs con su estado de análisis.
    Laboratorista: no recibe IPs (confidencialidad muestreo ciego).
    Comercial/Gerencia/Admin: recibe lote_ip en cada CIP.
    CIPs de recuperación PENDIENTE aparecen destacados para laboratorista.
    """
    incluir_ip = _puede_ver_ip(current_user)
    return svc.obtener_cips_laboratorio(db, incluir_ip=incluir_ip)


# ── Registrar Análisis de Ley ────────────────────────────────────────────────


@router.post("/ley", response_model=AnalisisLeyOut, status_code=201)
def registrar_ley(
    datos: AnalisisLeyCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Registra un análisis de ley (Fire Assay triple sampling) para un CIP tipo Laboratorio.
    Accesible por Laboratorista y Comercial.
    """
    try:
        nuevo = svc.registrar_analisis_ley(db, datos, usuario_id=current_user.id)
        db.commit()
        lote = db.query(Lote).filter(Lote.id == nuevo.lote_id).first()
        ip = lote.ip if lote else None
        return svc._ley_out(nuevo, ip)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/ley/{analisis_id}/ag", response_model=AnalisisAgOut, status_code=201)
def registrar_ley_ag(
    analisis_id: int,
    datos: AnalisisAgCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Registra un análisis de ley de Plata (Ag) vinculado a un análisis Au existente.
    Calcula ley_ag_gr_tm = ((au_ag_mg - au_mg - 0.1444) * 1000) / peso_muestra
    Accesible por Laboratorista, Comercial y Admin.
    """
    try:
        resultado = svc.registrar_analisis_ag(db, analisis_id, datos, usuario_id=current_user.id)
        db.commit()
        return resultado
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/ley/{analisis_id}/descartar", response_model=AnalisisLeyOut)
def descartar_ley(
    analisis_id: int,
    datos: DescartarRequest,
    current_user=Depends(check_permiso("LABORATORIO", "DELETE")),
    db: Session = Depends(get_db),
):
    try:
        resultado = svc.descartar_analisis_ley(
            db, analisis_id, datos.justificacion, current_user.id
        )
        db.commit()
        return svc._ley_out(resultado)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/ley/{analisis_id}", status_code=204)
def eliminar_ley(
    analisis_id: int,
    current_user=Depends(check_permiso("LABORATORIO", "DELETE")),
    db: Session = Depends(get_db),
):
    """
    Soft delete de un analisis de ley.
    Lo oculta de todas las vistas (laboratorista y comercial) pero permanece en DB.
    Solo Admin, Gerencia y Comercial (permiso LABORATORIO DELETE).
    """
    try:
        svc.eliminar_analisis_ley(db, analisis_id, current_user.id)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/recuperacion/{analisis_id}", status_code=204)
def eliminar_recuperacion(
    analisis_id: int,
    current_user=Depends(check_permiso("LABORATORIO", "DELETE")),
    db: Session = Depends(get_db),
):
    """
    Soft delete de un analisis de recuperacion.
    Lo oculta de todas las vistas pero permanece en DB.
    Solo Admin, Gerencia y Comercial (permiso LABORATORIO DELETE).
    """
    try:
        svc.eliminar_analisis_recuperacion(db, analisis_id, current_user.id)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/ley/{analisis_id}/certificado")
async def subir_certificado_ley(
    analisis_id: int,
    archivo: UploadFile = File(...),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="ley")
        db.commit()
        return {"certificado_url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/ley/{analisis_id}/generar-certificado", response_model=AnalisisLeyOut)
def generar_certificado_ley_interno(
    analisis_id: int,
    descripcion: str | None = Query(None, description="Descripción para el PDF (e.g. LOTE)"),
    para_dest: str | None = Query("COMERCIAL", description="Destinatario: COMERCIAL o PLANTA"),
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    svc.generar_y_guardar_certificado_interno(
        db,
        analisis_id,
        "ley",
        descripcion_pdf=descripcion,
        para_dest=para_dest or "COMERCIAL",
    )
    db.commit()
    return svc._ley_out(db.query(AnalisisLey).get(analisis_id))


@router.post(
    "/recuperacion/{analisis_id}/generar-certificado", response_model=AnalisisRecuperacionOut
)
def generar_certificado_recuperacion_interno(
    analisis_id: int,
    descripcion: str | None = Query(None, description="Descripción para el PDF"),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    svc.generar_y_guardar_certificado_interno(
        db, analisis_id, "recuperacion", descripcion_pdf=descripcion
    )
    db.commit()
    return svc._rec_out(db.query(AnalisisRecuperacion).get(analisis_id))


# ── Flujo de recuperación interna ────────────────────────────────────────────


@router.post(
    "/lotes/{ip}/enviar-recuperacion",
    response_model=AnalisisRecuperacionOut,
    status_code=201,
    summary="Comercial crea registro PENDIENTE de recuperación para laboratorio interno",
)
def enviar_recuperacion_interna(
    ip: str,
    datos: EnviarRecuperacionInternaRequest = EnviarRecuperacionInternaRequest(),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Crea un análisis de recuperación en estado PENDIENTE.
    - Snapshot de ley_cabeza = ley planta calculada en este momento.
    - El laboratorista lo completa con ley_cola y ley_liquido.
    - Requiere que el lote tenga CIPs de RecuperacionInterno y análisis de ley vigentes.
    Solo Comercial/Gerencia/Admin.
    """
    try:
        nuevo = svc.enviar_recuperacion_interna(db, ip, datos, current_user.id)
        db.commit()
        lote = db.query(Lote).filter(Lote.id == nuevo.lote_id).first()
        ip_lote = lote.ip if lote else None
        return svc._rec_out(nuevo, ip_lote)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get(
    "/recuperacion/{analisis_id}",
    response_model=AnalisisRecuperacionOut,
    summary="Obtiene un análisis de recuperación por ID, incluyendo detalles (muestras)",
)
def obtener_recuperacion(
    analisis_id: int,
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    a = (
        db.query(AnalisisRecuperacion)
        .options(joinedload(AnalisisRecuperacion.detalles))
        .filter(AnalisisRecuperacion.id == analisis_id)
        .filter(~AnalisisRecuperacion.eliminado)
        .first()
    )
    if not a:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    return a


@router.patch(
    "/recuperacion/{analisis_id}/completar",
    response_model=AnalisisRecuperacionOut,
    summary="Laboratorista completa un análisis de recuperación PENDIENTE",
)
def completar_recuperacion(
    analisis_id: int,
    datos: CompletarRecuperacionRequest,
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Ingresa ley_cola y ley_liquido en un análisis PENDIENTE.
    La recuperación se calcula automáticamente.
    Accesible por Laboratorista, Comercial, Admin.
    """
    try:
        resultado = svc.completar_recuperacion(db, analisis_id, datos, current_user.id)
        db.commit()
        return svc._rec_out(resultado)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Registro directo de recuperación (flujo externo / sin pending) ────────────


@router.post("/recuperacion", response_model=AnalisisRecuperacionOut, status_code=201)
def registrar_recuperacion(
    datos: AnalisisRecuperacionCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Registro directo COMPLETADO de recuperación (sin pending previo).
    Usado para: certificados de laboratorio externo donde Comercial ingresa todos los datos.
    El CIP debe ser de tipo RecuperacionExterno o RecuperacionInterno.
    """
    try:
        nuevo = svc.registrar_analisis_recuperacion(db, datos, usuario_id=current_user.id)
        db.commit()
        lote = db.query(Lote).filter(Lote.id == nuevo.lote_id).first()
        ip = lote.ip if lote else None
        return svc._rec_out(nuevo, ip)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/recuperacion/{analisis_id}/descartar", response_model=AnalisisRecuperacionOut)
def descartar_recuperacion(
    analisis_id: int,
    datos: DescartarRequest,
    current_user=Depends(check_permiso("LABORATORIO", "DELETE")),
    db: Session = Depends(get_db),
):
    try:
        resultado = svc.descartar_analisis_recuperacion(
            db, analisis_id, datos.justificacion, current_user.id
        )
        db.commit()
        return svc._rec_out(resultado)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/recuperacion/{analisis_id}/certificado")
async def subir_certificado_recuperacion(
    analisis_id: int,
    archivo: UploadFile = File(...),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    try:
        url = svc.subir_certificado(db, analisis_id, archivo, tipo="recuperacion")
        db.commit()
        return {"certificado_url": url}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── OCR: extraer datos del certificado de ley ──────────────────────────────
@router.post("/certificado/extraer-ley")
async def extraer_certificado_ley(
    archivo: UploadFile = FastAPIFile(...),
    laboratorio: str = "",  # operador lo ingresa - no extraído del doc
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
):
    """
    OCR de certificado PDF/imagen de ley.
    El operador indica el laboratorio manualmente - la extracción es flexible
    y no depende del formato de un laboratorio específico.
    Devuelve campos pre-llenados para que el operador verifique/corrija.
    """
    contenido = await archivo.read()
    resultado = svc.extraer_certificado_ley(contenido, archivo.filename or "cert.pdf", laboratorio)
    return resultado


@router.post("/certificado/extraer-leyrecuperacion")
async def extraer_certificado_recuperacion(
    archivo: UploadFile = FastAPIFile(...),
    laboratorio: str = "",
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
):
    """
    OCR de certificado de recuperación (AAS u otro formato).
    laboratorio: ingresado por el operador.
    """
    contenido = await archivo.read()
    resultado = svc.extraer_certificado_recuperacion(
        contenido, archivo.filename or "cert.pdf", laboratorio
    )
    return resultado


# ── Ley comercial: preview del cálculo con parametros_comerciales ──────────
@router.get("/lotes/{ip}/ley-comercial")
def preview_ley_comercial(
    ip: str,
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Calcula y devuelve la ley comercial del lote aplicando las reglas
    de parametros_comerciales del proveedor-acopiador.
    Solo visible para Comercial, Gerencia, Admin (pueden ver IP).

    Desglose completo de leyes del lote:
        ley_planta_solo : solo lab propio (tipo 'planta')
        ley_externo     : labs externos (tipo 'externo')
        ley_comercial   : average(planta, externo) → factores aplicados
        ley_minero      : ley declarada por el minero
        ley_promedio    : (comercial + minero) / 2, o clamp con dirimencia
    """
    lote = db.query(Lote).filter(Lote.ip == ip, ~Lote.eliminado).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    ley_base = calcular_ley_planta(db, lote.id)
    if ley_base is None:
        # Fallback: si no hay análisis planta/externo vigentes, usar dirimencia (flujo legacy)
        ley_base = svc._ley_dirimencia(db, lote.id)
    if ley_base is None:
        raise HTTPException(
            status_code=422, detail="Sin análisis de ley vigentes para calcular ley planta"
        )

    try:
        provacop = lote.sesion.provacop
        params = db.query(ParametrosComerciales).filter_by(provacop_id=provacop.id).first()
    except AttributeError:
        params = None

    from app.services.config_calculo import get_constantes, get_quantize_decimal

    constantes = get_constantes(db)

    q_comercial = get_quantize_decimal(constantes.decimales_ley_comercial)
    q_final = get_quantize_decimal(constantes.decimales_ley_final)

    result = svc.calcular_ley_comercial(
        ley_base, params, umbral_volado=constantes.umbral_volado_oz_tc, q_comercial=q_comercial
    )

    ley_solo_planta = svc._ley_solo_planta(db, lote.id)
    ley_externo = svc._ley_solo_externo(db, lote.id)
    ley_minero = svc._ley_minero(db, lote.id)
    ley_dirimencia = svc._ley_dirimencia(db, lote.id)

    ley_comercial_dec = Decimal(str(result["ley_comercial"])).quantize(
        q_comercial, rounding=ROUND_DOWN
    )
    ley_promedio: Decimal | None = None

    if ley_minero is not None:
        if ley_dirimencia is not None:
            # Clamping
            ley_low = min(ley_comercial_dec, Decimal(str(ley_minero)))
            ley_high = max(ley_comercial_dec, Decimal(str(ley_minero)))
            ley_promedio = max(min(ley_dirimencia, ley_high), ley_low).quantize(
                q_final, rounding=ROUND_DOWN
            )
        else:
            ley_promedio = ((ley_comercial_dec + Decimal(str(ley_minero))) / 2).quantize(
                q_final, rounding=ROUND_DOWN
            )
    else:
        ley_promedio = ley_comercial_dec.quantize(q_final, rounding=ROUND_DOWN)

    result["ley_planta_solo"] = float(ley_solo_planta) if ley_solo_planta is not None else None
    result["ley_externo"] = float(ley_externo) if ley_externo is not None else None
    result["ley_minero"] = float(ley_minero) if ley_minero is not None else None
    result["ley_promedio"] = float(ley_promedio) if ley_promedio is not None else None
    result["tiene_dirimencia"] = ley_dirimencia is not None

    return result


@router.post(
    "/lotes/{ip}/ley",
    response_model=AnalisisLeyOut,
    status_code=201,
    summary="Registrar ley minero o dirimencia por IP (sin CIP obligatorio)",
)
def registrar_ley_por_ip(
    ip: str,
    datos: AnalisisLeyPorIPCreate,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """
    Usado por Comercial para:
    - Ingresar la ley declarada por el minero (tipo='minero')
    - Registrar resultado de dirimencia (tipo='dirimencia')
    Ambos pueden no tener CIP de planta. El lote se identifica por su IP.
    """
    try:
        nuevo = svc.registrar_ley_por_ip(db, ip, datos, usuario_id=current_user.id)
        db.commit()
        return svc._ley_out(nuevo, lote_ip=ip)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


# ── Generar certificado PDF (formato Paititi) ──────────────────────────────
@router.get("/lotes/{ip}/certificado-pdf")
def ver_certificado_ley_comercial(
    ip: str,
    inline: bool = True,
    columnas: list[str] = Query(None),
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Descarga o previsualiza (inline) el certificado comercial de ley (PDF).
    Solo Comercial, Gerencia, Admin.
    """
    from app.services import certificado_ley_pdf as cert_svc

    try:
        pdf_bytes = cert_svc.generar_certificado_ley_comercial_pdf(db, ip, columnas=columnas)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    nombre = f"certificado_ley_{ip.replace('-', '_')}.pdf"
    disposition = "inline" if inline else f'attachment; filename="{nombre}"'
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": disposition},
    )


@router.post("/lotes/{ip}/guardar-certificado-ley")
def guardar_certificado_ley(
    ip: str,
    columnas: list[str] = Query(None),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Genera y persiste el certificado de ley en storage. Retorna ruta relativa."""
    try:
        pdf_bytes = cert_svc.generar_certificado_ley_comercial_pdf(db, ip, columnas=columnas)
        ruta = cert_svc._guardar_cert_storage(pdf_bytes, ip, "ley")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    lote_obj = db.query(Lote).filter(Lote.ip == ip).first()
    if lote_obj:
        # Recalcular ley_comercial para persistirla (misma lógica que el PDF)
        ley_planta = calcular_ley_planta(db, lote_obj.id)
        if ley_planta is not None:
            try:
                provacop = lote_obj.sesion.provacop
                params = db.query(ParametrosComerciales).filter_by(provacop_id=provacop.id).first()
            except AttributeError:
                params = None
            calc = svc.calcular_ley_comercial(ley_planta, params)
            ley_comercial_val = Decimal(str(calc["ley_comercial"]))
            ley_gr_tm_val = (ley_comercial_val * Decimal("34.2857")).quantize(Decimal("0.001"))
            es_volado = calc["ley_comercial"] == 0.0
        else:
            ley_comercial_val = Decimal("0")
            ley_gr_tm_val = Decimal("0")
            es_volado = False

        cert_record = (
            db.query(AnalisisLey)
            .filter(
                AnalisisLey.lote_id == lote_obj.id,
                AnalisisLey.tipo_analisis == TipoAnalisis.COMERCIAL,
            )
            .first()
        )
        if cert_record:
            cert_record.certificado_url = ruta
            cert_record.ley_final = ley_comercial_val
            cert_record.ley_gr_tm = ley_gr_tm_val
        else:
            db.add(
                AnalisisLey(
                    lote_id=lote_obj.id,
                    laboratorio="Paititi",
                    tipo_analisis=TipoAnalisis.COMERCIAL,
                    material="Au",
                    ley_fino=Decimal("0"),
                    ley_grueso=Decimal("0"),
                    ley_final=ley_comercial_val,
                    ley_gr_tm=ley_gr_tm_val,
                    certificado_url=ruta,
                    vigente=True,
                    creado_por=current_user.id,
                )
            )

        # Marcar como volado si ley_comercial < UMBRAL_VOLADO (0.100 Oz/TC)
        if es_volado and not lote_obj.volado:
            lote_obj.volado = True

        # Marcar como volado si ley = 0
        db.commit()

    return {"ruta": ruta, "url": f"/laboratorio/archivos/{ruta}"}


@router.get("/lotes/{ip}/certificado-recuperacion-pdf")
def generar_certificado_recuperacion_pdf(
    ip: str,
    inline: bool = False,
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """
    Genera el PDF del certificado de recuperación (formato Paititi con marca de agua).
    ?inline=true → previsualización. Solo Comercial, Gerencia, Admin.
    """
    from app.services import certificado_ley_pdf as cert_svc

    try:
        pdf_bytes = cert_svc.generar_certificado_recuperacion_comercial_pdf(db, ip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    nombre = f"certificado_rec_{ip.replace('-', '_')}.pdf"
    disposition = "inline" if inline else f'attachment; filename="{nombre}"'
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": disposition},
    )


@router.post("/lotes/{ip}/guardar-certificado-recuperacion")
def guardar_certificado_recuperacion(
    ip: str,
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Genera y persiste el certificado de recuperación en storage."""
    try:
        pdf_bytes = cert_svc.generar_certificado_recuperacion_comercial_pdf(db, ip)
        ruta = cert_svc._guardar_cert_storage(pdf_bytes, ip, "rec")

        lote_obj = db.query(Lote).filter(Lote.ip == ip).first()
        if lote_obj:
            cert_record = (
                db.query(AnalisisRecuperacion)
                .filter(
                    AnalisisRecuperacion.lote_id == lote_obj.id,
                    AnalisisRecuperacion.estado == EstadoRecuperacion.CERT_COMERCIAL,
                )
                .first()
            )
            if cert_record:
                cert_record.certificado_url = ruta
            else:
                db.add(
                    AnalisisRecuperacion(
                        lote_id=lote_obj.id,
                        cip=None,
                        laboratorio="Paititi",
                        estado=EstadoRecuperacion.CERT_COMERCIAL,
                        certificado_url=ruta,
                        vigente=True,
                        creado_por=current_user.id,
                    )
                )
            db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"ruta": ruta, "url": f"/laboratorio/archivos/{ruta}"}


@router.post("/lotes/{ip}/guardar-certificado-reconocimiento")
def guardar_certificado_reconocimiento(
    ip: str,
    columnas: str = Query(None, description="Columnas separadas por comas"),
    current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
    db: Session = Depends(get_db),
):
    """Genera y persiste el certificado de reconocimiento en storage."""
    try:
        col_list = columnas.split(",") if columnas else None
        pdf_bytes = cert_svc.generar_cert_reconocimiento_cip_pdf(db, ip, columnas=col_list)
        ruta = cert_svc._guardar_cert_storage(pdf_bytes, ip, "reconocimiento")

        lote_obj = db.query(Lote).filter(Lote.ip == ip).first()
        if lote_obj:
            cert_record = (
                db.query(AnalisisRecuperacion)
                .filter(
                    AnalisisRecuperacion.lote_id == lote_obj.id,
                    AnalisisRecuperacion.estado == EstadoRecuperacion.CERT_RECONOCIMIENTO,
                )
                .first()
            )
            if cert_record:
                cert_record.certificado_url = ruta
            else:
                db.add(
                    AnalisisRecuperacion(
                        lote_id=lote_obj.id,
                        cip=None,
                        laboratorio="Paititi",
                        estado=EstadoRecuperacion.CERT_RECONOCIMIENTO,
                        certificado_url=ruta,
                        vigente=True,
                        creado_por=current_user.id,
                    )
                )
            db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"ruta": ruta, "url": f"/laboratorio/archivos/{ruta}"}


@router.get("/cips/{cip}/certificado-ensayo")
def generar_certificado_ensayo(
    cip: str,
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """
    Genera PDF de informe de ensayo Fire Assay para un CIP.
    Accesible por Laboratorista (VIEW). No expone IP ni datos del proveedor.
    """
    from app.services import certificado_ley_pdf as cert_svc

    try:
        pdf_bytes = cert_svc.generar_certificado_ensayo_cip_pdf(db, cip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    nombre = f"ensayo_{cip.replace('-', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.get("/cips/certificado-ensayo-conjunto")
def generar_certificado_ensayo_conjunto(
    cips: str = Query(..., description="CIPs separados por coma"),
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """Genera PDF de informe de ensayo consolidado para múltiples CIPs."""
    from app.services import certificado_ley_pdf as cert_svc

    cip_list = [c.strip() for c in cips.split(",")]
    if not cip_list:
        raise HTTPException(status_code=400, detail="Debe proveer al menos un CIP")

    try:
        pdf_bytes = cert_svc.generar_certificado_ensayo_conjunto_pdf(db, cip_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    nombre = "ensayos_consolidados.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.get("/cips/certificado-recuperacion-conjunto")
def generar_certificado_recuperacion_conjunto(
    cips: str = Query(..., description="CIPs separados por coma"),
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """Genera PDF de informe de recuperación consolidado para múltiples CIPs."""
    from app.services import certificado_ley_pdf as cert_svc

    cip_list = [c.strip() for c in cips.split(",")]
    if not cip_list:
        raise HTTPException(status_code=400, detail="Debe proveer al menos un CIP")

    try:
        pdf_bytes = cert_svc.generar_certificado_recuperacion_conjunto_pdf(db, cip_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    nombre = "recuperaciones_consolidadas.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.get("/ley/{analisis_id}/certificado")
def descargar_certificado_ley(
    analisis_id: int,
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """Descarga el certificado PDF de un análisis de ley guardado en disco."""
    analisis = db.query(AnalisisLey).get(analisis_id)
    if not analisis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    if not analisis.certificado_url or not os.path.exists(analisis.certificado_url):
        raise HTTPException(status_code=404, detail="Certificado no generado aún")

    def iterfile():
        with open(analisis.certificado_url, "rb") as f:
            yield from f

    nombre = f"Certificado_Ley_{analisis_id}.pdf"
    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.get("/recuperacion/{analisis_id}/certificado")
def descargar_certificado_recuperacion(
    analisis_id: int,
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """Descarga el certificado PDF de un análisis de recuperación guardado en disco."""
    analisis = db.query(AnalisisRecuperacion).get(analisis_id)
    if not analisis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    if not analisis.certificado_url or not os.path.exists(analisis.certificado_url):
        raise HTTPException(status_code=404, detail="Certificado no generado aún")

    def iterfile():
        with open(analisis.certificado_url, "rb") as f:
            yield from f

    nombre = f"Certificado_Rec_{analisis_id}.pdf"
    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


# Obtener certificado
@router.get("/archivos/{ruta_archivo:path}")
def descargar_archivo(
    ruta_archivo: str,
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
):
    """Sirve archivos del storage (certificados) con autenticación."""
    storage = Path(os.getenv("STORAGE_PATH", "storage"))
    ruta_completa = storage / ruta_archivo
    # Prevenir path traversal
    try:
        ruta_completa.resolve().relative_to(storage.resolve())
    except ValueError as e:
        raise HTTPException(status_code=403, detail="Acceso denegado") from e
    if not ruta_completa.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(ruta_completa)


# ── Vista por Lote/IP (solo Comercial, Gerencia, Admin) ──────────────────────


@router.get("/lotes", response_model=list[LoteLabOut])
def listar_lotes(
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """Lista lotes con análisis. Incluye ley_planta y ley_minero calculados. Solo Comercial+."""
    if not _puede_ver_ip(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo Comercial, Gerencia y Admin pueden acceder a la vista por IP",
        )
    return svc.obtener_lotes_laboratorio(db)


@router.get("/lotes/{ip}", response_model=LoteLabOut)
def detalle_lote(
    ip: str,
    material: str | None = Query(None, description="Filtrar análisis por material (Au, Ag)"),
    current_user=Depends(check_permiso("LABORATORIO", "VIEW")),
    db: Session = Depends(get_db),
):
    """Detalle completo de un lote: todos sus análisis, vigentes y descartados."""
    if not _puede_ver_ip(current_user):
        raise HTTPException(
            status_code=403,
            detail="Solo Comercial, Gerencia y Admin pueden acceder a la vista por IP",
        )
    result = svc.obtener_detalle_lote(db, ip, material=material)
    if not result:
        raise HTTPException(status_code=404, detail=f"Lote {ip} no encontrado o sin CIPs")
    return result


# ── Sync Offline ─────────────────────────────────────────────────────────────


@router.post("/sync", response_model=SyncLaboratorioResponse)
def sync_batch(
    payload: SyncLaboratorioRequest,
    current_user=Depends(check_permiso("LABORATORIO", "CREATE")),
    db: Session = Depends(get_db),
):
    """Sincroniza análisis registrados offline desde tablet de laboratorio."""
    return svc.sincronizar_batch(db, payload, current_user.id)
