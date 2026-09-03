import os
import sys

sys.path.append(os.getcwd())
from app.db.session import SessionLocal
from app.models.models import Liquidacion, Lote, Ruma
from sqlalchemy.orm import joinedload

db = SessionLocal()
print("--- Estados Liquidacion ---")
for liq in db.query(Liquidacion).limit(10).all():
    print(f"Liquidacion ID: {liq.id}, Estado: {liq.estado}, Type of Estado: {type(liq.estado)}")

print("\n--- Lotes Liquidaciones ---")
lote = (
    db.query(Lote)
    .options(joinedload(Lote.liquidaciones_lotes))
    .filter(Lote.liquidaciones_lotes.any())
    .first()
)
if lote:
    print(f"Lote ID: {lote.id}")
    for ll in lote.liquidaciones_lotes:
        print(f" LL: {ll.liquidacion_id}, liq obj: {ll.liquidacion}")
else:
    print("No lotes with liquidaciones found")

print("\n--- Ruma Campaña ---")
ruma = db.query(Ruma).first()
if ruma:
    print(f'Ruma ID: {ruma.id}, campana_id: {getattr(ruma, "campana_id", None)}')
