# from decimal import Decimal

# from pydantic import BaseModel


# class DefinirLeyComercialRequest(BaseModel):
#     """
#     Payload para que Gerencia/Comercial defina la ley comercial final.
#     ids_analisis: lista de IDs de analisis_ley a promediar.
#     Si viene solo 1 ID de tipo dirimencia → metodo=DIRIMENCIA.
#     Si vienen 2+ IDs → el sistema promedia y el usuario elige el metodo.
#     Si viene ley_manual → metodo=MANUAL, se ignoran ids_analisis.
#     """

#     ids_analisis: list[int] | None = None  # IDs a promediar
#     ley_manual: Decimal | None = None  # Override manual
#     justificacion: str  # Obligatoria siempre
