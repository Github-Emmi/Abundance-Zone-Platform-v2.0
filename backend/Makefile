.PHONY: dev test migrate migrate-create seed lint format install clean docker-up docker-down celery-worker celery-beat

# ─── Development Commands ────────────────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-watch:
	pytest-watch tests/ -v

# ─── Database Commands ───────────────────────────────────────────────────────
migrate:
	alembic upgrade head

migrate-create:
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

migrate-rollback:
	alembic downgrade -1

seed:
	python -m app.scripts.seed_db

# ─── Code Quality ────────────────────────────────────────────────────────────
lint:
	ruff check app/
	mypy app/

format:
	ruff format app/
	isort app/

# ─── Installation ────────────────────────────────────────────────────────────
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# ─── Clean Up ────────────────────────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

# ─── Celery Commands ─────────────────────────────────────────────────────────
celery-worker:
	celery -A app.tasks.celery_app worker --loglevel=info --without-gossip --without-mingle --without-heartbeat

celery-beat:
	celery -A app.tasks.celery_app beat --loglevel=info

celery-flower:
	celery -A app.tasks.celery_app flower --port=5555

# ─── Docker Commands ─────────────────────────────────────────────────────────
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# ─── Help ────────────────────────────────────────────────────────────────────
help:
	@echo "Abundance Zone Youth Platform v2.0 - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start development server with hot reload"
	@echo "  make test             - Run tests with coverage"
	@echo "  make test-watch       - Run tests in watch mode"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          - Run pending migrations"
	@echo "  make migrate-create   - Create new migration"
	@echo "  make migrate-rollback - Rollback last migration"
	@echo "  make seed             - Seed database with initial data"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run linters (ruff + mypy)"
	@echo "  make format           - Format code (ruff + isort)"
	@echo ""
	@echo "Celery:"
	@echo "  make celery-worker    - Start Celery worker"
	@echo "  make celery-beat      - Start Celery beat scheduler"
	@echo "  make celery-flower    - Start Flower monitoring UI"
	@echo ""
	@echo "Other:"
	@echo "  make install          - Install dependencies"
	@echo "  make install-dev      - Install dev dependencies"
	@echo "  make clean            - Remove cache files"
