from app.core.deps import get_db
from app.schemas.dashboard import AlertasConfig, AlertasResponse, DashboardResponse
from app.services.dashboard import (
    actualizar_config_alertas,
    generar_excel_dashboard,
    obtener_alertas,
    obtener_resumen_dashboard,
)
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class ExportarPayload(BaseModel):
    tipo: str = Field(
        "lotes",
        pattern="^(lotes|acopiadores)$",
        description="Tipo de datos a exportar: 'lotes' o 'acopiadores'",
    )
    clave: str = Field(..., min_length=4, description="Contraseña para proteger el archivo Excel")


@router.get("/resumen", response_model=DashboardResponse)
def get_dashboard_resumen(db: Session = Depends(get_db)):
    return obtener_resumen_dashboard(db)


@router.post("/exportar")
def exportar_excel(
    payload: ExportarPayload,
    db: Session = Depends(get_db),
):
    data = obtener_resumen_dashboard(db)
    buf = generar_excel_dashboard(data, tipo=payload.tipo, clave=payload.clave)
    nombre = f"{'lotes' if payload.tipo == 'lotes' else 'acopiadores'}_paititi.xlsx"
    return Response(
        content=buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nombre}"},
    )


@router.get("/alertas", response_model=AlertasResponse)
def get_alertas(db: Session = Depends(get_db)):
    """Obtiene las alertas activas según la configuración actual."""
    return obtener_alertas(db)


@router.put("/alertas/config", response_model=AlertasConfig)
def update_alertas_config(config: AlertasConfig, db: Session = Depends(get_db)):
    """Actualiza la configuración de alertas."""
    actualizar_config_alertas(db, config)
    return config
