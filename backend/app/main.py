"""
INVERMIN PAITITI S.A.C. — Sistema Comercial Minero
Backend principal FastAPI.
"""

from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.database import SessionLocal, check_db_connection
from app.core.security import cleanup_expired_tokens
from app.routers import auth, balanza, entidades, usuarios
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Código que corre al iniciar y al cerrar la app.
    - Startup: verifica BD, limpia tokens expirados.
    - Shutdown: nada por ahora (SQLAlchemy gestiona el pool).
    """
    # ── Startup ──────────────────────────────────────────────────────────────
    print(f"Iniciando {settings.app_name} [{settings.app_env}]")

    if not check_db_connection():
        print("No se pudo conectar a la base de datos al iniciar")
    else:
        print("Conexión a BD establecida")
        # Limpia tokens JWT expirados de la blacklist
        db = SessionLocal()
        try:
            eliminados = cleanup_expired_tokens(db)
            if eliminados:
                print(f"{eliminados} tokens expirados eliminados de la blacklist")
        finally:
            db.close()

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    print("Apagando servidor...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version="0.1.0-mvp",
    description="Sistema ERP Comercial para Planta Paititi - INVERMIN S.A.C.",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(entidades.router, prefix="/api/v1")

# A medida que se agreguen módulos:
app.include_router(balanza.router, prefix="/api/v1")
# app.include_router(muestreo.router, prefix="/api/v1")
# app.include_router(laboratorio.router, prefix="/api/v1")
# app.include_router(liquidaciones.router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Sistema"])
def health():
    """
    Endpoint de salud para Azure App Service health probe.
    Verifica conectividad con la BD.
    """
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "ok" if db_ok else "error",
        "env": settings.app_env,
    }


@app.get("/", tags=["Sistema"])
def root():
    return {"message": settings.app_name, "docs": "/docs"}
