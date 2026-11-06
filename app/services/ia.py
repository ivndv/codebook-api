# Cliente de IA (Groq, compatible con el SDK de OpenAI)
import json
from functools import lru_cache

from openai import AsyncOpenAI

from app.core.config import settings

# Idioma de salida que acepta la app
_IDIOMAS = {"es": "Spanish", "en": "English"}

_SISTEMA = (
    "You summarize code for a snippet app. "
    "Write exactly one sentence, no markdown, and never repeat the code. "
    "Keep identifiers and technical terms as they appear. "
    "Always write the explanation in {language}."
)

_INSTRUCCIONES = (
    "Return a JSON object with two fields:\n"
    '- "explanation": ONE sentence in {language} explaining what the code does.\n'
    '- "language": the detected programming language in lowercase '
    "(python, javascript, typescript, sql...), or null if unknown.\n"
)


def _idioma(locale: str) -> str:
    """Idioma de salida que se le pide a la IA."""
    return _IDIOMAS.get(locale, "Spanish")


def _sistema(locale: str) -> str:
    """Instrucción de sistema con el idioma de salida."""
    return _SISTEMA.format(language=_idioma(locale))


def _instrucciones(locale: str) -> str:
    """Instrucción de usuario con el idioma de salida."""
    return _INSTRUCCIONES.format(language=_idioma(locale))


@lru_cache(maxsize=1)
def _cliente() -> AsyncOpenAI:
    """Crea el cliente una sola vez (perezoso: no falla si aún no hay key)."""
    if not settings.groq_api_key:
        raise RuntimeError("Falta GROQ_API_KEY")

    # Sin reintentos internos: el frontend ya reintenta la llamada
    return AsyncOpenAI(
        base_url=settings.groq_base_url,
        api_key=settings.groq_api_key,
        timeout=settings.groq_timeout_seconds,
        max_retries=0,
    )


async def resumir_codigo(code: str, locale: str = "es") -> tuple[str, str | None]:
    """Pide a la IA un resumen de una línea y el lenguaje detectado."""
    respuesta = await _cliente().chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": _sistema(locale)},
            {
                "role": "user",
                "content": f"{_instrucciones(locale)}\n```\n{code}\n```",
            },
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
