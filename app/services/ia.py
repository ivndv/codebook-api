# Cliente de IA (Groq, compatible con el SDK de OpenAI)
import json
from functools import lru_cache

from openai import OpenAI

from app.core.config import settings

_SISTEMA = (
    "Resumes código para una app de snippets. Respondes SIEMPRE en español, "
    "en una sola frase, sin markdown y sin repetir el código."
)

_INSTRUCCIONES = (
    "Devuelve un JSON con dos campos:\n"
    '- "explanation": UNA frase en español que explique qué hace el código.\n'
    '- "language": el lenguaje detectado en minúsculas (python, javascript, '
    "typescript, sql...), o null si no lo sabes.\n"
)


@lru_cache(maxsize=1)
def _cliente() -> OpenAI:
    """Crea el cliente una sola vez (perezoso: no falla si aún no hay key)."""
    if not settings.groq_api_key:
        raise RuntimeError("Falta GROQ_API_KEY")
    return OpenAI(base_url=settings.groq_base_url, api_key=settings.groq_api_key)


def resumir_codigo(code: str) -> tuple[str, str | None]:
    """Pide a la IA un resumen de una línea y el lenguaje detectado."""
    respuesta = _cliente().chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": _SISTEMA},
            {"role": "user", "content": f"{_INSTRUCCIONES}\n```\n{code}\n```"},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    contenido = respuesta.choices[0].message.content or "{}"
    datos = json.loads(contenido)

    explanation = str(datos.get("explanation") or "").strip()
    if not explanation:
        raise ValueError("La IA no devolvió una explicación.")

    language = datos.get("language")
    language = str(language).strip().lower() if language else None

    return explanation, language
