"""
FastAPI backend for Artificial Phronesis web interface.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from src.utils.neo4j_connection import Neo4jConnection
from src.graphrag import GraphRAG, HybridRAG

import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Artificial Phronesis Knowledge Graph",
    description="Exploring the conceptual landscape of wisdom, intelligence, and their artificial counterparts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# Initialize database connection
db = None
graphrag = None
hybrid_rag = None
use_google_rag = False


@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup."""
    global db, graphrag, hybrid_rag, use_google_rag
    try:
        db = Neo4jConnection()

        # Check which RAG provider to use
        rag_provider = os.getenv("RAG_PROVIDER", "google").lower()

        if rag_provider == "google" and os.getenv("GOOGLE_API_KEY"):
            try:
                hybrid_rag = HybridRAG(db)
                use_google_rag = True
                logger.info("Initialized Hybrid RAG with Google File Search")
            except Exception as e:
                logger.warning(f"Failed to initialize Google File Search: {e}")
                logger.info("Falling back to standard GraphRAG")
                graphrag = GraphRAG(db)
        else:
            graphrag = GraphRAG(db)
            logger.info("Initialized standard GraphRAG")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    global db
    if db:
        db.close()
        logger.info("Database connections closed")


# ============================================
# Pydantic Models
# ============================================

class ConceptQuery(BaseModel):
    name: str


class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5


class QuestionQuery(BaseModel):
    question: str


# ============================================
# HTML Pages
# ============================================

@app.get("/")
async def landing_page(request: Request):
    """Render landing page with interactive graph."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about")
async def about_page(request: Request):
    """Render about page."""
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/references")
async def references_page(request: Request):
    """Render references page."""
    return templates.TemplateResponse("references.html", {"request": request})


# ============================================
# API Endpoints
# ============================================

@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """Get database statistics."""
    try:
        info = db.get_schema_info()
        return {
            "node_count": info["node_count"],
            "relationship_count": info["relationship_count"],
            "node_labels": info["node_labels"],
            "relationship_types": info["relationship_types"]
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/concepts")
async def get_all_concepts() -> List[Dict[str, Any]]:
    """Get all concepts in the knowledge graph."""
    try:
        query = """
        MATCH (c:Concept)
        RETURN c.name as name, c.type as type, c.domain as domain, c.short_def as short_def
        ORDER BY c.name
        """
        results = db.execute_query(query)
        return results
    except Exception as e:
        logger.error(f"Error getting concepts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/concept/{concept_name}")
async def get_concept(concept_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific concept."""
    try:
        details = graphrag.get_concept_details(concept_name)
        if not details:
            raise HTTPException(status_code=404, detail=f"Concept '{concept_name}' not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting concept details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph/full")
async def get_full_graph() -> Dict[str, Any]:
    """Get the complete knowledge graph for visualization."""
    try:
        # Get all nodes and relationships
        query = """
        // Get all nodes
        MATCH (n)
        WHERE n:Concept OR n:Trait OR n:Architecture
        WITH collect({
            id: id(n),
            label: labels(n)[0],
            name: n.name,
            type: n.type,
            domain: n.domain,
            description: n.description,
            short_def: n.short_def
        }) as nodes

        // Get all relationships
        MATCH (source)-[r]->(target)
        WHERE (source:Concept OR source:Trait OR source:Architecture)
          AND (target:Concept OR target:Trait OR target:Architecture)
        WITH nodes, collect({
            source: id(source),
            target: id(target),
            type: type(r),
            properties: properties(r)
        }) as relationships

        RETURN nodes, relationships
        """

        result = db.execute_query(query)

        if result:
            return {
                "nodes": result[0]["nodes"],
                "edges": result[0]["relationships"]
            }
        else:
            return {"nodes": [], "edges": []}

    except Exception as e:
        logger.error(f"Error getting full graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph/concept/{concept_name}")
async def get_concept_subgraph(concept_name: str, depth: int = 2) -> Dict[str, Any]:
    """Get a subgraph centered on a specific concept."""
    try:
        query = f"""
        MATCH (c {{name: $name}})
        CALL apoc.path.subgraphAll(c, {{
            maxLevel: $depth,
            relationshipFilter: "HAS_TRAIT>|REQUIRES_TRAIT>|CONTRASTED_WITH|SUBTYPE_OF>|IMPLEMENTS_ASPECT_OF>"
        }})
        YIELD nodes, relationships

        RETURN
            [n in nodes | {{
                id: id(n),
                label: labels(n)[0],
                name: n.name,
                type: n.type,
                description: n.description
            }}] as nodes,
            [r in relationships | {{
                source: id(startNode(r)),
                target: id(endNode(r)),
                type: type(r)
            }}] as edges
        """

        result = db.execute_query(query, {"name": concept_name, "depth": depth})

        if result:
            return {
                "nodes": result[0]["nodes"],
                "edges": result[0]["edges"]
            }
        else:
            return {"nodes": [], "edges": []}

    except Exception as e:
        logger.error(f"Error getting concept subgraph: {e}")
        # Fallback to simpler query without APOC
        query = """
        MATCH (c {name: $name})
        OPTIONAL MATCH path = (c)-[r*1..2]-(related)
        WITH c, collect(DISTINCT related) as related_nodes, collect(DISTINCT r) as rels

        RETURN
            [{id: id(c), label: labels(c)[0], name: c.name, type: c.type}] +
            [n in related_nodes | {id: id(n), label: labels(n)[0], name: n.name, type: n.type}] as nodes,
            [] as edges
        """
        result = db.execute_query(query, {"name": concept_name})
        if result:
            return {"nodes": result[0]["nodes"], "edges": result[0]["edges"]}
        return {"nodes": [], "edges": []}


@app.post("/api/search")
async def search(query: SearchQuery) -> Dict[str, Any]:
    """Perform hybrid search across the knowledge graph."""
    try:
        results = graphrag.hybrid_search(query.query, top_k=query.top_k)
        return results
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ask")
async def ask_question(query: QuestionQuery) -> Dict[str, Any]:
    """Ask a question and get an LLM-powered answer using graph context."""
    try:
        if use_google_rag and hybrid_rag:
            # Use Google File Search + Knowledge Graph
            # Try to extract relevant concepts from the question
            concepts = []
            concept_keywords = [
                "wisdom", "phronesis", "intelligence", "sapience",
                "artificial wisdom", "artificial intelligence",
                "machine phronesis", "computational sapience"
            ]

            question_lower = query.question.lower()
            for keyword in concept_keywords:
                if keyword in question_lower:
                    # Capitalize first letter of each word
                    concepts.append(keyword.title())

            result = hybrid_rag.query_with_context(
                query.question,
                concepts=concepts if concepts else None,
                include_graph_context=True
            )

            return {
                "question": query.question,
                "answer": result['answer'],
                "sources": result.get('sources', []),
                "provider": "Google File Search + Neo4j"
            }
        else:
            # Fallback to standard GraphRAG
            answer = graphrag.query_with_llm(query.question)
            return {
                "question": query.question,
                "answer": answer,
                "provider": "OpenAI + Neo4j"
            }
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/papers")
async def get_papers() -> List[Dict[str, Any]]:
    """Get all papers in the knowledge graph."""
    try:
        query = """
        MATCH (p:Paper)
        OPTIONAL MATCH (p)-[:DISCUSSES]->(c:Concept)
        RETURN
            p.title as title,
            p.year as year,
            p.authors_list as authors,
            p.abstract as abstract,
            p.venue as venue,
            p.doi as doi,
            collect(DISTINCT c.name) as concepts
        ORDER BY p.year DESC, p.title
        """
        results = db.execute_query(query)
        return results
    except Exception as e:
        logger.error(f"Error getting papers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/authors")
async def get_authors() -> List[Dict[str, Any]]:
    """Get all authors and their papers."""
    try:
        query = """
        MATCH (a:Author)-[:AUTHORED]->(p:Paper)
        WITH a, collect({title: p.title, year: p.year}) as papers
        RETURN
            a.name as name,
            a.discipline as discipline,
            papers,
            size(papers) as paper_count
        ORDER BY paper_count DESC, a.name
        """
        results = db.execute_query(query)
        return results
    except Exception as e:
        logger.error(f"Error getting authors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Google File Search Specific Endpoints
# ============================================

class CompareQuery(BaseModel):
    concept1: str
    concept2: str


class GapAnalysisQuery(BaseModel):
    concept: str


@app.get("/api/google/files")
async def list_google_files() -> Dict[str, Any]:
    """List files uploaded to Google File Search."""
    if not use_google_rag or not hybrid_rag:
        return {"files": [], "message": "Google File Search not enabled"}

    try:
        files = hybrid_rag.gfs.list_files()
        return {
            "count": len(files),
            "files": files
        }
    except Exception as e:
        logger.error(f"Error listing Google files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/google/compare")
async def compare_concepts_google(query: CompareQuery) -> Dict[str, Any]:
    """Compare two concepts using Google File Search + Knowledge Graph."""
    if not use_google_rag or not hybrid_rag:
        raise HTTPException(status_code=503, detail="Google File Search not enabled")

    try:
        result = hybrid_rag.compare_concepts(query.concept1, query.concept2)
        return result
    except Exception as e:
        logger.error(f"Error comparing concepts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/google/gaps")
async def find_gaps_google(query: GapAnalysisQuery) -> Dict[str, Any]:
    """Find implementation gaps for a concept using Google File Search."""
    if not use_google_rag or not hybrid_rag:
        raise HTTPException(status_code=503, detail="Google File Search not enabled")

    try:
        result = hybrid_rag.find_implementation_gaps(query.concept)
        return result
    except Exception as e:
        logger.error(f"Error finding gaps: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/info")
async def get_system_info() -> Dict[str, Any]:
    """Get information about the RAG system configuration."""
    if use_google_rag and hybrid_rag:
        stats = hybrid_rag.get_statistics()
        stats['rag_provider'] = 'Google File Search + Neo4j'
    elif graphrag:
        stats = {
            'rag_provider': 'OpenAI + Neo4j',
            'knowledge_graph': db.get_schema_info()
        }
    else:
        stats = {'rag_provider': 'None', 'status': 'Not initialized'}

    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
