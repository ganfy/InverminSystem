import sys
from pathlib import Path

sys.path.insert(0, str(Path("d:/Invermin/Development/code/InverminSystem/backend")))
from app.core.database import SessionLocal
from app.models.models import Lote
from app.services.liquidaciones import lotes_disponibles_para_liquidar

db = SessionLocal()
lote = db.query(Lote).order_by(Lote.id.desc()).first()
print(f"Lote: {lote.id}, provacop: {lote.sesion.provacop_id}")
print(f"Params: {lote.sesion.provacop.parametros}")
ldisp = lotes_disponibles_para_liquidar(db, lote.sesion.provacop_id)
print(f"Lotes disponibles len: {len(ldisp)}")
for ld in ldisp:
    print(ld["ip"], ld["listo_para_liquidar"], ld["ley_comercial"])
