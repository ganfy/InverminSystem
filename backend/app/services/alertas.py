"""
Router: Alertas — endpoint para guardar observaciones de operadores.

Las observaciones se almacenan en la tabla `configuraciones` con clave:
  obs_alerta:{tipo}:{ip}

Esto permite que Gerencia vea el contexto al revisar alertas, sin necesidad
de una tabla separada. Si en el futuro se requiere historial completo, se
puede migrar a una tabla dedicada.
"""

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Configuracion, Usuario
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter(prefix="/alertas", tags=["Alertas"])


class ObservacionRequest(BaseModel):
    tipo: str
    ip: str
    observacion: str


@router.post("/observacion")
def guardar_observacion(
    datos: ObservacionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Guarda una observación/justificación de un operador sobre una alerta."""
    clave = f"obs_alerta:{datos.tipo}:{datos.ip}"
    descripcion = f"Obs. {datos.tipo} {datos.ip} — por {current_user.nombre_completo}"

    row = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if row:
        # Acumular observaciones con timestamp
        from datetime import datetime

        nueva = (
            f"[{datetime.now():%Y-%m-%d %H:%M} {current_user.nombre_completo}] {datos.observacion}"
        )
        row.valor = f"{row.valor}\n{nueva}" if row.valor else nueva
    else:
        from datetime import datetime

        valor = (
            f"[{datetime.now():%Y-%m-%d %H:%M} {current_user.nombre_completo}] {datos.observacion}"
        )
        db.add(Configuracion(clave=clave, valor=valor, descripcion=descripcion))

    db.commit()
    return {"ok": True}


@router.get("/observaciones/{ip}")
def listar_observaciones_ip(
    ip: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna todas las observaciones de alertas para un IP dado."""
    rows = db.query(Configuracion).filter(Configuracion.clave.like(f"obs_alerta:%:{ip}")).all()
    return [{"clave": r.clave, "texto": r.valor, "descripcion": r.descripcion} for r in rows]
