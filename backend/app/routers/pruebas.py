# backend/app/routers/pruebas.py

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Usuario
from app.schemas.pruebas import (
    LotePruebaList,
    PruebaMetalurgicaCreate,
    SyncPruebasRequest,
    SyncPruebasResponse,
)
from app.services import pruebas as pruebas_service
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pruebas", tags=["Pruebas Metalúrgicas"])


@router.get("/lista", response_model=list[LotePruebaList])
def listar_pruebas(db: Session = Depends(get_db)):
    """
    Lista todos los lotes activos y su estado en las pruebas metalúrgicas.
    """
    return pruebas_service.obtener_lista_pruebas(db)


@router.post("/sync", response_model=SyncPruebasResponse)
def sync_pruebas_batch(
    request: SyncPruebasRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return pruebas_service.sync_batch(db, request.pruebas, current_user.id)


@router.post("/{ip}")
def registrar_prueba(
    ip: str,
    datos: PruebaMetalurgicaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        prueba, warning = pruebas_service.registrar_prueba(db, ip, datos, current_user.id)
        return {"data": prueba, "warning": warning}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
