"""
Hybrid RAG combining Google File Search with Neo4j Knowledge Graph.

Uses Google File Search for document retrieval and Neo4j for conceptual relationships.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

from src.utils.neo4j_connection import Neo4jConnection
from src.graphrag.google_file_search import GoogleFileSearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HybridRAG:
    """
    Hybrid RAG system combining:
    - Google File Search: Document retrieval and semantic search
    - Neo4j Knowledge Graph: Conceptual relationships and structure
    """

    def __init__(self, neo4j_conn: Neo4jConnection, google_api_key: Optional[str] = None):
        """
        Initialize Hybrid RAG.

        Args:
            neo4j_conn: Neo4j database connection
            google_api_key: Google API key (optional)
        """
        load_dotenv()

        self.db = neo4j_conn
        self.gfs = GoogleFileSearch(api_key=google_api_key)

        logger.info("Initialized Hybrid RAG with Google File Search + Neo4j")

    def get_concept_context(self, concept_name: str) -> Dict[str, Any]:
        """
        Get structured context about a concept from the knowledge graph.

        Args:
            concept_name: Name of the concept

        Returns:
            Concept details including traits, relationships, and papers
        """
        cypher = """
        MATCH (c) WHERE c.name = $name

        // Get traits
        OPTIONAL MATCH (c)-[r:HAS_TRAIT|REQUIRES_TRAIT]->(t:Trait)

        // Get related concepts
        OPTIONAL MATCH (c)-[r2:SUBTYPE_OF|CONTRASTED_WITH|ANALOGY_TO]-(related:Concept)

        // Get architectures
        OPTIONAL MATCH (arch:Architecture)-[r3:IMPLEMENTS_ASPECT_OF|ORIENTED_TOWARD]->(c)

        // Get papers
        OPTIONAL MATCH (p:Paper)-[:DISCUSSES]->(c)

        RETURN
            c as concept,
            labels(c) as labels,
            collect(DISTINCT {name: t.name, type: type(r), description: t.description}) as traits,
            collect(DISTINCT {name: related.name, relationship: type(r2)}) as related_concepts,
            collect(DISTINCT {name: arch.name, relationship: type(r3)}) as architectures,
            collect(DISTINCT {title: p.title, year: p.year, id: p.id}) as papers
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
            'related_concepts': [r for r in record['related_concepts'] if r['name']],
            'architectures': [a for a in record['architectures'] if a['name']],
            'papers': [p for p in record['papers'] if p['title']]
        }

    def query_with_context(
        self,
        question: str,
        concepts: Optional[List[str]] = None,
        include_graph_context: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using both document search and knowledge graph context.

        Args:
            question: User's question
            concepts: Optional list of concepts to focus on
            include_graph_context: Whether to include graph structure in context

        Returns:
            Answer with sources and graph context
        """
        logger.info(f"Hybrid query: {question}")

        # Build enhanced prompt with graph context
        enhanced_prompt = question

        if include_graph_context and concepts:
            # Get graph context for relevant concepts
            graph_context_parts = []

            for concept in concepts:
                context = self.get_concept_context(concept)
                if context:
                    context_str = f"\n\n## Knowledge Graph Context for {concept}:"
                    context_str += f"\n- Definition: {context.get('description', 'N/A')}"

                    if context.get('traits'):
                        traits_list = [t['name'] for t in context['traits']]
                        context_str += f"\n- Key Traits: {', '.join(traits_list)}"

                    if context.get('related_concepts'):
                        related = [f"{r['name']} ({r['relationship']})" for r in context['related_concepts']]
                        context_str += f"\n- Related Concepts: {', '.join(related)}"

                    if context.get('architectures'):
                        archs = [a['name'] for a in context['architectures']]
                        context_str += f"\n- Relevant AI Systems: {', '.join(archs)}"

                    graph_context_parts.append(context_str)

            if graph_context_parts:
                enhanced_prompt = question + "\n" + "\n".join(graph_context_parts)

        # Query Google File Search with enhanced context
        result = self.gfs.search_documents(enhanced_prompt, include_citations=True)

        # Add graph context to response
        if include_graph_context and concepts:
            result['graph_context'] = [self.get_concept_context(c) for c in concepts]

        return result

    def compare_concepts(self, concept1: str, concept2: str) -> Dict[str, Any]:
        """
        Compare two concepts using both documents and knowledge graph.

        Args:
            concept1: First concept
            concept2: Second concept

        Returns:
            Comparison with document analysis and graph structure
        """
        logger.info(f"Comparing concepts: {concept1} vs {concept2}")

        # Get graph context for both concepts
        context1 = self.get_concept_context(concept1)
        context2 = self.get_concept_context(concept2)

        # Build comparison prompt
        prompt = f"""Compare and contrast {concept1} and {concept2} based on the academic literature.

Knowledge Graph Context:

{concept1}:
- Type: {context1.get('type', 'N/A')}
- Domain: {context1.get('domain', 'N/A')}
- Traits: {', '.join([t['name'] for t in context1.get('traits', [])])}

{concept2}:
- Type: {context2.get('type', 'N/A')}
- Domain: {context2.get('domain', 'N/A')}
- Traits: {', '.join([t['name'] for t in context2.get('traits', [])])}

Please provide:
1. How each concept is defined across different papers
2. Key differences and similarities in traits and capabilities
3. Disciplinary perspectives
4. Implementation status (for artificial constructs)
5. Specific citations from the papers
"""

        # Query documents
        result = self.gfs.search_documents(prompt, include_citations=True)

        # Add graph context
        result['graph_context'] = {
            concept1: context1,
            concept2: context2
        }

        return result

    def find_implementation_gaps(self, concept: str) -> Dict[str, Any]:
        """
        Identify implementation gaps for an artificial construct.

        Args:
            concept: Concept to analyze (e.g., "Artificial Wisdom")

        Returns:
            Gap analysis with graph and document insights
        """
        logger.info(f"Finding implementation gaps for: {concept}")

        # Get concept context
        context = self.get_concept_context(concept)

        # Identify required traits from graph
        required_traits = [t['name'] for t in context.get('traits', []) if 'REQUIRES' in t.get('type', '')]

        # Identify implemented traits from architectures
        architectures = context.get('architectures', [])

        # Build gap analysis prompt
        prompt = f"""Analyze implementation gaps for {concept} based on the academic literature.

Knowledge Graph shows {concept} requires these traits:
{', '.join(required_traits)}

Current AI systems mentioned:
{', '.join([a['name'] for a in architectures])}

Please identify:
1. Which required traits are well-implemented in current AI systems
2. Which traits are theorized but not yet operationalized
3. Which traits are completely missing
4. Technical challenges for implementing missing traits
5. Research opportunities

Cite specific papers and systems."""

        # Query documents
        result = self.gfs.search_documents(prompt, include_citations=True)

        # Add structured gap analysis from graph
        result['graph_analysis'] = {
            'required_traits': required_traits,
            'current_architectures': [a['name'] for a in architectures],
            'trait_count': len(required_traits),
            'architecture_count': len(architectures)
        }

        return result

    def explore_concept_neighborhood(self, concept: str, depth: int = 2) -> Dict[str, Any]:
        """
        Explore a concept's neighborhood in the knowledge graph.

        Args:
            concept: Concept to explore
            depth: How many hops to traverse

        Returns:
            Subgraph with document insights
        """
        logger.info(f"Exploring neighborhood of: {concept}")

        # Get neighborhood from graph
        cypher = f"""
        MATCH path = (c {{name: $name}})-[*1..{depth}]-(related)
        WHERE c:Concept OR c:Trait OR c:Architecture

        WITH c, collect(DISTINCT related) as neighbors

        RETURN
            c.name as center_concept,
            [n in neighbors | {{name: n.name, labels: labels(n)}}] as neighborhood
        """

        result = self.db.execute_query(cypher, {'name': concept})

        if not result:
            return {'neighborhood': [], 'insights': 'Concept not found in knowledge graph.'}

        neighborhood = result[0]['neighborhood']

        # Build exploration prompt
        neighbor_names = [n['name'] for n in neighborhood if n.get('name')]

        prompt = f"""Explore the conceptual landscape around {concept} based on the academic papers.

The knowledge graph shows {concept} is connected to:
{', '.join(neighbor_names[:20])}  # Limit to avoid too long prompt

Please discuss:
1. How {concept} relates to these connected concepts
2. Which connections are well-theorized in the literature
3. Which connections are mentioned but under-explored
4. Opportunities for integrating insights across concepts

Cite relevant papers."""

        # Query documents
        doc_result = self.gfs.search_documents(prompt, include_citations=True)

        doc_result['graph_neighborhood'] = neighborhood

        return doc_result

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the hybrid system."""
        # Neo4j stats
        graph_info = self.db.get_schema_info()

        # Google File Search stats
        files = self.gfs.list_files()

        return {
            'knowledge_graph': {
                'nodes': graph_info['node_count'],
                'relationships': graph_info['relationship_count'],
                'labels': graph_info['node_labels']
            },
            'document_corpus': {
                'file_count': len(files),
                'files': [f['display_name'] for f in files]
            }
        }


if __name__ == "__main__":
    # Example usage
    from src.utils.neo4j_connection import Neo4jConnection

    db = Neo4jConnection()
    hybrid_rag = HybridRAG(db)

    # Query with graph context
    result = hybrid_rag.query_with_context(
        "What is artificial wisdom?",
        concepts=["Artificial Wisdom", "Wisdom"]
    )
    print(result['answer'])

    # Compare concepts
    comparison = hybrid_rag.compare_concepts("Wisdom", "Intelligence")
    print(comparison['answer'])

    # Find gaps
    gaps = hybrid_rag.find_implementation_gaps("Artificial Wisdom")
    print(gaps['answer'])
