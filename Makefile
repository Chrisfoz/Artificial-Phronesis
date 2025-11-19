.PHONY: help install neo4j-start neo4j-stop init ingest web clean test upload-google list-google

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
	@echo "  make ingest         - Ingest PDF papers to Neo4j (with entity extraction)"
	@echo "  make upload-google  - Upload PDFs to Google File Search for RAG"
	@echo "  make list-google    - List files uploaded to Google File Search"
	@echo "  make web            - Start web interface"
	@echo ""
	@echo "Development:"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up generated files"
	@echo ""
	@echo "All-in-one:"
	@echo "  make setup          - Full setup (install + neo4j + init)"
	@echo "  make setup-google   - Full setup + upload to Google"
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

upload-google:
	python scripts/upload_to_google.py

list-google:
	python scripts/upload_to_google.py --list

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
	@echo "  2. Run: make upload-google (for Google RAG)"
	@echo "  3. Run: make ingest (optional - for Neo4j entity extraction)"
	@echo "  4. Run: make web"

setup-google: setup
	@echo ""
	@echo "Uploading papers to Google File Search..."
	python scripts/upload_to_google.py
	@echo ""
	@echo "✓ Google File Search setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run: make web"
	@echo "  2. Visit http://localhost:8000"
	@echo "  3. Ask questions using the Google-powered RAG system"

run: neo4j-start web
