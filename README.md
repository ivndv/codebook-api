# Codebook API

## Descripción

Microservicio en Python que recibe un fragmento de código y devuelve un **resumen de una línea** generado con IA (Groq), junto al lenguaje detectado.

Existe para **aislar la clave de la IA** del frontend: el navegador nunca conoce la API key de Groq, solo habla con este servicio.

## Características

- **Resumen con IA**: `POST /summarize` devuelve `{ explanation, language }`.
- **Salud**: `GET /health` ultraligero, para monitoreo y para evitar la pausa por inactividad.
- **Rate limiting**: límite por IP (peticiones por minuto y por día).
- **Autenticación simple**: secreto compartido en el header `X-API-Key`.
- **Documentación automática**: Swagger/OpenAPI en `/docs`.
- **Tests sin gastar cuota**: la IA va mockeada en pytest.

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/health` | `{ "status": "ok" }` |
| `POST` | `/summarize` | Recibe `{ code }` y devuelve `{ explanation, language }` |

```bash
curl -X POST http://localhost:8000/summarize \
  -H "X-API-Key: tu_secreto" \
  -H "Content-Type: application/json" \
  -d '{"code": "def suma(a, b):\n    return a + b"}'
```

## Estructura

```plaintext
app/
├── main.py                  → crea la app, CORS y monta los routers
├── core/config.py           → settings (pydantic-settings)
├── routers/                 → health.py · summarize.py
├── schemas/                 → PeticionResumen · RespuestaResumen
├── services/ia.py           → cliente Groq + resumir_codigo()
└── dependencies/security.py → X-API-Key + rate limit por IP
```

## Tecnologías Utilizadas

- **Framework**: FastAPI + Uvicorn
- **IA**: Groq (`openai/gpt-oss-20b`) mediante el SDK de OpenAI
- **Config**: pydantic-settings (variables de entorno tipadas)
- **Tests**: pytest + httpx
- **Lint & formato**: ruff
- **Infra & CI/CD**: Railway + GitHub Actions

## Instalación

1. **Clonar el Repositorio**:

```bash
git clone https://github.com/ivndv/codebook-api.git
```

2. **Crear el entorno e instalar dependencias**:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
```

3. **Variables de Entorno**: copia `.env.example` a `.env` y rellena los valores.

```env
GROQ_API_KEY=tu_clave_de_groq
CODEBOOK_API_KEY=tu_secreto_compartido
GROQ_MODEL=openai/gpt-oss-20b
ALLOWED_ORIGINS=http://localhost:3000
```

4. **Iniciar el Proyecto**:

```bash
# Con el Makefile (recomendado)
make dev      # servidor con recarga en http://localhost:8000
make test     # tests
make lint     # ruff
make docs     # abre Swagger

# O a mano
.venv/bin/uvicorn app.main:app --reload
```

La documentación interactiva (Swagger) queda en **http://localhost:8000/docs**.

## Despliegue

Desplegado en **Railway** con **Serverless** activado (el servicio duerme cuando no se usa, para que quepa en el plan gratuito). El front reintenta automáticamente la primera petición tras el "despertar".

## Licencia

Licencia de Uso Personal:

Este software es propiedad de **Ivan Cruz**. Se permite el uso de este software solo para fines personales y no comerciales. No se permite la distribución, modificación ni uso comercial de este software sin el consentimiento expreso de **Ivan Cruz**.

Cualquier uso no autorizado puede resultar en acciones legales.
