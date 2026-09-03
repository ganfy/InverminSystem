import os
import sys

sys.path.append(os.getcwd())
from app.core.database import SessionLocal
from app.models.models import Campana
from app.services.dashboard import obtener_resumen_dashboard

db = SessionLocal()
campanas = db.query(Campana).all()
for c in campanas:
    data = obtener_resumen_dashboard(db, filtro_estado=f"campana_{c.codigo}")
    print(f"Campana {c.codigo}: {len(data.lotes)} lotes")
