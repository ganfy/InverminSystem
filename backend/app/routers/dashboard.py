from app.core.deps import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import obtener_resumen_dashboard
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumen", response_model=DashboardResponse)
def get_dashboard_resumen(db: Session = Depends(get_db)):
    """
    Obtiene las métricas y la lista de lotes recientes para la vista principal del Dashboard.
    """
    return obtener_resumen_dashboard(db)
