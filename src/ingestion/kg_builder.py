"""
Knowledge graph builder - loads extracted entities into Neo4j.
"""

import hashlib
from typing import Dict, Any, List
from datetime import datetime
import logging

from src.utils.neo4j_connection import Neo4jConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Builds the knowledge graph from extracted entities and relationships."""

    def __init__(self, neo4j_conn: Neo4jConnection):
        """
        Initialize knowledge graph builder.

        Args:
            neo4j_conn: Neo4j database connection
        """
        self.db = neo4j_conn

    def create_paper_node(self, metadata: Any) -> str:
        """
        Create a Paper node in the graph.

        Args:
            metadata: PaperMetadata object

        Returns:
            Paper ID
        """
        # Generate unique ID for paper
        paper_id = self._generate_id(metadata.title or metadata.file_path)

        query = """
        MERGE (p:Paper {id: $paper_id})
        SET p.title = $title,
            p.year = $year,
            p.abstract = $abstract,
            p.doi = $doi,
            p.venue = $venue,
            p.file_path = $file_path,
            p.authors_list = $authors,
            p.updated_at = datetime()
        RETURN p.id as id
        """

        self.db.execute_write(query, {
            'paper_id': paper_id,
            'title': metadata.title,
            'year': metadata.year,
            'abstract': metadata.abstract,
            'doi': metadata.doi,
            'venue': metadata.venue,
            'file_path': metadata.file_path,
            'authors': metadata.authors or []
        })

        logger.info(f"Created Paper node: {metadata.title}")
        return paper_id

    def create_author_nodes(self, authors: List[str], paper_id: str):
        """
        Create Author nodes and link them to a paper.

        Args:
            authors: List of author names
            paper_id: ID of the paper they authored
        """
        for author_name in authors:
            author_id = self._generate_id(author_name)

            query = """
            MERGE (a:Author {id: $author_id})
            SET a.name = $name,
                a.updated_at = datetime()

            WITH a
            MATCH (p:Paper {id: $paper_id})
            MERGE (a)-[:AUTHORED]->(p)
            """

            self.db.execute_write(query, {
                'author_id': author_id,
                'name': author_name,
                'paper_id': paper_id
            })

        logger.info(f"Created {len(authors)} author nodes")

    def create_concept_nodes(self, entities: List[Dict[str, Any]], paper_id: str):
        """
        Create Concept/Trait/Architecture nodes from extracted entities.

        Args:
            entities: List of extracted entities
            paper_id: ID of the source paper
        """
        for entity in entities:
            entity_type = entity.get('type', 'concept')
            name = entity.get('name')

            if not name:
                continue

            # Determine node label
            if entity_type == 'trait':
                label = 'Trait'
            elif entity_type == 'architecture':
                label = 'Architecture'
            else:
                label = 'Concept'

            # Create or update the node
            query = f"""
            MERGE (e:{label} {{name: $name}})
            SET e.description = COALESCE($description, e.description),
                e.domain = COALESCE($domain, e.domain),
                e.type = COALESCE($type, e.type),
                e.updated_at = datetime()

            WITH e
            MATCH (p:Paper {{id: $paper_id}})
            MERGE (p)-[:DISCUSSES]->(e)
            """

            self.db.execute_write(query, {
                'name': name,
                'description': entity.get('description'),
                'domain': entity.get('domain'),
                'type': entity.get('type'),
                'paper_id': paper_id
            })

        logger.info(f"Created {len(entities)} entity nodes")

    def create_relationships(self, relationships: List[Dict[str, Any]]):
        """
        Create relationships between entities.

        Args:
            relationships: List of extracted relationships
        """
        for rel in relationships:
            source = rel.get('source')
            target = rel.get('target')
            rel_type = rel.get('relationship', 'RELATED_TO')
            properties = rel.get('properties', {})

            if not source or not target:
                continue

            # Build property string for Cypher
            prop_string = ", ".join([f"r.{k} = ${k}" for k in properties.keys()])
            if prop_string:
                prop_string = "SET " + prop_string

            # Try to find nodes (could be Concept, Trait, or Architecture)
            query = f"""
            MATCH (s) WHERE s.name = $source
            MATCH (t) WHERE t.name = $target
            MERGE (s)-[r:{rel_type}]->(t)
            {prop_string}
            SET r.updated_at = datetime()
            """

            params = {
                'source': source,
                'target': target,
                **properties
            }

            try:
                self.db.execute_write(query, params)
            except Exception as e:
                logger.warning(f"Failed to create relationship {source}-[{rel_type}]->{target}: {e}")

        logger.info(f"Created {len(relationships)} relationships")

    def create_passage_nodes(self, chunks: List[Any], paper_id: str, embeddings: List[List[float]] = None):
        """
        Create Passage nodes from text chunks.

        Args:
            chunks: List of TextChunk objects
            paper_id: ID of source paper
            embeddings: Optional pre-computed embeddings for chunks
        """
        for i, chunk in enumerate(chunks):
            chunk_id = f"{paper_id}_chunk_{chunk.chunk_id}"

            query = """
            MERGE (passage:Passage {id: $chunk_id})
            SET passage.text = $text,
                passage.page_num = $page_num,
                passage.chunk_id = $chunk_idx,
                passage.section = $section,
                passage.updated_at = datetime()

            WITH passage
            MATCH (p:Paper {id: $paper_id})
            MERGE (p)-[:HAS_PASSAGE]->(passage)
            """

            params = {
                'chunk_id': chunk_id,
                'text': chunk.text,
                'page_num': chunk.page_num,
                'chunk_idx': chunk.chunk_id,
                'section': chunk.section,
                'paper_id': paper_id
            }

            # Add embedding if available
            if embeddings and i < len(embeddings):
                query += "\nSET passage.embedding = $embedding"
                params['embedding'] = embeddings[i]

            self.db.execute_write(query, params)

        logger.info(f"Created {len(chunks)} passage nodes")

    def ingest_paper(self, extracted_data: Dict[str, Any], embeddings: List[List[float]] = None):
        """
        Ingest a complete paper into the knowledge graph.

        Args:
            extracted_data: Output from EntityExtractor.process_paper()
            embeddings: Optional embeddings for text chunks
        """
        # Create paper node
        paper_id = self.create_paper_node(extracted_data['paper_metadata'])

        # Create author nodes
        authors = extracted_data.get('authors', [])
        if authors:
            self.create_author_nodes(authors, paper_id)

        # Create concept/trait/architecture nodes
        entities = extracted_data.get('entities', [])
        if entities:
            self.create_concept_nodes(entities, paper_id)

        # Create relationships
        relationships = extracted_data.get('relationships', [])
        if relationships:
            self.create_relationships(relationships)

        # Create passage nodes
        chunks = extracted_data.get('chunks', [])
        if chunks:
            self.create_passage_nodes(chunks, paper_id, embeddings)

        logger.info(f"Successfully ingested paper: {extracted_data['paper_metadata'].title}")

        return paper_id

    @staticmethod
    def _generate_id(text: str) -> str:
        """Generate a deterministic ID from text."""
        return hashlib.md5(text.encode()).hexdigest()[:16]


if __name__ == "__main__":
    # Example usage
    from src.ingestion import PDFProcessor, EntityExtractor

    # Initialize components
    db = Neo4jConnection()
    processor = PDFProcessor()
    extractor = EntityExtractor()
    builder = KnowledgeGraphBuilder(db)

    # Process a paper
    # paper_data = processor.process_pdf("data/papers/example.pdf")
    # extracted = extractor.process_paper(paper_data)
    # paper_id = builder.ingest_paper(extracted)

    # print(f"Ingested paper with ID: {paper_id}")
