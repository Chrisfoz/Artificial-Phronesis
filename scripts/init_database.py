#!/usr/bin/env python3
"""
Initialize the Artificial Phronesis knowledge graph database.

This script:
1. Connects to Neo4j
2. Optionally clears existing data
3. Runs the schema initialization
4. Loads seed data
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.neo4j_connection import Neo4jConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the database."""
    logger.info("Initializing Artificial Phronesis knowledge graph...")

    # Connect to Neo4j
    db = Neo4jConnection()

    # Check connection
    info = db.get_schema_info()
    logger.info(f"Connected to Neo4j - Current state:")
    logger.info(f"  Nodes: {info['node_count']}")
    logger.info(f"  Relationships: {info['relationship_count']}")
    logger.info(f"  Labels: {info['node_labels']}")

    # Ask if should clear database
    if info['node_count'] > 0:
        response = input(f"\nDatabase contains {info['node_count']} nodes. Clear all data? (yes/no): ")
        if response.lower() == 'yes':
            logger.warning("Clearing database...")
            db.clear_database()
            logger.info("Database cleared")

    # Initialize schema
    schema_file = Path(__file__).parent.parent / "schema" / "init_schema.cypher"
    logger.info(f"Loading schema from {schema_file}")

    db.initialize_schema(str(schema_file))

    # Show final state
    final_info = db.get_schema_info()
    logger.info(f"\nDatabase initialized:")
    logger.info(f"  Nodes: {final_info['node_count']}")
    logger.info(f"  Relationships: {final_info['relationship_count']}")
    logger.info(f"  Labels: {final_info['node_labels']}")
    logger.info(f"  Relationship types: {final_info['relationship_types']}")

    logger.info("\n✓ Database initialization complete!")
    logger.info("\nNext steps:")
    logger.info("  1. Add PDF papers to data/papers/")
    logger.info("  2. Run: python scripts/ingest_papers.py")

    db.close()


if __name__ == "__main__":
    main()
