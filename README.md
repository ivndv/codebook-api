# Codebook API

## Descripción

Microservicio en Python que recibe un fragmento de código y devuelve un resumen de una línea generado con IA (Groq), junto al lenguaje detectado. Existe para aislar la clave de la IA del frontend: el navegador nunca conoce la API key de Groq, solo habla con este servicio.

## Características

- **Resumen con IA**: devuelve la explicación del código y el lenguaje detectado en una sola petición.
- **Salud ultraligera**: `/health` responde sin tocar la IA ni la base de datos.
- **Cliente async de Groq**: `AsyncOpenAI` sin bloquear el event loop.
- **Errores traducidos a HTTP**: cada fallo del proveedor tiene su código, sin 500 genéricos.
- **Autenticación simple**: secreto compartido en el header `X-API-Key`.
- **Rate limiting delegado**: el frontend limita por usuario o IP antes de llamar.
- **Documentación automática**: Swagger/OpenAPI en `/docs`.
- **Tests sin gastar cuota**: la IA va mockeada en pytest.

## Secciones

### Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/health` | `{ "status": "ok" }` — sin IA, sin dependencias |
| `POST` | `/summarize` | Recibe `{ code }` y devuelve `{ explanation, language }` |

### Códigos de error

| Código | Causa |
|---|---|
| `400` | Código vacío o mayor a `MAX_CODE_LENGTH` (10.000) |
| `401` | `X-API-Key` ausente o incorrecta |
| `429` | Groq agotó la cuota |
| `502` | La IA respondió algo no parseable |
| `503` | No se pudo conectar con Groq |
| `504` | Groq tardó más que `GROQ_TIMEOUT_SECONDS` |

## Uso

El consumidor único es el backend de Codebook, que llama desde el servidor:

```bash
curl -X POST http://localhost:8100/summarize \
  -H "X-API-Key: tu_secreto" \
  -H "Content-Type: application/json" \
  -d '{"code": "def suma(a, b):\n    return a + b"}'
```

```json
{
  "explanation": "Suma dos números y devuelve el resultado.",
  "language": "python"
}
```

- **`explanation`**: una frase en español que describe qué hace el código.
- **`language`**: lenguaje detectado en minúsculas, o `null` si el modelo no lo identifica.
- **`code`**: máximo 10.000 caracteres; el mismo límite que valida el frontend.

Si `CODEBOOK_API_KEY` está vacío, el header no se exige. Eso es solo para desarrollo local: en producción debe estar configurado.

## Tecnologías Utilizadas

- **Lenguaje**: Python 3
- **Framework**: FastAPI + Uvicorn
- **IA**: Groq (`openai/gpt-oss-20b`) mediante el SDK de OpenAI
- **Configuración**: pydantic-settings
- **Testing**: pytest + httpx, IA mockeada
- **Lint & Formato**: ruff
- **Herramientas**: Docker
- **Infra & CI/CD**: Railway, Dokploy (standby), GitHub Actions

## Despliegue

El servicio corre en **Railway** con Serverless activo.

- **API:** [Codebook API](https://codebook-api-production-0be5.up.railway.app/health)
- **Documentación:** [Swagger](https://codebook-api-production-0be5.up.railway.app/docs)

Dokploy + Cloudflare Tunnel queda como respaldo manual:

- **API:** [Codebook API (respaldo)](https://codebook-api.fluxdv.icu/health)

## Licencia

[PolyForm Noncommercial 1.0.0](LICENSE). Uso personal y no comercial; el uso comercial requiere permiso.

© 2026 Ivan Cruz
