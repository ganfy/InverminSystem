# from datetime import UTC, datetime

# from app.models import AnalisisLey, Lote
# from sqlalchemy.orm import Session

# from backend.app.schemas.laboratorio import DefinirLeyComercialRequest


# def definir_ley_comercial(
#     ip: str,
#     datos: DefinirLeyComercialRequest,
#     usuario_id: int,
#     db: Session,
# ) -> Lote:
#     lote = db.query(Lote).filter_by(ip=ip, eliminado=False).first()
#     if not lote:
#         raise ValueError(f"Lote {ip} no encontrado")

#     if datos.ley_manual is not None:
#         # Gerencia ingresa ley manualmente
#         ley_final = datos.ley_manual
#         metodo = "MANUAL"

#     elif datos.ids_analisis:
#         # Calcular promedio de los análisis seleccionados
#         analisis = (
#             db.query(AnalisisLey)
#             .filter(
#                 AnalisisLey.id.in_(datos.ids_analisis),
#                 AnalisisLey.lote_id == lote.id,
#             )
#             .all()
#         )

#         if len(analisis) != len(datos.ids_analisis):
#             raise ValueError("Uno o más análisis no pertenecen a este lote")

#         leyes = [a.ley_final for a in analisis if a.ley_final is not None]
#         if not leyes:
#             raise ValueError("Los análisis seleccionados no tienen ley calculada")

#         ley_final = sum(leyes) / len(leyes)

#         tipos = {a.tipo_analisis for a in analisis}
#         if "dirimencia" in tipos and len(analisis) == 1:
#             metodo = "DIRIMENCIA"
#         elif "dirimencia" in tipos:
#             metodo = "PROMEDIO_DIRIM_LAB"
#         else:
#             metodo = "PROMEDIO_LABS"
#     else:
#         raise ValueError("Debe proveer ids_analisis o ley_manual")

#     lote.ley_comercial_final = ley_final
#     lote.metodo_ley_final = metodo
#     lote.justificacion_ley = datos.justificacion
#     lote.ley_definida_por = usuario_id
#     lote.ley_definida_en = datetime.now(UTC)

#     db.commit()
#     db.refresh(lote)
#     return lote
