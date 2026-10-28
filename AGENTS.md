# AGENTS.md — Guía para Agentes en Codebook API

Guía operativa y técnica para agentes de Inteligencia Artificial que colaboren en el desarrollo del proyecto **codebook-api**.

---

## 1. Visión General del Proyecto

**codebook-api** es un microservicio en **Python (FastAPI)** que recibe un fragmento de código y devuelve un **resumen de una línea** generado con IA, más el lenguaje detectado.

* **Propósito:** aislar la **clave de la IA** y la llamada al modelo del frontend.
* **Consumidor único:** el backend de `codebook` (Next.js), vía `POST /summarize`.
* **Documentación de arquitectura:** [`docs/diseno-y-arquitectura.md`](docs/diseno-y-arquitectura.md).
* **Repositorio:** `codebook-api` · **Front:** `codebook`.

---

## 2. Antes de Tocar Código

* **Documentación de arquitectura:** lee `docs/diseno-y-arquitectura.md` antes de cambios estructurales.
* **FastAPI:** https://fastapi.tiangolo.com/
* **Groq (compatible con el SDK de OpenAI):** https://console.groq.com/docs/openai
* **Uso del MCP CodeGraph:** antes de búsquedas masivas, usa `codegraph_explore` con `projectPath: "/home/ivan/software-dev/codebook-api"`.

---

## 3. Stack Tecnológico

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

---

## 4. Estructura del Código

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

---

## 5. Comandos de Desarrollo

Todos los comandos usan el entorno virtual `.venv`:

```bash
# Con el Makefile (recomendado)
make dev          # servidor con recarga
make test         # pytest
make lint         # ruff check + format --check
make format       # ruff format
make docs         # abre Swagger
make docker-build # imagen local
make docker-run   # contenedor con .env

# O a mano
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/uvicorn app.main:app --reload
.venv/bin/ruff check .
.venv/bin/pytest -q
```

---

## 6. Convenciones Obligatorias para Agentes

### 6.1 Regla de Oro en Ejecución de Checks

* **PROHIBIDO ejecutar tests o linter de forma reactiva tras cada pequeño cambio.** Acumula los cambios y corre `ruff check .` y `pytest -q` **una sola vez al final**.

### 6.2 Estilo de Código y Comentarios

* **Lenguaje:** código, comentarios y documentación en **español**.
* **Comentarios:** `#` de **una sola línea**, en español, **sin punto final**. Nada de docstrings multilínea largos (salvo la línea de resumen del módulo o función).
* **Pasos numerados:** `# 1. …`, `# 2. …` dentro de la lógica secuencial larga.
* **Tipado estricto:** anotaciones de tipo en todas las funciones; prohibido `Any` sin justificar.

### 6.3 Reglas de Negocio

* **La clave de Groq NUNCA sale de este servicio.** El front jamás la conoce.
* **Los tests NO llaman a Groq de verdad** → siempre mockeado.
* **`/health` debe ser ultraligero** (sin tocar la IA): lo usa el monitoreo y el anti-pausa.
* **El rate limit por usuario o IP no vive aquí**: lo aplica Next.js con Upstash.
* **Todo fallo de la IA se traduce a un código HTTP explícito** (`429`, `502`, `503`, `504`); nunca se devuelve un 500 genérico.

### 6.4 Contrato con el frontend

* El frontend espera exactamente `{ explanation: string, language: string | null }`.
* `language` va en **minúsculas** o `null`.
* `MAX_CODE_LENGTH` (10.000) está duplicado a propósito en ambos lados: si cambia aquí, cambia en `codebook/src/core/domain/snippet.ts`.

### 6.5 Flujo de Git

* **PROHIBIDO hacer commits o push sin la aprobación explícita del usuario.**
* **Flujo de ramas:** desarrollo en `develop`; merge a `main` solo tras aprobación.
* **Mensajes de commit:** *Conventional Commits* en minúsculas y español (`feat: …`, `fix: …`, `chore: …`).

---

## 7. CI/CD y Despliegue

* **CI**: `.github/workflows/ci-cd.yml` — ruff + pytest en push/PR a `main` y `develop`
* **CD**: `.github/workflows/deploy.yml` — manual (`workflow_dispatch`), solo `main`
* **Deploy**: Actions → `codebook-api Deploy` → Run workflow
* **Autodeploy**: apagado; el deploy siempre es manual
* **Secret**: `RAILWAY_TOKEN` (scope `production`)
* **Variable**: `RAILWAY_PROJECT_ID` (y `RAILWAY_URL` opcional para smoke test)
* **Railway**: Dockerfile, `PORT=8000`, Serverless, healthcheck `/health`
* **Rollback**: Railway → Deployments → Redeploy
* **Dokploy**: standby manual, sin CI
* No usar `railway.toml` ni `railway.json` (Config-as-Code deprecado)
* No commitear secretos ni `.env`
