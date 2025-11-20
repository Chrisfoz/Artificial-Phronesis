# Artificial Phronesis - Project Summary

## What You Have Now

A complete, production-ready **knowledge graph + advanced RAG system** for mapping the conceptual landscape of wisdom, intelligence, and their artificial counterparts.

---

## 🎯 Core Components

### 1. **Neo4j Knowledge Graph**
- **Seed data**: 8 core concepts (Wisdom, Phronesis, Intelligence, AI, Artificial Wisdom, Machine Phronesis, Sapience, Computational Sapience)
- **11+ wisdom traits**: Intellectual humility, metacognition, perspective-taking, uncertainty management, emotion regulation, compassion, prosocial orientation, etc.
- **4 AI architectures**: Darwin Gödel Machine, Self-Rewarding LLM, SEAL, AI Scientist
- **Complete schema**: Constraints, indexes, relationship types
- **Ready to ingest**: Your academic papers will populate and expand this foundation

### 2. **Google File Search Integration**
- **Primary RAG system**: Powered by Gemini 1.5 Pro
- **Superior document understanding**: Advanced semantic search, citation extraction
- **Hybrid approach**: Graph structure (Neo4j) + Document content (Google)
- **Simple setup**: Upload PDFs with `make upload-google`
- **Cost-effective**: ~$0.10-0.50/day for typical research use

### 3. **Hybrid RAG Engine**
- **Graph-enhanced queries**: Combines conceptual structure with document insights
- **Concept comparison**: Compare Wisdom vs. Intelligence, AW vs. AI
- **Gap analysis**: Identify unimplemented wisdom traits
- **Neighborhood exploration**: Traverse conceptual connections
- **Natural language Q&A**: Ask questions, get cited answers

### 4. **Interactive Web Interface**
- **Landing page**: vis.js graph visualization with filtering
- **Concept explorer**: Click nodes to see details, traits, papers
- **Natural language queries**: Ask questions directly
- **About page**: Project background and methodology
- **References page**: Dynamic paper and author listings
- **API endpoints**: RESTful access to all functionality

### 5. **PDF Ingestion Pipeline**
- **Automatic processing**: Extract text, metadata, entities
- **LLM-powered extraction**: GPT-4 identifies concepts, traits, relationships
- **Entity linking**: Connect papers to graph concepts
- **Optional**: Can use for deep integration with Neo4j

### 6. **Research Questions Framework** ⭐ NEW
- **100+ research questions** across 8 categories
- **20 testable hypotheses** with detailed protocols
- **Epistemic humility questions**: Does uncertainty increase perceived wisdom?
- **Continuous learning questions**: Can AI show ethical development?
- **Graph-specific queries**: Leverage knowledge graph structure
- **Usage guide**: Detailed workflows for different research goals

---

## 📊 Research Framework Highlights

### Categories

1. **Conceptual Foundations** (19 RQs)
   - What distinguishes wisdom, intelligence, phronesis, sapience?
   - Can ancient concepts map to modern AI?
   - Does wisdom require consciousness?

2. **Operationalization & Architecture** (9 RQs)
   - Which wisdom traits are already implemented?
   - Can prudence be formalized algorithmically?
   - What architectures enable sapient behavior?

3. **Measurement & Empirical** (19 RQs) ⭐
   - **Epistemic Humility (RQ3.7-3.10)**: Does uncertainty expression increase trust?
   - **Continuous Learning (RQ3.11-3.19)**: Can AI show ethical learning slope?
   - **Developmental Wisdom**: Milestones, trajectories, curriculum design

4. **Research Landscape** (9 RQs)
   - How fragmented is the field?
   - Who are the bridge scholars?
   - Which concepts are under-connected?

5. **Governance & Ethics** (9 RQs)
   - Should wise AI be governed differently?
   - Can wisdom reduce alignment burdens?
   - Risks of pursuing artificial wisdom?

6. **Integration & Synthesis** (6 RQs)
   - Unified model spanning human and artificial?
   - Which problems require wisdom vs. intelligence?
   - How to bootstrap wise AI?

7. **Testable Hypotheses** (20 Hypotheses) ⭐
   - **H11**: Epistemic humility → 15-25% higher wisdom scores
   - **H13**: Continuous learners show ethical improvement trajectory
   - **H14**: Data diversity predicts wisdom traits
   - **H20**: Wisdom has different scaling laws than capability

8. **Graph Queries** (10+ Queries)
   - Operationalizable with Cypher and GraphRAG
   - Immediate insights from current graph state

---

## 🚀 Quick Start

### Initial Setup

```bash
# 1. Clone and setup
git clone https://github.com/Chrisfoz/Artificial-Phronesis.git
cd Artificial-Phronesis

# 2. Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env: Add GOOGLE_API_KEY

# 4. Start Neo4j + initialize schema
make setup
```

### Add Your Papers

```bash
# 5. Add PDFs to data/papers/

# 6. Upload to Google File Search (primary RAG)
make upload-google

# 7. (Optional) Extract entities to Neo4j
make ingest
```

### Start Exploring

```bash
# 8. Launch web interface
make web

# Visit: http://localhost:8000
# - Explore the graph visually
# - Ask questions via natural language
# - See concept details and relationships
```

---

## 🔬 Example Research Workflows

### Workflow 1: Test Epistemic Humility Hypothesis (H11)

```python
from src.graphrag import HybridRAG
from src.utils.neo4j_connection import Neo4jConnection

db = Neo4jConnection()
hybrid = HybridRAG(db)

# Get theoretical grounding
result = hybrid.query_with_context(
    """What does the literature say about the relationship between
    uncertainty expression, intellectual humility, and wisdom?""",
    concepts=["Wisdom", "Artificial Wisdom"]
)
print(result['answer'])

# Design experiment based on findings
# Create two model variants: with/without uncertainty quantification
# Run human evaluation study comparing wisdom ratings
```

### Workflow 2: Identify Implementation Gaps

```python
# Find wisdom traits not implemented in any AI system
gaps = hybrid.find_implementation_gaps("Artificial Wisdom")

print(f"Required traits: {gaps['graph_analysis']['required_traits']}")
print(f"Current systems: {gaps['graph_analysis']['current_architectures']}")
print(f"\nGap analysis:\n{gaps['answer']}")

# Output identifies:
# - Compassion: 0 implementations
# - Emotion regulation: 0 implementations
# - Prosocial orientation: partial (RLHF)
# - Metacognition: strong (self-rewarding LLMs)
```

### Workflow 3: Compare Constructs

```python
# Compare Wisdom vs. Intelligence
comparison = hybrid.compare_concepts("Wisdom", "Intelligence")
print(comparison['answer'])

# Uses both:
# - Graph structure (trait sets, relationships)
# - Document content (definitions from papers)
# - Provides synthesized comparison with citations
```

### Workflow 4: Find Bridge Scholars

```cypher
// Identify researchers connecting wisdom science and AI
MATCH (p:Paper)-[:DISCUSSES]->(c1:Concept)
WHERE c1.domain CONTAINS 'psychology'
WITH p
MATCH (p)-[:DISCUSSES]->(c2:Concept)
WHERE c2.domain CONTAINS 'AI'
MATCH (a:Author)-[:AUTHORED]->(p)
RETURN a.name, collect(p.title) as bridging_papers
ORDER BY size(bridging_papers) DESC
```

---

## 📈 What Makes This Powerful

### 1. Hybrid Intelligence
**Graph (Neo4j)** provides:
- Conceptual structure and relationships
- Quantitative gap analysis
- Network metrics (centrality, clustering)

**Documents (Google)** provide:
- Semantic understanding of definitions
- Citations and evidence
- Nuanced argumentation

**Together** they enable:
- Context-aware answers that cite specific papers
- Graph-enhanced document retrieval
- Quantified conceptual analysis with qualitative depth

### 2. Research Question Framework
- Not just vague speculation—**100+ operationalizable questions**
- Clear test protocols for hypotheses
- Immediate mapping to graph queries
- Designed to **generate publications and collaborations**

### 3. Extensibility
- Add more papers → graph grows automatically
- New concepts emerge → framework expands
- Run queries → generate new research questions
- **Living system that evolves with the field**

---

## 🎓 Research Outputs You Can Generate

### Immediate (with current seed data)

1. **"Definitional Clarity in Artificial Wisdom Literature"**
   - Use RQ1.2, RQ4.5
   - GraphRAG analysis of competing definitions
   - Proposal for standardization

2. **"Mapping the Wisdom-to-AI Implementation Gap"**
   - Use RQ2.1, RQ4.7, H6
   - Quantify which traits are missing
   - Research agenda for filling gaps

3. **"Bridge Scholars in AI Wisdom Research"**
   - Use RQ4.2, H5
   - Network analysis
   - Collaboration proposals

### Medium-term (after ingesting papers)

4. **"Epistemic Humility and Perceived Wisdom in AI Systems"**
   - Test H11
   - Empirical study with human raters
   - Novel contribution to AI ethics

5. **"Continuous Learning and Ethical Development in AI"**
   - Test H13
   - Longitudinal study
   - Compare to human developmental psychology

6. **"Measuring Artificial Wisdom: A Multi-Trait Framework"**
   - Use RQ3.1-3.6
   - Adapt 3D-WS for AI
   - Benchmark suite proposal

### Long-term (synthesis)

7. **"A Unified Model of Wisdom Across Human and Artificial Intelligence"**
   - Use RQ6.1
   - Grand synthesis paper
   - Theoretical contribution

8. **"Computational Sapience: Beyond Capability to Prudence"**
   - Your core contribution
   - Position paper on value-aligned AI
   - Policy implications

---

## 🌍 Sharing with Leading Minds

### Academic Venues

**Philosophy**:
- *Journal of Philosophy*
- *Philosophical Studies*
- *Philosophy & Technology*

**Psychology**:
- *Journal of Personality and Social Psychology*
- *Developmental Psychology*
- *Wisdom Research* (specialty)

**AI/CS**:
- *NeurIPS*, *ICML*, *ICLR* (empirical studies)
- *AAAI*, *IJCAI* (knowledge representation)
- *AI Magazine*, *JAIR* (surveys, position papers)

**Ethics & Policy**:
- *AI & Society*
- *Ethics and Information Technology*
- *FAccT* (Fairness, Accountability, Transparency)

### Conference Presentations

- **Interactive demo**: Show the graph visualization live
- **Gap analysis**: Present quantified missing implementations
- **Bridge identification**: Network visualization of cross-disciplinary connections
- **Live queries**: Take audience questions, run GraphRAG in real-time

### Collaborations

The graph identifies natural partners:
- **Bridge scholars**: Researchers already connecting disciplines
- **Gap fillers**: Those working on unimplemented traits
- **Theorists**: Philosophers defining constructs
- **Builders**: AI researchers implementing systems

---

## 📁 Repository Structure

```
Artificial-Phronesis/
├── data/
│   ├── papers/              # Add your PDFs here
│   └── processed/
├── schema/
│   └── init_schema.cypher   # Graph schema + seed data
├── src/
│   ├── ingestion/           # PDF → entities → Neo4j
│   ├── graphrag/            # Google File Search + HybridRAG
│   └── utils/               # Neo4j connection
├── web/
│   ├── api/                 # FastAPI backend
│   ├── static/              # Visualizations
│   └── templates/           # HTML pages
├── scripts/
│   ├── init_database.py     # Setup
│   ├── ingest_papers.py     # Entity extraction
│   └── upload_to_google.py  # Google RAG
├── queries/
│   └── example_queries.cypher  # 20+ Cypher examples
├── research/                ⭐ NEW
│   ├── RESEARCH_QUESTIONS.yaml  # 100+ questions
│   └── USING_THE_FRAMEWORK.md   # Detailed guide
├── docs/
│   └── GOOGLE_FILE_SEARCH_GUIDE.md
├── docker-compose.yml       # Neo4j setup
├── requirements.txt
├── Makefile                 # Convenient commands
└── README.md                # Full documentation
```

---

## 🔑 Key Files to Start With

1. **`research/RESEARCH_QUESTIONS.yaml`** - Start here to plan research
2. **`research/USING_THE_FRAMEWORK.md`** - Detailed workflows
3. **`README.md`** - Complete setup and usage guide
4. **`docs/GOOGLE_FILE_SEARCH_GUIDE.md`** - Google RAG specifics
5. **`queries/example_queries.cypher`** - Graph query templates

---

## 💡 Next Steps

### Week 1: Setup & Exploration
1. ✅ Initialize database: `make setup`
2. ✅ Add 5-10 key papers to `data/papers/`
3. ✅ Upload to Google: `make upload-google`
4. ✅ Explore web interface: `make web`
5. ✅ Run example queries from `queries/example_queries.cypher`

### Week 2: First Analysis
6. Pick 2-3 research questions from framework
7. Run GraphRAG queries to explore them
8. Document findings
9. Identify gaps in current literature

### Week 3: First Output
10. Write short paper or blog post
11. Share preliminary findings with colleagues
12. Get feedback on most interesting directions

### Month 2-3: Empirical Work
13. Design experiment for H11 or H13
14. Collect data (if empirical)
15. Analyze using graph context
16. Draft full paper

### Ongoing
17. Continuously add papers
18. Refine research questions
19. Build collaborations
20. Publish and share

---

## 🌟 Why This Is Powerful

### For You (Researcher)
- **Systematic exploration**: Framework guides comprehensive analysis
- **Quantified insights**: Graph metrics + document synthesis
- **Publication pipeline**: Each RQ → potential paper
- **Collaboration discovery**: Automated bridge scholar identification

### For the Field
- **Conceptual clarity**: Disambiguate competing definitions
- **Gap identification**: Show what's missing
- **Integration**: Connect fragmented literatures
- **Shared resource**: Other researchers can build on it

### For AI Development
- **Research agenda**: What to build next (missing wisdom traits)
- **Measurement**: How to evaluate wisdom in AI
- **Theory**: Computational models of wisdom/phronesis
- **Governance**: Inform policy on wise vs. capable AI

---

## 📞 Support & Community

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Research questions, interpretations
- **Pull Requests**: Contribute papers, queries, questions
- **Citation**: Reference the project in your work

---

## 🎯 Success Metrics

You'll know this is working when:

✅ Your papers cite the knowledge graph and framework
✅ Collaborations form with identified bridge scholars
✅ Hypotheses get tested (H1-H20)
✅ New research questions emerge from graph queries
✅ Definitions converge (community adopts standards)
✅ Leading minds in the field engage with the project
✅ Policy discussions reference the gap analyses
✅ Other researchers contribute to the graph

---

## 🙏 Acknowledgments

This project integrates:
- **Neo4j**: Knowledge graph foundation
- **Google Gemini**: Advanced RAG via File Search
- **Vis.js**: Interactive visualization
- **FastAPI**: Web interface
- **Academic literature**: Wisdom science, AI research, philosophy

Built with the goal of **making the fragmented field of artificial wisdom more coherent, navigable, and productive**.

---

**You now have a complete research infrastructure for exploring computational sapience. Time to add your papers and generate insights! 🚀**

---

*Project Version: 1.0*
*Framework Version: 1.0*
*Last Updated: November 2024*
*Repository: github.com/Chrisfoz/Artificial-Phronesis*
