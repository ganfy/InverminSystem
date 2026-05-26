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
    "factor_oz_tc": "34.2857",  # Factor conversión Oz/TC → Gr/TM
    "umbral_volado_oz_tc": "0.100",  # Ley mínima; por debajo → lote volado
    "blank_correction_ag": "0.1444",  # Corrección en blanco para análisis Ag
}

DESCRIPCIONES: dict[str, str] = {
    "factor_oz_tc": "Factor de conversión Oz/TC a Gr/TM (1 Oz/TC = X Gr/TM)",
    "umbral_volado_oz_tc": "Ley mínima en Oz/TC; si la ley comercial es menor, el lote se marca como volado",
    "blank_correction_ag": "Corrección en blanco (mg) para el cálculo de ley de plata",
}


@dataclass
class ConstantesCalculo:
    factor_oz_tc: Decimal
    umbral_volado_oz_tc: Decimal
    blank_correction_ag: Decimal


def get_constantes(db: Session) -> ConstantesCalculo:
    """Carga las constantes de cálculo desde BD. Usa fallback si no existen."""
    rows = (
        db.query(Configuracion.clave, Configuracion.valor)
        .filter(Configuracion.clave.in_(DEFAULTS.keys()))
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
    """Actualiza o crea una constante de cálculo. Valida que sea numérica."""
    if clave not in DEFAULTS:
        raise ValueError(f"Constante '{clave}' no existe")
    try:
        Decimal(valor)
    except Exception as e:
        raise ValueError(f"Valor '{valor}' no es un número válido") from e

    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if row:
        row.valor = valor
    else:
        db.add(
            Configuracion(
                clave=clave,
                valor=valor,
                descripcion=DESCRIPCIONES.get(clave, ""),
            )
        )
    db.commit()
    return {"clave": clave, "valor": valor, "descripcion": DESCRIPCIONES.get(clave, "")}
