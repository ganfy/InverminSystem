# from app.core.database import get_db
# from app.core.deps import check_permiso
# from app.schemas.laboratorio import DefinirLeyComercialRequest
# from app.services import laboratorio as svc
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# router = APIRouter(prefix="/laboratorio", tags=["Laboratorio"])


# @router.post("/lotes/{ip}/ley-comercial")
# def definir_ley_comercial(
#     ip: str,
#     datos: DefinirLeyComercialRequest,
#     # Solo Gerencia, Comercial y Admin pueden hacer esto
#     current_user=Depends(check_permiso("LABORATORIO", "UPDATE")),
#     db: Session = Depends(get_db),
# ):
#     try:
#         lote = svc.definir_ley_comercial(ip, datos, current_user.id, db)
#         return {
#             "ip": lote.ip,
#             "ley_comercial_final": lote.ley_comercial_final,
#             "metodo": lote.metodo_ley_final,
#             "definida_por": current_user.nombre_completo,
#             "definida_en": lote.ley_definida_en,
#         }
#     except ValueError as e:
#         raise HTTPException(400,  detail=str(e)) from e
