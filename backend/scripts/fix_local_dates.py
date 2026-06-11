import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.models import PruebaMetalurgica


def fix_dates():
    db = SessionLocal()
    try:
        pruebas = (
            db.query(PruebaMetalurgica).filter(PruebaMetalurgica.fecha_ingreso is not None).all()
        )
        print(f"Encontradas {len(pruebas)} pruebas metalúrgicas.")

        # Corregir sumando 5 horas para pasar de hora local Perú (UTC-5) a UTC
        actualizadas = 0
        for p in pruebas:
            original = p.fecha_ingreso
            # Ajustar solo si la fecha parece no estar en UTC (por ejemplo, si es coherente con hora local de pruebas antiguas)
            # Como es local y queremos regularizarla a UTC, le sumamos 5 horas.
            nueva = original + timedelta(hours=5)
            p.fecha_ingreso = nueva
            print(f"Prueba ID {p.id}: {original} (Local) -> {nueva} (UTC)")
            actualizadas += 1

        db.commit()
        print(f"Se actualizaron {actualizadas} pruebas metalúrgicas locales con éxito.")
    except Exception as e:
        db.rollback()
        print(f"Error al corregir fechas: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    fix_dates()
