# Artificial Phronesis

**Mapping the Conceptual Landscape of Wisdom, Intelligence, and Their Artificial Counterparts**

A knowledge graph + GraphRAG system for exploring how wisdom, phronesis, sapience, intelligence, and their artificial instantiations connect across philosophy, psychology, and AI research.

![Knowledge Graph](https://img.shields.io/badge/Neo4j-5.15-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

**Artificial Phronesis** is a knowledge graph that maps the fractured conceptual space at the intersection of:
- **Human wisdom** (psychology & philosophy)
- **Artificial intelligence** (computer science)
- **Artificial wisdom** and **machine phronesis** (emerging interdisciplinary field)

Using **Neo4j** for graph storage and **GraphRAG** (graph-augmented retrieval) with LLMs, this project enables:
- ✅ Exploration of conceptual relationships and hierarchies
- ✅ Citation network analysis across disciplines
- ✅ Identification of research gaps (under-theorized connections)
- ✅ Natural language queries over structured + unstructured knowledge

## Why a Knowledge Graph?

The field of AI wisdom is **fragmented**:
- Psychologists study measurable wisdom traits (humility, perspective-taking, emotion regulation)
- Philosophers debate whether machines can possess phronesis (practical wisdom)
- AI researchers build metacognitive systems but often lack grounding in wisdom science

A knowledge graph lets us:
1. **Map overlaps and distinctions** between different conceptualizations
2. **Trace intellectual lineages** via citation networks
3. **Discover research gaps** where concepts are under-connected
4. **Query the landscape** using GraphRAG to answer complex questions

## Core Concepts

| Concept | Type | Description |
|---------|------|-------------|
| **Wisdom** | Human Trait | Meta-capacity combining cognitive, reflective, and affective traits toward balanced, pro-social judgment |
| **Phronesis** | Human Trait | Aristotelian practical wisdom—prudent judgment in particular contexts |
| **Intelligence** | Human Trait | Cognitive ability for learning, reasoning, problem-solving, and abstraction |
| **Sapience** | Meta-Concept | Higher-order wisdom; self-aware, value-aligned intelligence |
| **Artificial Intelligence** | Machine Construct | Computational systems capable of tasks requiring human-like intelligence |
| **Artificial Wisdom** | Machine Construct | AI systems exhibiting wisdom-like traits: metacognition, humility, pro-social orientation |
| **Machine Phronesis** | Machine Construct | AI instantiation of phronesis—context-sensitive ethical reasoning |
| **Computational Sapience** | Machine Construct | Self-reflective, value-aligned AI with metacognitive monitoring |

## Features

### 1. Knowledge Graph
- **Entities**: Concepts, Traits, Papers, Authors, Architectures
- **Relationships**: `SUBTYPE_OF`, `CONTRASTED_WITH`, `HAS_TRAIT`, `IMPLEMENTS_ASPECT_OF`, etc.
- **Schema-driven** with constraints and indexes for performance

### 2. GraphRAG Query Engine
- **Hybrid search**: Combine vector similarity (passages) + graph traversal (concepts)
- **LLM-powered Q&A**: Ask natural language questions with graph context
- **Subgraph extraction**: Focus on specific concepts and their neighborhoods

### 3. Interactive Web Interface
- **Landing page**: Interactive graph visualization (vis.js)
- **About page**: Project background and methodology
- **References page**: Dynamically loaded papers and authors
- **Natural language queries**: Ask questions directly in the UI

### 4. PDF Ingestion Pipeline
- **Automatic entity extraction** using LLMs (GPT-4)
- **Relationship extraction** from academic text
- **Vector embeddings** for semantic search
- **Metadata extraction**: Authors, year, abstract, DOI

## Architecture

```
Artificial-Phronesis/
├── data/
│   ├── papers/              # PDF papers to ingest
│   └── processed/           # Processed data
├── schema/
│   └── init_schema.cypher   # Graph schema + seed data
├── src/
│   ├── ingestion/           # PDF processing & entity extraction
│   │   ├── pdf_processor.py
│   │   ├── entity_extractor.py
│   │   └── kg_builder.py
│   ├── graphrag/            # GraphRAG query engine
│   │   └── query_engine.py
│   └── utils/               # Neo4j connection utilities
│       └── neo4j_connection.py
├── web/
│   ├── api/                 # FastAPI backend
│   │   └── main.py
│   ├── static/              # CSS, JavaScript
│   └── templates/           # HTML pages
├── scripts/
│   ├── init_database.py     # Initialize schema
│   └── ingest_papers.py     # Ingest PDF papers
├── queries/
│   └── example_queries.cypher  # Example Cypher queries
├── docker-compose.yml       # Neo4j database
├── requirements.txt
└── README.md
```

## Quick Start

### Prerequisites
- **Docker** and **Docker Compose** (for Neo4j)
- **Python 3.9+**
- **OpenAI API key** (for LLM-based entity extraction and GraphRAG)

### 1. Clone the Repository

```bash
git clone https://github.com/Chrisfoz/Artificial-Phronesis.git
cd Artificial-Phronesis
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Start Neo4j Database

```bash
docker-compose up -d
```

Neo4j will be available at:
- **Browser**: http://localhost:7474
- **Bolt**: bolt://localhost:7687
- **Credentials**: `neo4j` / `phronesis123`

### 4. Initialize the Database

```bash
python scripts/init_database.py
```

This creates the schema, constraints, indexes, and loads seed data (core concepts, traits, architectures).

### 5. Add Papers and Ingest

```bash
# Add PDF papers to data/papers/
# Then run ingestion:
python scripts/ingest_papers.py

# Optional: Skip embeddings for faster ingestion (no vector search)
python scripts/ingest_papers.py --no-embeddings
```

The ingestion script will:
1. Extract text from PDFs
2. Use GPT-4 to extract entities (concepts, traits, architectures)
3. Extract relationships
4. Generate embeddings for text chunks
5. Load everything into Neo4j

### 6. Launch Web Interface

```bash
cd web
uvicorn api.main:app --reload
```

Open http://localhost:8000 in your browser.

## Usage

### Web Interface

#### Landing Page
- **Interactive graph visualization** of the full knowledge graph
- **Focus mode**: Select a concept to see its subgraph
- **Natural language Q&A**: Ask questions like:
  - "How does artificial wisdom differ from artificial intelligence?"
  - "Which AI architectures implement metacognitive traits?"
  - "What are the key distinctions between wisdom and intelligence?"

#### About Page
- Project background and methodology
- Core concept definitions
- Research questions

#### References Page
- Dynamically loaded list of all papers in the graph
- Filter by domain or search by keyword
- Author collaboration networks

### Python API

```python
from src.utils.neo4j_connection import Neo4jConnection
from src.graphrag import GraphRAG

# Connect to Neo4j
db = Neo4jConnection()

# Initialize GraphRAG
graphrag = GraphRAG(db)

# Get concept details
wisdom = graphrag.get_concept_details("Wisdom")
print(wisdom)

# Hybrid search
results = graphrag.hybrid_search("What is artificial phronesis?")

# Ask a question
answer = graphrag.query_with_llm("How do current AI systems relate to wisdom?")
print(answer)
```

### Cypher Queries

See `queries/example_queries.cypher` for 20+ example queries:

```cypher
// Find wisdom traits not implemented by any AI architecture
MATCH (aw:Concept {name: "Artificial Wisdom"})-[:REQUIRES_TRAIT]->(t:Trait)
WHERE NOT EXISTS {
    MATCH (arch:Architecture)-[:IMPLEMENTS_ASPECT_OF]->(t)
}
RETURN t.name as unimplemented_trait, t.description;

// Find papers bridging psychology and AI
MATCH (p:Paper)-[:DISCUSSES]->(c1:Concept)
WHERE c1.domain CONTAINS 'psychology'
WITH p, collect(c1.name) as psych_concepts
MATCH (p)-[:DISCUSSES]->(c2:Concept)
WHERE c2.domain CONTAINS 'AI'
RETURN p.title, psych_concepts, collect(c2.name) as ai_concepts;
```

## Research Questions

This knowledge graph helps answer questions like:

1. **Conceptual fragmentation**: How do different disciplines define "artificial wisdom"?
2. **Implementation gaps**: Which wisdom traits are theorized but not operationalized in AI?
3. **Bridging literature**: Which papers connect psychological wisdom science to AI research?
4. **Architectural coverage**: Which AI systems already exhibit wisdom-like capabilities?
5. **Research opportunities**: Where are the under-theorized connections?

## Example Insights

After ingesting papers, you might discover:

- **Metacognition** is well-covered by self-rewarding LLMs and AI-Scientist, but lacks epistemic humility
- **Pro-social orientation** and **emotion regulation** are central to psychological wisdom but largely absent from AI architectures
- **Phronesis** (practical wisdom) requires context-sensitive ethical reasoning, which is still under-developed in current AI
- Papers on "artificial wisdom" cite psychological wisdom scales but rarely operationalize specific traits

## Data Schema

### Node Types
- **Concept**: Wisdom, Phronesis, AI, Artificial Wisdom, etc.
- **Trait**: Intellectual humility, metacognition, perspective-taking, etc.
- **Architecture**: Darwin Gödel Machine, Self-Rewarding LLM, AI Scientist, etc.
- **Paper**: Academic papers
- **Author**: Researchers
- **Passage**: Text chunks from papers (with embeddings)

### Relationship Types
- `SUBTYPE_OF`: Hierarchical relationships (e.g., Phronesis → Wisdom)
- `CONTRASTED_WITH`: Distinctions (e.g., Wisdom ↔ Intelligence)
- `HAS_TRAIT`: Concepts and their traits
- `REQUIRES_TRAIT`: Artificial constructs and needed traits
- `IMPLEMENTS_ASPECT_OF`: Architectures implementing traits
- `DISCUSSES`: Papers discussing concepts
- `AUTHORED`: Authors and their papers

## Technologies

- **Neo4j 5.15**: Graph database with APOC and GDS plugins
- **Python 3.9+**: Core processing logic
- **FastAPI**: Web backend
- **OpenAI GPT-4**: Entity extraction and Q&A
- **Sentence Transformers**: Local embeddings (optional)
- **Vis.js**: Interactive graph visualization
- **PyMuPDF / pdfplumber**: PDF text extraction

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Concepts Manually

```cypher
// Add a new concept
MERGE (c:Concept {name: "New Concept"})
SET c.type = "machine_construct",
    c.domain = "AI, philosophy",
    c.description = "Description here";

// Link to existing concept
MATCH (new:Concept {name: "New Concept"})
MATCH (existing:Concept {name: "Artificial Wisdom"})
MERGE (new)-[:SUBTYPE_OF]->(existing);
```

### Customizing Entity Extraction

Edit `src/ingestion/entity_extractor.py` to adjust:
- Prompt templates for entity/relationship extraction
- LLM model (e.g., switch to GPT-3.5 for cost)
- Entity types and relationship types

## Roadmap

- [x] Core knowledge graph schema
- [x] PDF ingestion pipeline
- [x] Entity and relationship extraction
- [x] GraphRAG query engine
- [x] Interactive web interface
- [ ] Temporal analysis (concept evolution over time)
- [ ] Citation network analysis (PageRank, betweenness centrality)
- [ ] Automated research gap detection
- [ ] Integration with arXiv / Semantic Scholar APIs
- [ ] Collaborative annotation interface
- [ ] Export to RDF/OWL for semantic web

## Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Suggested contributions**:
- Add more papers (especially foundational works)
- Improve entity extraction prompts
- Add new query examples
- Enhance visualizations
- Write tests

## Citation

If you use this project in your research, please cite:

```bibtex
@misc{artificial-phronesis-2024,
  title={Artificial Phronesis: A Knowledge Graph of Wisdom and Intelligence},
  author={},
  year={2024},
  howpublished={\url{https://github.com/Chrisfoz/Artificial-Phronesis}},
  note={Knowledge graph mapping conceptual relationships between wisdom, intelligence, and their artificial counterparts}
}
```

## Key References

Foundational papers included in the graph:

- **Jeste, D. V., Lee, E. E., & Cassidy, C. (2020).** Beyond artificial intelligence: exploring artificial wisdom. *International Psychogeriatrics, 32*(8), 993-1001.

- **Grossmann, I., & Johnson, S. (2025).** Imagining and building wise machines.

- **McGregor, S. (2025).** The Philosophy of Artificial Wisdom.

- **Tsai, C.** The Possibility of Artificial Phronesis.

- **Schmidhuber, J., et al. (2024).** Darwin Gödel Machines. *arXiv:2410.06087*.

- **Lu, C., et al. (2024).** The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contact

For questions, collaborations, or to contribute papers:
- **GitHub**: [Chrisfoz/Artificial-Phronesis](https://github.com/Chrisfoz/Artificial-Phronesis)
- **Issues**: [Report bugs or request features](https://github.com/Chrisfoz/Artificial-Phronesis/issues)

---

**Built with ❤️ for wisdom research and computational sapience**
