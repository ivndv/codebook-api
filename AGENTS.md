# AGENTS.md — Guía para Agentes en Codebook API

Guía operativa y técnica para agentes de Inteligencia Artificial que colaboren en el desarrollo del proyecto **codebook-api**.

---

## 1. Visión General del Proyecto

**codebook-api** es un microservicio en **Python (FastAPI)** que recibe un fragmento de código y devuelve un **resumen de una línea** generado con IA, más el lenguaje detectado.

* **Propósito:** Aislar la **clave de la IA** y la llamada al modelo del frontend.
* **Consumidor único:** el backend de `codebook` (Next.js), vía `POST /summarize`.
* **Documentación de diseño:** `../codebook-api.md`.
* **Repositorio:** `codebook-api` · **Front:** `codebook`.

---

## 2. Antes de Tocar Código

* **Documentación de FastAPI:** https://fastapi.tiangolo.com/
* **Groq (compatible con el SDK de OpenAI):** https://console.groq.com/docs/openai
* **Uso del MCP CodeGraph:** antes de búsquedas masivas, usa `codegraph_explore` con `projectPath: "/home/ivan/software-dev/codebook-api"`.

---

## 3. Stack Tecnológico

| Capa | Tecnología | Detalle |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | ASGI, async, OpenAPI automático |
| **Servidor** | **Uvicorn** | `--host 0.0.0.0 --port $PORT` |
| **IA** | **Groq** vía SDK `openai` | `base_url=https://api.groq.com/openai/v1` |
| **Modelo** | `openai/gpt-oss-20b` | Rápido y barato (free: 1.000 req/día) |
| **Config** | **pydantic-settings** | Variables de entorno tipadas |
| **Tests** | **pytest** + httpx | IA mockeada (no gasta cuota) |
| **Lint/Formato** | **ruff** | `line-length 100` |
| **Deploy** | **Railway** | Con **Serverless** (duerme por inactividad) |
| **Python** | 3.11+ | `.python-version` fija 3.13 |

---

## 4. Estructura del Código

```plaintext
codebook-api/
├── app/
│   ├── __init__.py      → paquete
│   ├── main.py          → FastAPI: /health y /summarize
│   ├── config.py        → settings (pydantic-settings)
│   ├── ai.py            → cliente Groq + summarize()
│   └── rate_limit.py    → limitador por IP
├── tests/               → pytest (IA mockeada)
├── requirements.txt     → dependencias de producción
├── requirements-dev.txt → + pytest, ruff, httpx
├── pyproject.toml       → config de ruff y pytest
├── .env.example         → plantilla de variables
└── .github/workflows/   → CI (ruff + pytest)
```

---

## 5. Comandos de Desarrollo

Todos los comandos usan el entorno virtual `.venv`:

```bash
# Crear el entorno
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt

# Servidor de desarrollo
.venv/bin/uvicorn app.main:app --reload

# Lint y formato
.venv/bin/ruff check .
.venv/bin/ruff format .

# Tests
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
* **El invitado puede usar `/summarize`** (el rate limit protege la cuota), pero **el guardado ocurre en el front**.

### 6.4 Flujo de Git

* **PROHIBIDO hacer commits o push sin la aprobación explícita del usuario.**
* **Flujo de ramas:** desarrollo en `develop`; merge a `main` solo tras aprobación.
* **Mensajes de commit:** *Conventional Commits* en minúsculas y español (`feat: …`, `fix: …`, `chore: …`).

### 6.5 Fases del Proyecto

| Fase | Alcance | Estado |
| :--- | :--- | :--- |
| **F8.0** | Scaffolding (estructura, ruff, docs, CI) | ✅ |
| **F8.1** | API + Groq (`/summarize` real) | ⏳ |
| **F8.2** | Rate limit + seguridad (`X-API-Key`, CORS) | ⏳ |
| **F8.3** | Deploy en Railway (+ Serverless) | ⏳ |
| **F8.4** | Conectar el front (retry + mock → real) | ⏳ |
