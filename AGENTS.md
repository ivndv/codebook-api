# AGENTS.md — Codebook API

Guía operativa y técnica para agentes de Inteligencia Artificial que colaboren en el desarrollo de **codebook-api**.

## 1. Visión general

**codebook-api** es un microservicio en **Python (FastAPI)** que recibe un fragmento de código y devuelve un **resumen de una línea** generado con IA, más el lenguaje detectado.

- **Propósito:** aislar la **clave de la IA** y la llamada al modelo del frontend.
- **Consumidor único:** el backend de `codebook` (Next.js), vía `POST /summarize`.
- **Documentación de arquitectura:** [`docs/diseno-y-arquitectura.md`](docs/diseno-y-arquitectura.md).
- **Repositorio:** `codebook-api` · **Front:** `codebook`.

## 2. Antes de tocar código

- **Documentación de arquitectura:** lee `docs/diseno-y-arquitectura.md` antes de cambios estructurales.
- **FastAPI:** https://fastapi.tiangolo.com/
- **Groq (compatible con el SDK de OpenAI):** https://console.groq.com/docs/openai

**CodeGraph** (índice de símbolos del repo): usa `codegraph_explore` (`query`, `maxFiles`, `projectPath`) antes de un grep masivo o de leer varios archivos; devuelve fuente verbatim, rutas de llamada e impacto.

- `codegraph sync /home/ivan/software-dev/codebook-api` tras editar, pull o cambiar de rama (incremental, uso normal).
- `codegraph index /home/ivan/software-dev/codebook-api` solo al crear el índice, tras `codegraph upgrade` o si `status` avisa `built by vX` (rebuild completo).
- `codegraph status /home/ivan/software-dev/codebook-api` para comprobar el estado.

## 3. Stack tecnológico

| Capa | Tecnología | Detalle |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | ASGI, async, OpenAPI automático |
| **Servidor** | **Uvicorn** | `--host 0.0.0.0 --port $PORT` |
| **IA** | **Groq** vía SDK `openai` | `AsyncOpenAI` + `base_url=https://api.groq.com/openai/v1` |
| **Modelo** | `openai/gpt-oss-20b` | Rápido y barato (free: 1.000 req/día) |
| **Config** | **pydantic-settings** | Variables de entorno tipadas |
| **Tests** | **pytest** + httpx | IA mockeada (no gasta cuota) |
| **Lint/Formato** | **ruff** | `line-length 100` |
| **Deploy** | **Railway** | Manual vía GitHub Actions; **Serverless** activo |
| **Python** | 3.15.1 | `.python-version` fija 3.15.1 |

## 4. Estructura del código

```plaintext
codebook-api/
├── app/
│   ├── main.py                  → crea la app, CORS y monta los routers
│   ├── core/config.py           → settings (pydantic-settings)
│   ├── routers/
│   │   ├── health.py            → GET /health
│   │   └── summarize.py         → POST /summarize
│   ├── schemas/summarize.py     → PeticionResumen · RespuestaResumen
│   ├── services/ia.py           → cliente Groq + resumir_codigo()
│   └── dependencies/security.py → verificación de X-API-Key
├── tests/                       → 11 pruebas pytest (IA mockeada)
├── docs/                        → documentación de arquitectura
├── Makefile                     → make dev / test / lint / format / docs
├── requirements.txt             → dependencias de producción
├── requirements-dev.txt         → + pytest, ruff, httpx
├── pyproject.toml               → config de ruff y pytest
├── Dockerfile                   → imagen sin privilegios + healthcheck
├── .env.example                 → plantilla de variables
└── .github/workflows/           → CI (ruff + pytest) + CD manual (Railway)
```

## 5. Arquitectura y flujo de datos

### 5.1 Flujo de una petición

- `POST /summarize` entra por `app/routers/summarize.py`, se valida con `app/schemas/summarize.py` y se resuelve en `app/services/ia.py`.
- `app/services/ia.py` usa el cliente Groq (`AsyncOpenAI`) y devuelve el resumen junto al lenguaje detectado.
- `app/dependencies/security.py` verifica el header `X-API-Key`.
- `GET /health` vive en `app/routers/health.py` y se mantiene separado del flujo de IA.

### 5.2 Contrato con el frontend

- El frontend espera exactamente `{ explanation: string, language: string | null }`.
- `language` va en **minúsculas** o `null`.
- `MAX_CODE_LENGTH` (10.000) está duplicado a propósito en ambos lados: si cambia aquí, cambia en `codebook/src/core/domain/snippet.ts`.

## 6. Variables de entorno

`.env.example` es la plantilla; `.env` está en `.gitignore`. Solo se documentan los nombres, nunca los valores.

- **IA:** `GROQ_API_KEY`, `GROQ_BASE_URL`, `GROQ_MODEL`, `GROQ_TIMEOUT_SECONDS`.
- **Seguridad:** `CODEBOOK_API_KEY`.
- **CORS:** `ALLOWED_ORIGINS`.

## 7. Comandos

Todos los comandos usan el entorno virtual `.venv`.

### 7.1 Con el Makefile (recomendado)

```bash
# Servidor con recarga
make dev

# pytest
make test

# ruff check + format --check
make lint

# ruff format
make format

# Abre Swagger
make docs

# Imagen local
make docker-build

# Contenedor con .env
make docker-run
```

### 7.2 A mano

```bash
# Crear entorno virtual
python3 -m venv .venv

# Instalar dependencias de desarrollo
.venv/bin/pip install -r requirements-dev.txt

# Servidor con recarga
.venv/bin/uvicorn app.main:app --reload

# Lint
.venv/bin/ruff check .

# Tests
.venv/bin/pytest -q
```

## 8. Convenciones y reglas críticas

### 8.1 Regla de oro en ejecución de checks

- **PROHIBIDO ejecutar tests o linter de forma reactiva tras cada pequeño cambio.** Acumula los cambios y corre `ruff check .` y `pytest -q` **una sola vez al final**.

### 8.2 Estilo de código y comentarios

- **Lenguaje:** código, comentarios y documentación en **español**.
- **Comentarios:** `#` de **una sola línea**, en español, **sin punto final**. Nada de docstrings multilínea largos (salvo la línea de resumen del módulo o función).
- **Pasos numerados:** `# 1. …`, `# 2. …` dentro de la lógica secuencial larga.
- **Tipado estricto:** anotaciones de tipo en todas las funciones; prohibido `Any` sin justificar.

### 8.3 Reglas de negocio

- **La clave de Groq NUNCA sale de este servicio.** El front jamás la conoce.
- **Los tests NO llaman a Groq de verdad** → siempre mockeado.
- **`/health` debe ser ultraligero** (sin tocar la IA): lo usa el monitoreo y el anti-pausa.
- **El rate limit por usuario o IP no vive aquí**: lo aplica Next.js con Upstash.
- **Todo fallo de la IA se traduce a un código HTTP explícito** (`429`, `502`, `503`, `504`); nunca se devuelve un 500 genérico.

## 9. Flujo de Git y despliegue

- **PROHIBIDO hacer commits o push sin la aprobación explícita del usuario.**
- **Flujo de ramas:** desarrollo en `develop`; merge a `main` solo tras aprobación.
- **Mensajes de commit:** *Conventional Commits* en minúsculas y español (`feat: ...`, `fix: ...`, `chore: ...`).
- El despliegue se detalla en §10.

## 10. CI/CD

- **CI**: `.github/workflows/ci-cd.yml` — ruff + pytest en push/PR a `main` y `develop`
- **CD**: `.github/workflows/deploy.yml` — manual (`workflow_dispatch`), solo `main`
- **Deploy**: Actions → `codebook-api Deploy` → Run workflow
- **Autodeploy**: apagado; el deploy siempre es manual
- **Secret**: `RAILWAY_TOKEN` (scope `production`)
- **Variable**: `RAILWAY_PROJECT_ID` (y `RAILWAY_URL` opcional para smoke test)
- **Railway**: Dockerfile, `PORT=8000`, Serverless, healthcheck `/health`
- **Rollback**: Railway → Deployments → Redeploy
- **Dokploy**: standby manual, sin CI
- No usar `railway.toml` ni `railway.json` (Config-as-Code deprecado)
- No commitear secretos ni `.env`
