.PHONY: help install dev test lint format clean docker-up docker-down train

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

dev-backend: ## Start backend dev server
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend dev server
	cd frontend && npm run dev

test: ## Run all tests
	cd backend && python -m pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

lint: ## Run linters
	cd backend && python -m ruff check app/
	cd frontend && npm run lint

format: ## Format code
	cd backend && python -m ruff format app/
	cd frontend && npm run format

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/build
	rm -rf frontend/.next frontend/out

docker-up: ## Start all services with Docker
	docker-compose up -d --build

docker-down: ## Stop all Docker services
	docker-compose down

train: ## Train all ML models
	cd ml-engine && python -m training.trainer --task all

generate-data: ## Generate synthetic training data
	cd ml-engine && python -m training.data_generator --samples 5000
