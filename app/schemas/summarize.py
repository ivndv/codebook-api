from typing import Literal

from pydantic import BaseModel, Field


class PeticionResumen(BaseModel):
    code: str = Field(min_length=1)
    locale: Literal["es", "en"] = "es"


class RespuestaResumen(BaseModel):
    explanation: str
    language: str | None = None
