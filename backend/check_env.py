from app.core.config import get_settings

# Cargamos la configuración de Pydantic
settings = get_settings()

print("--- CONFIGURACIÓN ACTUAL DE LA APP ---")
print(f"Entorno (APP_ENV):  {settings.app_env}")
print(f"Motor DB:           {settings.db_engine}")
print(f"Servidor:           {settings.db_server}")
print(f"Base de datos:      {settings.db_name}")
print(f"URL generada:       {settings.database_url}")
print("--------------------------------------")
