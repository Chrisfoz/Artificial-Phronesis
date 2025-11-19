.PHONY: help install neo4j-start neo4j-stop init ingest web clean test

help:
	@echo "Artificial Phronesis - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        - Install Python dependencies"
	@echo "  make neo4j-start    - Start Neo4j database"
	@echo "  make neo4j-stop     - Stop Neo4j database"
	@echo "  make init           - Initialize database schema"
	@echo ""
	@echo "Usage:"
	@echo "  make ingest         - Ingest PDF papers from data/papers/"
	@echo "  make web            - Start web interface"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up generated files"
	@echo ""
	@echo "All-in-one:"
	@echo "  make setup          - Full setup (install + neo4j + init)"
	@echo "  make run            - Start Neo4j + Web interface"

install:
	pip install -r requirements.txt

neo4j-start:
	docker-compose up -d
	@echo "Waiting for Neo4j to start..."
	@sleep 10
	@echo "Neo4j is ready at http://localhost:7474"

neo4j-stop:
	docker-compose down

init:
	python scripts/init_database.py

ingest:
	python scripts/ingest_papers.py

ingest-fast:
	python scripts/ingest_papers.py --no-embeddings

web:
	cd web && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

setup: install neo4j-start init
	@echo ""
	@echo "✓ Setup complete!"
	@echo "  - Neo4j running at http://localhost:7474"
	@echo "  - Database schema initialized"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Add PDF papers to data/papers/"
	@echo "  2. Run: make ingest"
	@echo "  3. Run: make web"

run: neo4j-start web
