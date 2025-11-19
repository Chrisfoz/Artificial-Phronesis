"""
GraphRAG query engine - combines graph traversal with vector search and LLM reasoning.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

from src.utils.neo4j_connection import Neo4jConnection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphRAG:
    """GraphRAG query engine combining knowledge graph and vector search."""

    def __init__(self, neo4j_conn: Neo4jConnection, embedding_model: Optional[str] = None):
        """
        Initialize GraphRAG engine.

        Args:
            neo4j_conn: Neo4j database connection
            embedding_model: Model for embeddings (OpenAI or sentence-transformers)
        """
        load_dotenv()

        self.db = neo4j_conn
        self.embedding_model_name = embedding_model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

        # Initialize embedding model
        if HAS_OPENAI:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.use_openai = True
        elif HAS_SENTENCE_TRANSFORMERS:
            self.sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_openai = False
        else:
            raise ImportError("Need either OpenAI or sentence-transformers for embeddings")

        self.llm_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.use_openai:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model_name,
                input=text
            )
            return response.data[0].embedding
        else:
            return self.sentence_encoder.encode(text).tolist()

    def vector_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search on passages.

        Args:
            query: Query text
            top_k: Number of results to return

        Returns:
            List of matching passages with metadata
        """
        # Get query embedding
        query_embedding = self.get_embedding(query)

        # Vector search in Neo4j
        cypher = """
        CALL db.index.vector.queryNodes('passage_embeddings', $k, $query_embedding)
        YIELD node, score

        MATCH (p:Paper)-[:HAS_PASSAGE]->(node)
        RETURN
            node.text as text,
            node.chunk_id as chunk_id,
            p.title as paper_title,
            p.year as paper_year,
            p.authors_list as authors,
            score
        ORDER BY score DESC
        LIMIT $k
        """

        try:
            results = self.db.execute_query(cypher, {
                'query_embedding': query_embedding,
                'k': top_k
            })
            return results
        except Exception as e:
            logger.warning(f"Vector search failed (index may not exist yet): {e}")
            return []

    def graph_search(self, query: str, entity_types: List[str] = None) -> Dict[str, Any]:
        """
        Search for entities and their local graph neighborhoods.

        Args:
            query: Search query
            entity_types: Filter by entity types (Concept, Trait, Architecture)

        Returns:
            Subgraph containing matching entities and their relationships
        """
        # Full-text search for entities
        entity_filter = ""
        if entity_types:
            labels = "|".join(entity_types)
            entity_filter = f"AND n:{labels}"

        cypher = f"""
        CALL db.index.fulltext.queryNodes('concept_search', $query)
        YIELD node as n, score
        WHERE score > 0.5 {entity_filter}

        // Get the entity and its immediate neighborhood
        OPTIONAL MATCH (n)-[r1]-(neighbor)
        OPTIONAL MATCH (n)-[r2]-()-[r3]-(neighbor2)

        RETURN
            n as entity,
            labels(n) as entity_labels,
            collect(DISTINCT {{
                node: neighbor,
                labels: labels(neighbor),
                relationship: type(r1),
                direction: CASE WHEN startNode(r1) = n THEN 'out' ELSE 'in' END
            }}) as immediate_neighbors,
            collect(DISTINCT {{
                node: neighbor2,
                labels: labels(neighbor2)
            }}) as extended_neighbors,
            score
        ORDER BY score DESC
        LIMIT 10
        """

        results = self.db.execute_query(cypher, {'query': query})

        # Structure the subgraph
        entities = []
        relationships = []

        for record in results:
            entity = record['entity']
            entities.append({
                'id': entity.id,
                'labels': record['entity_labels'],
                'properties': dict(entity)
            })

            for neighbor in record['immediate_neighbors']:
                if neighbor['node']:
                    relationships.append({
                        'source': entity.id,
                        'target': neighbor['node'].id,
                        'type': neighbor['relationship'],
                        'direction': neighbor['direction']
                    })

        return {
            'entities': entities,
            'relationships': relationships,
            'entity_count': len(entities),
            'relationship_count': len(relationships)
        }

    def get_concept_details(self, concept_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific concept including traits and papers.

        Args:
            concept_name: Name of the concept

        Returns:
            Detailed concept information
        """
        cypher = """
        MATCH (c) WHERE c.name = $name

        // Get traits
        OPTIONAL MATCH (c)-[r:HAS_TRAIT|REQUIRES_TRAIT]->(t:Trait)

        // Get related architectures
        OPTIONAL MATCH (arch:Architecture)-[r2:IMPLEMENTS_ASPECT_OF|ORIENTED_TOWARD]->(c)

        // Get papers discussing this concept
        OPTIONAL MATCH (p:Paper)-[:DISCUSSES]->(c)

        // Get contrasted concepts
        OPTIONAL MATCH (c)-[r3:CONTRASTED_WITH]-(other)

        RETURN
            c as concept,
            labels(c) as labels,
            collect(DISTINCT {name: t.name, type: type(r), description: t.description}) as traits,
            collect(DISTINCT {name: arch.name, relationship: type(r2)}) as architectures,
            collect(DISTINCT {title: p.title, year: p.year}) as papers,
            collect(DISTINCT {name: other.name, basis: r3.basis}) as contrasts
        """

        results = self.db.execute_query(cypher, {'name': concept_name})

        if not results:
            return {}

        record = results[0]
        concept = record['concept']

        return {
            'name': concept.get('name'),
            'type': concept.get('type'),
            'domain': concept.get('domain'),
            'description': concept.get('description'),
            'short_def': concept.get('short_def'),
            'labels': record['labels'],
            'traits': [t for t in record['traits'] if t['name']],
            'architectures': [a for a in record['architectures'] if a['name']],
            'papers': [p for p in record['papers'] if p['title']],
            'contrasts': [c for c in record['contrasts'] if c['name']]
        }

    def hybrid_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Combine vector search and graph search.

        Args:
            query: Query text
            top_k: Number of results

        Returns:
            Combined search results
        """
        # Vector search for relevant passages
        passages = self.vector_search(query, top_k)

        # Graph search for relevant concepts
        graph_results = self.graph_search(query)

        return {
            'passages': passages,
            'subgraph': graph_results,
            'query': query
        }

    def query_with_llm(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Answer a question using LLM with graph context.

        Args:
            question: User's question
            context: Optional pre-fetched context (from hybrid_search)

        Returns:
            LLM-generated answer
        """
        if not HAS_OPENAI:
            return "OpenAI not available for LLM queries"

        # Get context if not provided
        if context is None:
            context = self.hybrid_search(question, top_k=5)

        # Build context string
        context_parts = []

        # Add passages
        if context.get('passages'):
            context_parts.append("## Relevant Passages:\n")
            for i, passage in enumerate(context['passages'][:3]):
                context_parts.append(
                    f"\n{i+1}. From '{passage['paper_title']}' ({passage['paper_year']}):\n"
                    f"{passage['text'][:500]}...\n"
                )

        # Add concept information
        if context.get('subgraph', {}).get('entities'):
            context_parts.append("\n## Relevant Concepts:\n")
            for entity in context['subgraph']['entities'][:5]:
                props = entity['properties']
                context_parts.append(
                    f"\n- {props.get('name', 'Unknown')}: {props.get('description', 'No description')}\n"
                )

        context_str = "\n".join(context_parts)

        # Query LLM
        prompt = f"""You are an expert on wisdom, artificial intelligence, and philosophy.

Use the following context from a knowledge graph of academic papers to answer the question.
Cite specific papers or concepts when relevant.

Context:
{context_str}

Question: {question}

Answer:"""

        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are an expert researcher in philosophy, psychology, and AI. Answer questions based on the provided academic context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    # Example usage
    db = Neo4jConnection()
    graphrag = GraphRAG(db)

    # Search for concept
    wisdom_details = graphrag.get_concept_details("Wisdom")
    print("Wisdom concept:", wisdom_details)

    # Hybrid search
    results = graphrag.hybrid_search("What is artificial wisdom?")
    print(f"\nFound {len(results['passages'])} passages")
    print(f"Found {results['subgraph']['entity_count']} entities")

    # Query with LLM
    answer = graphrag.query_with_llm("How does artificial wisdom differ from artificial intelligence?")
    print(f"\nAnswer: {answer}")
