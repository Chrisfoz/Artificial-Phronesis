# Google File Search Integration Guide

This guide explains how to use Google's powerful File Search API for document-based RAG (Retrieval-Augmented Generation) in the Artificial Phronesis project.

## Overview

Artificial Phronesis now supports **hybrid RAG** combining:
1. **Google File Search**: Advanced document indexing and semantic retrieval using Gemini
2. **Neo4j Knowledge Graph**: Structured conceptual relationships and entity mapping

This combination provides:
- **Powerful document search** powered by Google's latest Gemini models
- **Structured knowledge** from the Neo4j graph
- **Context-aware answers** combining both sources

## Setup

### 1. Get Google API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your keys
nano .env
```

In `.env`:
```bash
# Google AI Configuration (primary RAG system)
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_MODEL=gemini-1.5-pro-latest

# RAG Configuration
RAG_PROVIDER=google  # Use Google File Search
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-generativeai` - Google's Gemini SDK
- `langchain-google-genai` - LangChain integration (optional)

## Usage

### Upload Papers to Google File Search

```bash
# Upload all PDFs from data/papers/
make upload-google

# Or directly:
python scripts/upload_to_google.py
```

The script will:
1. Find all PDFs in `data/papers/`
2. Upload them to Google's File API
3. Wait for processing (automatic chunking and indexing)
4. Return file URIs for querying

### List Uploaded Files

```bash
# List all files in Google File Search
make list-google

# Or directly:
python scripts/upload_to_google.py --list
```

### Delete All Files (Use with Caution!)

```bash
python scripts/upload_to_google.py --clear
```

### Query Documents

#### Via Python API

```python
from src.graphrag import HybridRAG
from src.utils.neo4j_connection import Neo4jConnection

# Initialize
db = Neo4jConnection()
hybrid_rag = HybridRAG(db)

# Simple query
result = hybrid_rag.query_with_context(
    "What is artificial wisdom?",
    concepts=["Artificial Wisdom", "Wisdom"]
)
print(result['answer'])

# Compare concepts
comparison = hybrid_rag.compare_concepts("Wisdom", "Intelligence")
print(comparison['answer'])

# Find implementation gaps
gaps = hybrid_rag.find_implementation_gaps("Artificial Wisdom")
print(gaps['answer'])
```

#### Via Web Interface

1. Start the web server:
```bash
make web
```

2. Visit http://localhost:8000

3. Use the "Ask a Question" feature on the landing page

4. Questions like:
   - "How does artificial wisdom differ from artificial intelligence?"
   - "Which AI architectures implement metacognitive traits?"
   - "What are the key traits of phronesis?"

### Advanced Queries

#### Concept Comparison (API)

```bash
curl -X POST http://localhost:8000/api/google/compare \
  -H "Content-Type: application/json" \
  -d '{
    "concept1": "Wisdom",
    "concept2": "Intelligence"
  }'
```

#### Gap Analysis (API)

```bash
curl -X POST http://localhost:8000/api/google/gaps \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Artificial Wisdom"
  }'
```

#### System Info

```bash
curl http://localhost:8000/api/system/info
```

## Architecture

### How Hybrid RAG Works

```
User Question
     │
     ├─→ Extract relevant concepts (e.g., "wisdom", "phronesis")
     │
     ├─→ Query Neo4j for graph context
     │    ├─ Concept definitions
     │    ├─ Related traits
     │    ├─ Architectural implementations
     │    └─ Relationship patterns
     │
     ├─→ Build enhanced prompt with graph context
     │
     ├─→ Query Google File Search with enhanced prompt
     │    ├─ Semantic search across all uploaded PDFs
     │    ├─ Automatic relevance ranking
     │    └─ Citation extraction
     │
     └─→ Combine graph structure + document insights
          └─ Return comprehensive answer with sources
```

### Benefits Over Traditional RAG

| Feature | Traditional RAG | Google File Search + Neo4j |
|---------|----------------|----------------------------|
| Document Search | Basic vector similarity | Advanced semantic understanding (Gemini) |
| Structured Knowledge | None | Full knowledge graph with relationships |
| Citation Quality | Basic | Automatic with Gemini's citation capabilities |
| Context Integration | Flat | Multi-level (documents + graph structure) |
| Conceptual Reasoning | Limited | Graph-enhanced reasoning |

## Python API Reference

### GoogleFileSearch

```python
from src.graphrag import GoogleFileSearch

gfs = GoogleFileSearch()

# Upload file
file_metadata = gfs.upload_file("path/to/paper.pdf")

# Upload directory
uploaded = gfs.upload_directory("data/papers", "*.pdf")

# List files
files = gfs.list_files()

# Query documents
answer = gfs.query("What is artificial wisdom?")

# Compare concepts
comparison = gfs.compare_concepts("Wisdom", "Phronesis")

# Find gaps
gaps = gfs.find_gaps("Artificial Wisdom")
```

### HybridRAG

```python
from src.graphrag import HybridRAG
from src.utils.neo4j_connection import Neo4jConnection

db = Neo4jConnection()
hybrid = HybridRAG(db)

# Query with graph context
result = hybrid.query_with_context(
    question="What traits define wisdom?",
    concepts=["Wisdom"],
    include_graph_context=True
)

# Compare concepts (uses both Google + Neo4j)
comparison = hybrid.compare_concepts("Wisdom", "Intelligence")

# Find implementation gaps
gaps = hybrid.find_implementation_gaps("Artificial Wisdom")

# Explore concept neighborhood
neighborhood = hybrid.explore_concept_neighborhood("Phronesis", depth=2)

# Get statistics
stats = hybrid.get_statistics()
```

## Best Practices

### 1. Upload Strategy

- **Keep files current**: Re-upload when papers are updated
- **Organize by topic**: You can filter by file URIs
- **Remove old versions**: Use `--clear` to reset

### 2. Query Optimization

- **Be specific**: More specific questions get better answers
- **Use concept names**: Mention concepts like "Wisdom", "Phronesis" explicitly
- **Request citations**: Ask for specific papers or authors

### 3. Graph + Document Synergy

The system works best when you:
1. Initialize Neo4j schema (conceptual structure)
2. Upload papers to Google (document content)
3. Optionally ingest entities to Neo4j (link concepts to papers)

This gives you:
- **Fast document search** (Google)
- **Structured reasoning** (Neo4j)
- **Citation tracking** (both)

## Troubleshooting

### File Upload Fails

**Error**: `File processing failed`

**Solution**:
- Check file format (PDF only)
- Ensure file is not corrupted
- Check file size (max 100MB per file)

### API Key Issues

**Error**: `GOOGLE_API_KEY not found`

**Solution**:
```bash
# Make sure .env is configured
cat .env | grep GOOGLE_API_KEY

# Should show:
# GOOGLE_API_KEY=your-actual-key-here
```

### RAG Provider Not Enabled

**Error**: `Google File Search not enabled`

**Solution**:
```bash
# Check .env
RAG_PROVIDER=google  # Must be set to 'google'
GOOGLE_API_KEY=your-key-here  # Must be present
```

### Slow Queries

If queries are slow:
1. Google File Search scales with document count
2. Consider filtering by specific file URIs
3. Use more specific questions
4. Check network connectivity to Google APIs

## Cost Considerations

Google File Search (Gemini API) pricing:
- **File upload**: Free
- **Storage**: Free (temporary - files expire after 48 hours)
- **Queries**: Based on Gemini API pricing
  - Input tokens: ~$0.35 per 1M tokens
  - Output tokens: ~$1.05 per 1M tokens

**Typical usage**:
- 10 papers uploaded
- 20 queries per day
- ~$0.10-0.50 per day

See [Google AI Pricing](https://ai.google.dev/pricing) for current rates.

## Examples

### Example 1: Compare Wisdom Constructs

```python
from src.graphrag import HybridRAG
from src.utils.neo4j_connection import Neo4jConnection

db = Neo4jConnection()
hybrid = HybridRAG(db)

result = hybrid.compare_concepts("Wisdom", "Artificial Wisdom")

print(result['answer'])
# Output: Comprehensive comparison citing specific papers,
# highlighting differences in traits, disciplinary perspectives,
# and implementation status
```

### Example 2: Research Gap Analysis

```python
gaps = hybrid.find_implementation_gaps("Computational Sapience")

print(f"Required traits: {gaps['graph_analysis']['required_traits']}")
print(f"\nGap analysis:\n{gaps['answer']}")

# Shows which traits are theorized but not implemented
```

### Example 3: Concept Exploration

```python
exploration = hybrid.explore_concept_neighborhood("Phronesis", depth=2)

print(f"Connected concepts: {exploration['graph_neighborhood']}")
print(f"\nInsights from papers:\n{exploration['answer']}")
```

## Next Steps

1. **Try it out**: Upload your first papers with `make upload-google`
2. **Experiment**: Ask different types of questions
3. **Compare**: Try both Google RAG and OpenAI RAG (set `RAG_PROVIDER=openai`)
4. **Extend**: Add more papers to build a comprehensive corpus
5. **Share**: Use the insights to share with leading minds in your field

## Resources

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Neo4j Cypher Guide](https://neo4j.com/docs/cypher-manual/)
- [Artificial Phronesis README](../README.md)
