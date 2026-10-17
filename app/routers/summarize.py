from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.dependencies.security import limitador, verificar_api_key
from app.schemas.summarize import PeticionResumen, RespuestaResumen
from app.services.ia import resumir_codigo

router = APIRouter(tags=["resúmenes"])


@router.post(
    "/summarize",
    dependencies=[Depends(verificar_api_key), Depends(limitador)],
)
def summarize(peticion: PeticionResumen) -> RespuestaResumen:
    """Resume el código con IA y devuelve el lenguaje detectado."""
    # 1. Rechaza códigos enormes sin gastar cuota
    if len(peticion.code) > settings.max_code_length:
        raise HTTPException(status_code=400, detail="El código es demasiado largo.")

    # 2. Pide el resumen a la IA
    try:
        explanation, language = resumir_codigo(peticion.code)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="La IA no respondió correctamente.") from exc

    return RespuestaResumen(explanation=explanation, language=language)
