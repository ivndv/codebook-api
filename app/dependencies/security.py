# Seguridad: X-API-Key (secreto compartido) y rate limit por IP
import secrets
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request

from app.core.config import settings


def verificar_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Comprueba el secreto compartido del header X-API-Key."""
    # Sin secreto configurado no se exige (solo desarrollo local)
    if not settings.codebook_api_key:
        return

    # compare_digest evita timing attacks (comparar con == filtra información)
    if x_api_key is None or not secrets.compare_digest(x_api_key, settings.codebook_api_key):
        raise HTTPException(status_code=401, detail="API key inválida.")


class LimitadorPorIP:
    """Límite de peticiones por IP, en memoria (por minuto y por día)."""

    def __init__(self) -> None:
        self._peticiones: dict[str, deque[float]] = defaultdict(deque)

    def limpiar(self) -> None:
        """Vacía los contadores (lo usan los tests)."""
        self._peticiones.clear()

    def _consumir(self, clave: str, limite: int, ventana: float) -> int | None:
        """Apunta la petición. Devuelve los segundos a esperar si se pasó del límite."""
        ahora = time.monotonic()
        cola = self._peticiones[clave]

        # 1. Descarta lo que ya salió de la ventana
        while cola and ahora - cola[0] > ventana:
            cola.popleft()

        # 2. Si está lleno, dice cuánto falta para el siguiente hueco
        if len(cola) >= limite:
            return int(ventana - (ahora - cola[0])) + 1

        # 3. Hay hueco: apunta la petición
        cola.append(ahora)
        return None

    def __call__(self, request: Request) -> None:
        """Se usa como dependencia: aplica los límites de la configuración."""
        ip = request.client.host if request.client else "desconocida"

        espera = self._consumir(f"{ip}:min", settings.rate_limit_per_min, 60)
        if espera is not None:
            raise HTTPException(
                status_code=429,
                detail="Demasiadas peticiones por minuto.",
                headers={"Retry-After": str(espera)},
            )

        espera = self._consumir(f"{ip}:dia", settings.rate_limit_per_day, 86_400)
        if espera is not None:
            raise HTTPException(
                status_code=429,
                detail="Demasiadas peticiones hoy.",
                headers={"Retry-After": str(espera)},
            )


# Instancia única que usan los routers como dependencia
limitador = LimitadorPorIP()
