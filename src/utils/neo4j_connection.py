"""
Neo4j connection utilities for Artificial Phronesis knowledge graph.
"""

import os
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Manages Neo4j database connections and queries."""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        load_dotenv()

        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "phronesis123")

        self.driver: Optional[Driver] = None
        self.connect()

    def connect(self):
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")

        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Execute a write query (CREATE, MERGE, etc.).

        Args:
            query: Cypher query string
            parameters: Query parameters
        """
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")

        with self.driver.session() as session:
            session.run(query, parameters or {})

    def initialize_schema(self, schema_file: str):
        """
        Initialize the database schema from a Cypher file.

        Args:
            schema_file: Path to .cypher file containing schema definitions
        """
        logger.info(f"Initializing schema from {schema_file}")

        with open(schema_file, 'r') as f:
            schema_cypher = f.read()

        # Split by semicolons and execute each statement
        statements = [stmt.strip() for stmt in schema_cypher.split(';') if stmt.strip()]

        for i, stmt in enumerate(statements):
            # Skip comments and empty statements
            if stmt.startswith('//') or not stmt:
                continue

            try:
                self.execute_write(stmt)
                logger.info(f"Executed statement {i+1}/{len(statements)}")
            except Exception as e:
                logger.warning(f"Statement {i+1} failed (may already exist): {e}")

        logger.info("Schema initialization complete")

    def clear_database(self):
        """Clear all nodes and relationships from the database. Use with caution!"""
        logger.warning("Clearing entire database...")
        self.execute_write("MATCH (n) DETACH DELETE n")
        logger.info("Database cleared")

    def get_node_count(self) -> int:
        """Get total number of nodes in the database."""
        result = self.execute_query("MATCH (n) RETURN count(n) as count")
        return result[0]['count'] if result else 0

    def get_relationship_count(self) -> int:
        """Get total number of relationships in the database."""
        result = self.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
        return result[0]['count'] if result else 0

    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the current schema."""
        node_labels = self.execute_query("CALL db.labels()")
        rel_types = self.execute_query("CALL db.relationshipTypes()")
        indexes = self.execute_query("SHOW INDEXES")

        return {
            'node_labels': [record['label'] for record in node_labels],
            'relationship_types': [record['relationshipType'] for record in rel_types],
            'indexes': indexes,
            'node_count': self.get_node_count(),
            'relationship_count': self.get_relationship_count()
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Example usage
    with Neo4jConnection() as db:
        info = db.get_schema_info()
        print(f"Node labels: {info['node_labels']}")
        print(f"Relationship types: {info['relationship_types']}")
        print(f"Total nodes: {info['node_count']}")
        print(f"Total relationships: {info['relationship_count']}")
