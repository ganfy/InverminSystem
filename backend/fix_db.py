from app.models.database import SessionLocal
from app.models.models import AnalisisRecuperacion


def fix_db():
    db = SessionLocal()
    try:
        # Get all records where ley_cabeza == 0 and set them to None
        records = db.query(AnalisisRecuperacion).filter(AnalisisRecuperacion.ley_cabeza == 0).all()
        for r in records:
            r.ley_cabeza = None
        db.commit()
        print(f"Fixed {len(records)} records.")
    finally:
        db.close()


if __name__ == "__main__":
    fix_db()
