import os
import sys

import httpx

# Agregar ruta para importar dependencias locales si es necesario
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.models import Rol, Usuario

BASE_URL = "http://localhost:8000/api/v1"


def print_result(name, expected_status, response):
    status = response.status_code
    if (
        isinstance(expected_status, list) and status in expected_status
    ) or status == expected_status:
        print(f"[PASO] {name}: Status: {status}")
    else:
        print(f"[FALLO] {name}: Esperaba {expected_status}, obtuvo {status}")
        try:
            print(f"   Response: {response.text}")
        except Exception:
            pass


def ensure_test_user():
    db = SessionLocal()
    try:
        # Asegurar que el rol ADMIN existe
        rol_admin = db.query(Rol).first()

        user = db.query(Usuario).filter_by(username="test_edge").first()
        if not user:
            user = Usuario(
                username="test_edge",
                password_hash=hash_password("testpass"),
                nombre_completo="Test Edge",
                email="edge@test.com",
                rol_id=rol_admin.id,
                activo=True,
            )
            db.add(user)
            db.commit()
    finally:
        db.close()


def test_edge_cases():
    print("=== Iniciando Pruebas de Casos Extremos (Edge Cases) ===")

    ensure_test_user()

    # 1. Login Authentication
    print("\n--- Autenticacion ---")
    res = httpx.post(
        f"{BASE_URL}/auth/login", data={"username": "test_edge", "password": "wrongpassword"}
    )
    print_result("Login con password incorrecto", 401, res)

    res = httpx.post(
        f"{BASE_URL}/auth/login", data={"username": "notexists", "password": "wrongpassword"}
    )
    print_result("Login con usuario inexistente", 401, res)

    # Obtener token
    res = httpx.post(
        f"{BASE_URL}/auth/login", data={"username": "test_edge", "password": "testpass"}
    )
    if res.status_code != 200:
        print("ERROR CRITICO: No se pudo iniciar sesion con el usuario de prueba")
        return

    token = res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    res = httpx.get(f"{BASE_URL}/usuarios/me", headers={"Authorization": "Bearer tokeninvalido123"})
    print_result("Acceso con token invalido", 401, res)

    # 2. Balanza (Payloads Invalidos)
    print("\n--- Balanza (Payloads Invalidos) ---")

    sesion_payload = {
        "provacop_id": 1,
        "placa": "ABC-123",
    }
    # Crear sesion. Puede fallar si provacop_id 1 no existe
    res = httpx.post(f"{BASE_URL}/balanza/sesiones", json=sesion_payload, headers=headers)
    sesion_id = res.json().get("id") if res.status_code == 201 else 1  # Fallback a 1

    # Lote con peso negativo o bruto < tara
    lote_payload = {
        "tipo_material": "Mineral",
        "pesaje": {
            "peso_inicial": 10,
            "peso_final": 15,  # Tara > Bruto (Inválido)
            "granel": True,
        },
    }
    res = httpx.post(
        f"{BASE_URL}/balanza/sesiones/{sesion_id}/lotes", json=lote_payload, headers=headers
    )
    print_result("Tara > Bruto en pesaje", 422, res)

    lote_payload_neg = {
        "tipo_material": "Mineral",
        "pesaje": {"peso_inicial": -5, "peso_final": 0, "granel": True},
    }
    res = httpx.post(
        f"{BASE_URL}/balanza/sesiones/{sesion_id}/lotes", json=lote_payload_neg, headers=headers
    )
    print_result("Peso negativo en pesaje", 422, res)

    # Tipo de material invalido
    lote_payload_tipo = {
        "tipo_material": "Uranio",  # No está en enum
        "pesaje": {"peso_inicial": 20, "peso_final": 10, "granel": True},
    }
    res = httpx.post(
        f"{BASE_URL}/balanza/sesiones/{sesion_id}/lotes", json=lote_payload_tipo, headers=headers
    )
    print_result("Tipo de material invalido", 422, res)

    # 3. SQL Injection en Terceros (Busqueda)
    print("\n--- Terceros (Inyeccion y Limites) ---")
    res = httpx.get(f"{BASE_URL}/terceros/entidades?q=1' OR '1'='1", headers=headers)
    print_result("Busqueda con caracteres de SQL Injection", 200, res)

    res = httpx.get(f"{BASE_URL}/terceros/entidades?skip=-5&limit=1000000", headers=headers)
    print_result("Paginacion con limites extremos", [422, 200], res)

    # 4. Datos muy largos
    payload_largo = {
        "ruc": "20123456789" * 10,  # RUC largo
        "razon_social": "A",
        "tipo": "EMPRESA",
    }
    res = httpx.post(f"{BASE_URL}/terceros/entidades", json=payload_largo, headers=headers)
    print_result("Entidad con RUC excesivamente largo", [422, 400], res)


if __name__ == "__main__":
    test_edge_cases()
