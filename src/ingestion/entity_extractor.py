"""
Entity and relationship extraction using LLMs.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extract entities and relationships from academic text using LLMs."""

    def __init__(self, model: Optional[str] = None):
        """
        Initialize entity extractor.

        Args:
            model: OpenAI model to use (default from env)
        """
        load_dotenv()

        if not HAS_OPENAI:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")

        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    def extract_concepts(self, text: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Extract conceptual entities (Wisdom, Phronesis, AI, etc.) from text.

        Args:
            text: Text to analyze
            context: Additional context (e.g., paper metadata)

        Returns:
            List of extracted concepts with properties
        """
        prompt = f"""You are analyzing an academic paper about wisdom, intelligence, and artificial intelligence.

Extract all conceptual entities mentioned in this text. Focus on:
- Concepts: Wisdom, Phronesis, Sapience, Intelligence, Artificial Intelligence, Artificial Wisdom, Machine Phronesis, Computational Sapience
- Traits: intellectual humility, perspective-taking, emotion regulation, metacognition, etc.
- Architectures: specific AI systems or frameworks mentioned

For each entity, provide:
1. name: The concept name
2. type: One of [concept, trait, architecture]
3. description: Brief description from the text
4. domain: The field(s) it belongs to (psychology, philosophy, AI, etc.)

Return ONLY a valid JSON array of objects. No additional text.

Text:
{text[:4000]}

JSON output:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in philosophy, psychology, and AI. Extract structured knowledge from academic texts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result = response.choices[0].message.content.strip()

            # Parse JSON
            # Sometimes the model includes markdown code blocks
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            entities = json.loads(result)
            return entities

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response was: {result}")
            return []
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    def extract_relationships(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities.

        Args:
            text: Text to analyze
            entities: Previously extracted entities

        Returns:
            List of relationships
        """
        entity_names = [e['name'] for e in entities]

        prompt = f"""You are analyzing relationships between concepts in an academic paper.

Here are the entities found in this text:
{json.dumps(entity_names, indent=2)}

Extract relationships between these entities from the following text. Focus on:
- SUBTYPE_OF: One concept is a specific type of another
- CONTRASTED_WITH: Concepts are distinguished or opposed
- HAS_TRAIT: A concept possesses a specific trait
- REQUIRES_TRAIT: A concept needs a trait to be realized
- IMPLEMENTS_ASPECT_OF: An architecture implements some aspect of a trait/concept
- ORIENTED_TOWARD: An architecture is designed for a concept
- ANALOGY_TO: One concept is analogous to another

For each relationship, provide:
1. source: Name of source entity
2. relationship: Relationship type (from list above)
3. target: Name of target entity
4. properties: Any additional properties (e.g., {{"basis": "explanation"}})

Return ONLY a valid JSON array. No additional text.

Text:
{text[:4000]}

JSON output:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in knowledge graphs and conceptual relationships."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result = response.choices[0].message.content.strip()

            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            relationships = json.loads(result)
            return relationships

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        except Exception as e:
            logger.error(f"Relationship extraction failed: {e}")
            return []

    def extract_authors_and_citations(self, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract author information and citations from paper text.

        Args:
            text: Full paper text
            metadata: Paper metadata

        Returns:
            Dictionary with authors and cited works
        """
        # Use first 3000 chars (usually contains authors and early citations)
        sample = text[:3000]

        prompt = f"""Extract author information from this academic paper text.

Provide:
1. authors: List of author names (just names, no affiliations)
2. cited_works: List of key works cited (title and year if available)

Return ONLY valid JSON.

Text:
{sample}

JSON output:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting bibliographic information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )

            result = response.choices[0].message.content.strip()

            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()

            return json.loads(result)

        except Exception as e:
            logger.error(f"Author extraction failed: {e}")
            return {"authors": [], "cited_works": []}

    def process_paper(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete paper and extract all entities and relationships.

        Args:
            paper_data: Output from PDFProcessor.process_pdf()

        Returns:
            Extracted knowledge graph elements
        """
        logger.info(f"Extracting entities from paper: {paper_data['metadata'].title}")

        # Extract from full text (or a sample if too long)
        text_sample = paper_data['full_text'][:8000]  # First 8000 chars

        # Extract entities
        entities = self.extract_concepts(text_sample, context={'metadata': paper_data['metadata']})

        # Extract relationships
        relationships = self.extract_relationships(text_sample, entities)

        # Extract authors and citations
        author_info = self.extract_authors_and_citations(paper_data['full_text'], paper_data['metadata'])

        return {
            'paper_metadata': paper_data['metadata'],
            'entities': entities,
            'relationships': relationships,
            'authors': author_info.get('authors', []),
            'cited_works': author_info.get('cited_works', []),
            'chunks': paper_data['chunks']
        }


if __name__ == "__main__":
    # Example usage
    extractor = EntityExtractor()

    sample_text = """
    Wisdom is distinguished from intelligence by its focus on prudential judgment
    rather than technical problem-solving. Artificial wisdom extends these capacities
    to machine systems, requiring traits like intellectual humility and metacognition.
    """

    entities = extractor.extract_concepts(sample_text)
    print("Entities:", json.dumps(entities, indent=2))

    relationships = extractor.extract_relationships(sample_text, entities)
    print("Relationships:", json.dumps(relationships, indent=2))
