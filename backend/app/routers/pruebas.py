# backend/app/routers/pruebas.py

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Usuario
from app.schemas.pruebas import (
    LotePruebaList,
    PruebaMetalurgicaCreate,
    PruebaMetalurgicaOut,
    SyncPruebasRequest,
    SyncPruebasResponse,
)
from app.services import pruebas as pruebas_service
from fastapi import APIRouter, Depends, HTTPException, status
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


@router.get(
    "/lotes/{ip_lote}", response_model=PruebaMetalurgicaOut
)  # Ajusta el response_model al tuyo
def obtener_detalle_prueba(ip_lote: str, db: Session = Depends(get_db)):
    prueba = pruebas_service.obtener_prueba_por_ip(db, ip_lote)
    if not prueba:
        # Devolvemos un 404 para que el Frontend sepa que está vacío y es una prueba NUEVA
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prueba no iniciada")
    return prueba
