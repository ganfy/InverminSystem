"""
config_calculo.py — Constantes de cálculo metalúrgico configurables.

Las constantes se leen desde la tabla `configuraciones`.
Si no existen en BD, se usan los valores por defecto (fallback).
Solo Admin y Gerencia pueden modificarlas vía /api/v1/admin/config-calculo.
"""

from dataclasses import dataclass
from decimal import Decimal

from app.models.models import Configuracion
from sqlalchemy.orm import Session

# ── Valores por defecto (fallback si no están en BD) ─────────────────────────
DEFAULTS: dict[str, str] = {
    # Constantes originales
    "factor_oz_tc": "34.2857",  # Factor conversión Oz/TC → Gr/TM
    "umbral_volado_oz_tc": "0.100",  # Ley mínima; por debajo → lote volado
    "blank_correction_ag": "0.1444",  # Corrección en blanco para análisis Ag
    # Unidades por módulo
    "unidad_balanza": "TM",
    "unidad_muestreo": "TM",
    "unidad_laboratorio": "KG",
    "unidad_liquidaciones": "TMC",
    "unidad_default": "TM",
    # Muestreo
    "MUESTREO_MAX_INTENTOS": "3",
    "MUESTREO_HUMEDAD_MAX_PCT": "50",
    "MUESTREO_MALLA_MIN_PCT": "88",
    "MUESTREO_MALLA_MAX_PCT": "94",
    "MAX_CIPS_GENERADOS": "5",
    "labs_lista": '["Minares South S.R.L.", "El Dorado - Invermin Paititi", "Quantum", "Otro"]',
    # Laboratorio
    "LAB_DIFERENCIA_MAX_PCT": "5",
    "LAB_DIFERENCIA_PLANTA_MINERO": "0.10",
    # Campaña / Planta / Empresa
    "empresa_nombre": "INVERMIN PAITITI S.A.C.",
    "empresa_planta": "Planta El Dorado",
    "empresa_ruc": "20601910587",
    "empresa_direccion": "Av. Principal 123, Lima",
    "CAMPANA_META_ORO_FINO_DEFAULT": "5000",
    # Pruebas Metalúrgicas / SLA
    "sla_metalurgia_horas": "48",
    "sla_limite_plazo_horas": "72",
    # Alertas Dashboard
    "alerta_horas_pesado_muestreo": "24",
    "alerta_horas_muestreo_ley": "24",
    "alerta_horas_ley_recuperacion": "72",
    "alerta_dias_volado_stock": "30",
}

DESCRIPCIONES: dict[str, str] = {
    "factor_oz_tc": "Factor de conversión Oz/TC a Gr/TM (1 Oz/TC = X Gr/TM)",
    "umbral_volado_oz_tc": "Ley mínima en Oz/TC; si la ley comercial es menor, el lote se marca como volado",
    "blank_correction_ag": "Corrección en blanco (mg) para el cálculo de ley de plata",
    "unidad_balanza": "Unidad de peso para el módulo de Balanza (TM, TMC, KG)",
    "unidad_muestreo": "Unidad de peso para el módulo de Muestreo (TM, TMC, KG)",
    "unidad_laboratorio": "Unidad de peso para el módulo de Laboratorio (TM, TMC, KG)",
    "unidad_liquidaciones": "Unidad de peso para el módulo de Liquidaciones (TM, TMC, KG)",
    "unidad_default": "Unidad de peso por defecto en el sistema (TM, TMC, KG)",
    "MUESTREO_MAX_INTENTOS": "Máximo de intentos de muestreo permitidos por lote",
    "MUESTREO_HUMEDAD_MAX_PCT": "Porcentaje de humedad máximo antes de generar un error",
    "MUESTREO_MALLA_MIN_PCT": "Porcentaje de malla mínimo aceptable para muestreo",
    "MUESTREO_MALLA_MAX_PCT": "Porcentaje de malla máximo aceptable para muestreo",
    "MAX_CIPS_GENERADOS": "Cantidad máxima de códigos CIP que se pueden generar por lote",
    "labs_lista": "Lista de laboratorios externos disponibles para asignar a CIPs (formato JSON)",
    "LAB_DIFERENCIA_MAX_PCT": "Diferencia porcentual máxima permitida entre laboratorios antes de alertar",
    "LAB_DIFERENCIA_PLANTA_MINERO": "Diferencia máxima de ley (Au) entre planta y minero antes de ir a dirimencia",
    "empresa_nombre": "Razón social / Nombre de la empresa para documentos y reportes",
    "empresa_planta": "Nombre de la planta/sede operativa",
    "empresa_ruc": "RUC de la empresa",
    "empresa_direccion": "Dirección fiscal o física de la empresa",
    "CAMPANA_META_ORO_FINO_DEFAULT": "Meta predeterminada de oro fino en gramos por campaña",
    "sla_metalurgia_horas": "Tiempo de espera en horas para considerar una prueba metalúrgica como retrasada",
    "sla_limite_plazo_horas": "Plazo máximo en horas para completar una prueba antes de alertar de incumplimiento",
    "alerta_horas_pesado_muestreo": "Horas máximas entre pesado en balanza y muestreo antes de generar alerta",
    "alerta_horas_muestreo_ley": "Horas máximas entre muestreo y resultado de ley antes de generar alerta",
    "alerta_horas_ley_recuperacion": "Horas máximas entre resultado de ley y recuperación antes de generar alerta",
    "alerta_dias_volado_stock": "Días máximos permitidos para lotes volados en stock antes de generar alerta",
}


@dataclass
class ConstantesCalculo:
    factor_oz_tc: Decimal
    umbral_volado_oz_tc: Decimal
    blank_correction_ag: Decimal


def get_constantes(db: Session) -> ConstantesCalculo:
    """Carga las constantes de cálculo desde BD. Usa fallback si no existen."""
    keys = ["factor_oz_tc", "umbral_volado_oz_tc", "blank_correction_ag"]
    rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(keys))
        .all()
    )
    cfg = {**DEFAULTS, **{r.clave: r.valor for r in rows}}
    return ConstantesCalculo(
        factor_oz_tc=Decimal(cfg["factor_oz_tc"]),
        umbral_volado_oz_tc=Decimal(cfg["umbral_volado_oz_tc"]),
        blank_correction_ag=Decimal(cfg["blank_correction_ag"]),
    )


def listar_constantes(db: Session) -> list[dict]:
    """Retorna lista de constantes con su valor actual y descripción."""
    rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(DEFAULTS.keys()))
        .all()
    )
    en_db = {r.clave: r.valor for r in rows}
    return [
        {
            "clave": clave,
            "valor": en_db.get(clave, default),
            "default": default,
            "descripcion": DESCRIPCIONES.get(clave, ""),
            "en_bd": clave in en_db,
        }
        for clave, default in DEFAULTS.items()
    ]


def actualizar_constante(db: Session, clave: str, valor: str) -> dict:
    """Actualiza o crea una constante de configuración. Valida el tipo de valor."""
    if clave not in DEFAULTS:
        raise ValueError(f"Configuración '{clave}' no existe")

    # Validación por tipo de clave
    val = valor.strip()
    if clave.startswith("unidad_"):
        if val not in ("TM", "TMC", "KG"):
            raise ValueError(f"Unidad '{val}' inválida. Debe ser TM, TMC o KG.")
    elif clave == "labs_lista":
        import json

        try:
            parsed = json.loads(val)
            if not isinstance(parsed, list):
                raise ValueError()
        except Exception as e:
            raise ValueError(
                'labs_lista debe ser un arreglo JSON válido (ej: ["Lab1", "Lab2"])'
            ) from e
    elif clave in ("empresa_nombre", "empresa_planta", "empresa_ruc", "empresa_direccion"):
        if not val:
            raise ValueError(f"El campo '{clave}' no puede estar vacío.")
    else:
        # Por defecto, todas las demás son numéricas (constantes, alertas, metas, etc.)
        try:
            Decimal(val)
        except Exception as e:
            raise ValueError(f"El valor para '{clave}' debe ser un número válido.") from e

    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if row:
        row.valor = val
    else:
        db.add(
            Configuracion(
                clave=clave,
                valor=val,
                descripcion=DESCRIPCIONES.get(clave, ""),
            )
        )
    db.commit()
    return {"clave": clave, "valor": val, "descripcion": DESCRIPCIONES.get(clave, "")}


def get_config_public_dict(db: Session) -> dict[str, str]:
    """Retorna las configuraciones públicas no sensibles (unidades, datos de empresa, etc.) desde la BD."""
    claves_publicas = [
        "unidad_balanza",
        "unidad_muestreo",
        "unidad_laboratorio",
        "unidad_liquidaciones",
        "unidad_default",
        "empresa_nombre",
        "empresa_planta",
        "empresa_ruc",
        "empresa_direccion",
        "factor_oz_tc",
    ]
    rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(claves_publicas))
        .all()
    )
    en_db = {r.clave: r.valor for r in rows}
    return {clave: en_db.get(clave, DEFAULTS[clave]) for clave in claves_publicas}
