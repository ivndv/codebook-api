from fastapi import APIRouter, Depends, HTTPException
from openai import APIConnectionError, APITimeoutError, RateLimitError

from app.core.config import settings
from app.dependencies.security import verificar_api_key
from app.schemas.summarize import PeticionResumen, RespuestaResumen
from app.services.ia import resumir_codigo

router = APIRouter(tags=["resúmenes"])


@router.post(
    "/summarize",
    dependencies=[Depends(verificar_api_key)],
)
async def summarize(peticion: PeticionResumen) -> RespuestaResumen:
    """Resume el código con IA y devuelve el lenguaje detectado."""
    # 1. Rechaza códigos enormes sin gastar cuota
    if len(peticion.code) > settings.max_code_length:
        raise HTTPException(status_code=400, detail="El código es demasiado largo.")

    # 2. Pide el resumen a la IA y traduce sus fallos a HTTP
    try:
        explanation, language = await resumir_codigo(peticion.code)
    except RateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail="La IA alcanzó su límite. Inténtalo más tarde.",
        ) from exc
    except APITimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="La IA tardó demasiado en responder.",
        ) from exc
    except APIConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con la IA.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="La IA no respondió correctamente.",
        ) from exc

    return RespuestaResumen(explanation=explanation, language=language)
