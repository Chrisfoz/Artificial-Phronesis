#!/usr/bin/env python3
"""
Ingest PDF papers into the knowledge graph.

This script:
1. Scans data/papers/ for PDF files
2. Extracts text and metadata
3. Uses LLM to extract entities and relationships
4. Loads everything into Neo4j
"""

import sys
import os
from pathlib import Path
from typing import List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.neo4j_connection import Neo4jConnection
from src.ingestion import PDFProcessor, EntityExtractor
from src.ingestion.kg_builder import KnowledgeGraphBuilder
from src.graphrag import GraphRAG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_papers(papers_dir: str, generate_embeddings: bool = True):
    """
    Ingest all papers from a directory.

    Args:
        papers_dir: Directory containing PDF files
        generate_embeddings: Whether to generate and store embeddings
    """
    # Initialize components
    logger.info("Initializing components...")
    db = Neo4jConnection()
    pdf_processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
    entity_extractor = EntityExtractor()
    kg_builder = KnowledgeGraphBuilder(db)

    graphrag = None
    if generate_embeddings:
        try:
            graphrag = GraphRAG(db)
            logger.info("Embeddings will be generated using GraphRAG")
        except Exception as e:
            logger.warning(f"Could not initialize GraphRAG for embeddings: {e}")
            generate_embeddings = False

    # Find PDF files
    papers_path = Path(papers_dir)
    pdf_files = list(papers_path.glob("*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in {papers_dir}")
        logger.info(f"Please add PDF papers to {papers_dir}")
        return

    logger.info(f"Found {len(pdf_files)} PDF files")

    # Process each paper
    for i, pdf_file in enumerate(pdf_files):
        logger.info(f"\n[{i+1}/{len(pdf_files)}] Processing: {pdf_file.name}")

        try:
            # Extract text and metadata
            logger.info("  - Extracting text...")
            paper_data = pdf_processor.process_pdf(str(pdf_file))

            # Extract entities and relationships
            logger.info("  - Extracting entities with LLM...")
            extracted = entity_extractor.process_paper(paper_data)

            # Generate embeddings for chunks
            embeddings = None
            if generate_embeddings and graphrag:
                logger.info("  - Generating embeddings...")
                embeddings = []
                for chunk in extracted['chunks']:
                    emb = graphrag.get_embedding(chunk.text)
                    embeddings.append(emb)

            # Load into Neo4j
            logger.info("  - Loading into knowledge graph...")
            paper_id = kg_builder.ingest_paper(extracted, embeddings)

            logger.info(f"  ✓ Successfully ingested: {paper_data['metadata'].title}")

        except Exception as e:
            logger.error(f"  ✗ Failed to process {pdf_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Summary
    final_info = db.get_schema_info()
    logger.info(f"\n{'='*60}")
    logger.info("Ingestion complete!")
    logger.info(f"{'='*60}")
    logger.info(f"Total nodes: {final_info['node_count']}")
    logger.info(f"Total relationships: {final_info['relationship_count']}")
    logger.info(f"Node types: {final_info['node_labels']}")

    db.close()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest PDF papers into knowledge graph")
    parser.add_argument(
        "--papers-dir",
        default="data/papers",
        help="Directory containing PDF files (default: data/papers)"
    )
    parser.add_argument(
        "--no-embeddings",
        action="store_true",
        help="Skip generating embeddings (faster, but no vector search)"
    )

    args = parser.parse_args()

    ingest_papers(args.papers_dir, generate_embeddings=not args.no_embeddings)


if __name__ == "__main__":
    main()
