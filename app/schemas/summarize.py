from pydantic import BaseModel, Field


class PeticionResumen(BaseModel):
    code: str = Field(min_length=1)


class RespuestaResumen(BaseModel):
    explanation: str
    language: str | None = None
