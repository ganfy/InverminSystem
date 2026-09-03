import os
import sys

sys.path.append(os.getcwd())
import traceback

from app.core.database import SessionLocal
from app.services.dashboard import obtener_resumen_dashboard

db = SessionLocal()
try:
    print("Testing todo")
    data = obtener_resumen_dashboard(db, filtro_estado="todo")
    print("TODO LOTES:", len(data.lotes))
except Exception:
    traceback.print_exc()

try:
    print("Testing stock")
    data = obtener_resumen_dashboard(db, filtro_estado="stock")
    print("STOCK LOTES:", len(data.lotes))
except Exception:
    traceback.print_exc()
