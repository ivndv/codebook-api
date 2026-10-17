# Configuración del servicio (variables de entorno)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Clave de la IA (secreta: solo vive aquí)
    groq_api_key: str = ""

    # Secreto compartido con el front (header X-API-Key).
    # Si está vacío NO se exige (solo para desarrollo local).
    codebook_api_key: str = ""

    # Proveedor de IA (compatible con el SDK de OpenAI)
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-20b"

    # Límites
    rate_limit_per_min: int = 10
    rate_limit_per_day: int = 100
    max_code_length: int = 10_000

    # CORS: orígenes permitidos (separados por coma)
    allowed_origins: str = "http://localhost:3000"


settings = Settings()
