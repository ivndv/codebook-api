# Comandos de desarrollo de codebook-api
.PHONY: help dev test lint format docs docker-build docker-run

help: ## Muestra esta ayuda
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

dev: ## Arranca el servidor con recarga automática
	.venv/bin/uvicorn app.main:app --reload

test: ## Corre los tests
	.venv/bin/pytest -q

lint: ## Revisa lint y formato (ruff)
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

format: ## Formatea el código
	.venv/bin/ruff format .

docs: ## Abre la documentación (Swagger) en el navegador
	xdg-open http://localhost:8000/docs

docker-build: ## Construye la imagen local
	docker build -t codebook-api .

docker-run: ## Corre la imagen local con el .env
	docker run --rm -p 8000:8000 --env-file .env codebook-api
