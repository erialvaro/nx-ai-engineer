# {{project_title}} — developer workflow.
# Dev = base + override (auto). Prod = base + prod (explicit).
COMPOSE       = docker compose
COMPOSE_PROD  = docker compose -f docker-compose.yml -f docker-compose.prod.yml

.DEFAULT_GOAL := help
.PHONY: help up down prod logs build shell migrate lint test clean ps restart

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Build + start the dev stack (base + override)
	$(COMPOSE) up --build -d
	@echo "backend  -> http://localhost:$${BACKEND_PORT:-{{backend_port}}}/health"
	@echo "frontend -> http://localhost:$${FRONTEND_PORT:-{{frontend_port}}}"

prod: ## Start the production stack (base + prod)
	$(COMPOSE_PROD) up --build -d

down: ## Stop and remove containers + networks
	$(COMPOSE) down

logs: ## Tail logs from all services
	$(COMPOSE) logs -f --tail=100

build: ## Build all images
	$(COMPOSE) build

shell: ## Open a shell in the backend container (svc=backend|frontend)
	$(COMPOSE) exec $${svc:-backend} sh

migrate: ## Apply Supabase migrations (supabase/migrations/*.sql)
	./scripts/migrate.sh

lint: ## Lint backend + frontend
	$(COMPOSE) run --rm backend sh -c "ruff check . || true"
	$(COMPOSE) run --rm frontend sh -c "npm run lint || true"

test: ## Run backend + frontend tests
	$(COMPOSE) run --rm backend pytest -q
	$(COMPOSE) run --rm frontend sh -c "npm test --silent || true"

ps: ## Show running services
	$(COMPOSE) ps

restart: ## Restart all services
	$(COMPOSE) restart

clean: ## Stop and remove containers, networks, volumes and local images
	$(COMPOSE) down -v --remove-orphans
	@echo "cleaned containers, networks and volumes"
