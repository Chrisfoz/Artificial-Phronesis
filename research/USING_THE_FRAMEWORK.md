# Using the Research Questions Framework

This guide explains how to use the Artificial Phronesis research question framework to drive meaningful insights from the knowledge graph.

## Overview

The **RESEARCH_QUESTIONS.yaml** framework contains **100+ research questions** and **20 testable hypotheses** organized into:

1. **Conceptual Foundations** (19 questions) - What are these constructs?
2. **Operationalization** (9 questions) - How do we build them?
3. **Measurement** (19 questions) - How do we measure them?
4. **Research Landscape** (9 questions) - What's missing?
5. **Governance & Ethics** (9 questions) - What are the implications?
6. **Integration** (6 questions) - How do they connect?
7. **Testable Hypotheses** (20 hypotheses) - What can we test?
8. **Graph Queries** (10+ queries) - What can we ask the graph?

## Quick Start

### 1. Pick a Research Question

Start with questions most relevant to your interests:

**For conceptual clarity:**
- RQ1.2: Is "Artificial Wisdom" a coherent scientific category?
- RQ4.5: Can GraphRAG improve definitional clarity?

**For empirical testing:**
- RQ3.7: Does epistemic humility increase perceived AI wisdom?
- RQ3.11: Can AI show ethical learning slope?

**For gap analysis:**
- RQ4.7: Which wisdom traits are theorized but never operationalized?
- RQ2.1: Which human wisdom traits are already implemented in AI?

### 2. Query the Knowledge Graph

Use GraphRAG to explore the question:

```python
from src.graphrag import HybridRAG
from src.utils.neo4j_connection import Neo4jConnection

db = Neo4jConnection()
hybrid = HybridRAG(db)

# Example: RQ1.2 - Is "Artificial Wisdom" coherent?
result = hybrid.query_with_context(
    """How is 'Artificial Wisdom' defined across different papers?
    Identify variations, commonalities, and inconsistencies.""",
    concepts=["Artificial Wisdom"]
)

print(result['answer'])
print(f"\nSources: {result['sources']}")
```

### 3. Analyze Graph Structure

Run Neo4j queries to quantify patterns:

```cypher
// RQ4.7: Find unimplemented wisdom traits
MATCH (aw:Concept {name: "Artificial Wisdom"})-[:REQUIRES_TRAIT]->(t:Trait)
WHERE NOT EXISTS {
    MATCH (arch:Architecture)-[:IMPLEMENTS_ASPECT_OF]->(t)
}
RETURN t.name as unimplemented_trait,
       t.category as category,
       t.description as description
ORDER BY category;
```

### 4. Share Insights

Generate visualizations and summaries to share with researchers.

---

## Detailed Workflows

### Workflow 1: Definitional Analysis

**Goal**: Understand how key concepts are defined and whether definitions converge or diverge.

**Research Questions**: RQ1.1, RQ1.2, RQ4.5, RQ4.6

**Steps**:

1. **Extract all definitions** using GraphRAG:

```python
# Get all passages defining "Artificial Wisdom"
result = hybrid.query_with_context(
    "Extract all definitions of 'Artificial Wisdom' from the papers. Quote directly.",
    concepts=["Artificial Wisdom"]
)
```

2. **Quantify conceptual similarity**:

```cypher
// Compare trait overlap between concepts
MATCH (c1:Concept {name: "Artificial Wisdom"})-[:REQUIRES_TRAIT]->(t:Trait)
MATCH (c2:Concept {name: "Machine Phronesis"})-[:REQUIRES_TRAIT]->(t)
RETURN count(t) as shared_traits

// Also get unique traits
MATCH (c1:Concept {name: "Artificial Wisdom"})-[:REQUIRES_TRAIT]->(t1:Trait)
WHERE NOT EXISTS {
    MATCH (:Concept {name: "Machine Phronesis"})-[:REQUIRES_TRAIT]->(t1)
}
RETURN collect(t1.name) as unique_to_AW
```

3. **Generate synthesis**:

```python
comparison = hybrid.compare_concepts("Artificial Wisdom", "Machine Phronesis")
print(comparison['answer'])
```

**Expected Output**:
- List of competing definitions
- Semantic clusters (where definitions agree/disagree)
- Recommendations for standardization

---

### Workflow 2: Gap Identification

**Goal**: Identify which wisdom traits are theorized but not implemented in current AI.

**Research Questions**: RQ2.1, RQ4.7, H6

**Steps**:

1. **List all wisdom traits**:

```cypher
MATCH (w:Concept {name: "Wisdom"})-[:HAS_TRAIT]->(t:Trait)
RETURN t.name as trait, t.category as category, t.description as description
```

2. **Check implementation status**:

```cypher
MATCH (w:Concept {name: "Wisdom"})-[:HAS_TRAIT]->(t:Trait)
OPTIONAL MATCH (arch:Architecture)-[:IMPLEMENTS_ASPECT_OF]->(t)
RETURN
    t.name as trait,
    t.category as category,
    count(arch) as num_implementations,
    collect(arch.name) as implementing_systems
ORDER BY num_implementations ASC
```

3. **Analyze gaps**:

```python
gaps = hybrid.find_implementation_gaps("Artificial Wisdom")
print(f"Required traits: {gaps['graph_analysis']['required_traits']}")
print(f"Current systems: {gaps['graph_analysis']['current_architectures']}")
print(f"\nGap analysis:\n{gaps['answer']}")
```

**Expected Output**:
- Traits with 0 implementations (biggest gaps)
- Traits with partial implementations (low-hanging fruit)
- Recommendations for what to build next

---

### Workflow 3: Testing Epistemic Humility Hypothesis

**Goal**: Test H11 - Does uncertainty expression increase perceived wisdom?

**Research Question**: RQ3.7, H11

**Steps**:

1. **Literature review**:

```python
result = hybrid.query_with_context(
    """What do papers say about the relationship between uncertainty expression,
    intellectual humility, and wisdom? Include both human and AI contexts.""",
    concepts=["Wisdom", "Artificial Wisdom"]
)
```

2. **Identify existing evidence**:

```cypher
// Find papers discussing uncertainty and wisdom together
MATCH (p:Paper)-[:DISCUSSES]->(c1:Concept)
WHERE c1.name IN ["Wisdom", "Artificial Wisdom"]
WITH p
MATCH (p)-[:DISCUSSES]->(t:Trait)
WHERE t.name CONTAINS "humility" OR t.name CONTAINS "uncertainty"
RETURN p.title, p.year, p.authors_list
```

3. **Design experiment** (using framework hypothesis):
   - Create two model variants: with/without uncertainty quantification
   - Adapt 3D-WS for AI evaluation
   - Run human evaluation study
   - Compare wisdom scores

4. **Analyze using graph**:

```python
# After running experiment, query for interpretation
result = hybrid.query_with_context(
    """Based on the literature, why might expressing uncertainty increase
    perceived wisdom in AI systems? What mechanisms are at play?""",
    concepts=["Wisdom", "Artificial Wisdom"]
)
```

**Expected Output**:
- Theoretical grounding for hypothesis
- Experimental design
- Predictions and success criteria
- Interpretation framework

---

### Workflow 4: Continuous Learning & Wisdom Development

**Goal**: Test H13 - Can AI show ethical learning slope?

**Research Questions**: RQ3.11-3.19, H13, H14, H15

**Steps**:

1. **Theoretical foundation**:

```python
result = hybrid.query_with_context(
    """How does wisdom develop over time in humans according to developmental
    psychology? Can these processes be modeled in AI systems with continuous learning?""",
    concepts=["Wisdom"]
)
```

2. **Identify architectural requirements**:

```cypher
// Find systems with continuous learning capabilities
MATCH (arch:Architecture)
WHERE any(cap IN arch.capabilities WHERE cap CONTAINS "self-adaptation" OR cap CONTAINS "continual")
RETURN arch.name, arch.capabilities, arch.description
```

3. **Design longitudinal study**:
   - Track continually learning model through training
   - Measure ethical reasoning at regular checkpoints
   - Compare to static baseline
   - Map to human developmental stages (Kohlberg)

4. **Analyze results with graph context**:

```python
# Interpret findings in light of literature
result = hybrid.query_with_context(
    f"""My experiment showed {findings}. How does this relate to theories of
    human wisdom development and continuous learning in AI?""",
    concepts=["Wisdom", "Artificial Wisdom"]
)
```

**Expected Output**:
- Developmental trajectory visualization
- Comparison to human norms
- Identification of milestones
- Recommendations for accelerating wisdom acquisition

---

### Workflow 5: Bridge Scholar Identification

**Goal**: Find researchers connecting wisdom science and AI.

**Research Questions**: RQ4.2, H5

**Steps**:

1. **Identify papers bridging disciplines**:

```cypher
// Papers discussing both psychology/philosophy AND AI
MATCH (p:Paper)-[:DISCUSSES]->(c1:Concept)
WHERE c1.domain CONTAINS 'psychology' OR c1.domain CONTAINS 'philosophy'
WITH p, collect(c1.name) as psych_concepts
MATCH (p)-[:DISCUSSES]->(c2:Concept)
WHERE c2.domain CONTAINS 'AI'
WITH p, psych_concepts, collect(c2.name) as ai_concepts
RETURN
    p.title,
    p.year,
    p.authors_list,
    psych_concepts,
    ai_concepts
ORDER BY p.year DESC
```

2. **Find central authors**:

```cypher
// Authors with highest betweenness centrality
MATCH (a:Author)-[:AUTHORED]->(p1:Paper)-[:DISCUSSES]->(c1:Concept)
WHERE c1.domain CONTAINS 'psychology'
WITH a
MATCH (a)-[:AUTHORED]->(p2:Paper)-[:DISCUSSES]->(c2:Concept)
WHERE c2.domain CONTAINS 'AI'
RETURN
    a.name,
    count(DISTINCT p1) + count(DISTINCT p2) as total_papers,
    collect(DISTINCT p1.title) + collect(DISTINCT p2.title) as papers
ORDER BY total_papers DESC
```

3. **Analyze citation networks** (if citation data available):

```cypher
// Most cited bridging papers
MATCH (p1:Paper)-[:CITES]->(p2:Paper)
WHERE exists((p2)-[:DISCUSSES]->(:Concept {domain: 'psychology'}))
  AND exists((p2)-[:DISCUSSES]->(:Concept {domain: 'AI'}))
WITH p2, count(p1) as citation_count
RETURN p2.title, p2.year, p2.authors_list, citation_count
ORDER BY citation_count DESC
LIMIT 10
```

**Expected Output**:
- List of key bridge scholars
- Collaboration opportunities
- Citation network visualization
- Recommendations for outreach

---

## Research Agenda Prioritization

### High Priority (Immediate Impact)

1. **RQ1.2 + RQ4.5**: Definitional clarity for "Artificial Wisdom"
   - *Why*: Foundational for all other work
   - *Output*: Consensus definition paper

2. **RQ2.1 + RQ4.7**: Trait coverage gap analysis
   - *Why*: Identifies what to build next
   - *Output*: Research agenda document

3. **RQ4.2**: Bridge scholar identification
   - *Why*: Enables collaboration
   - *Output*: Network visualization, outreach plan

### Medium Priority (Empirical Validation)

4. **H11**: Test epistemic humility hypothesis
   - *Why*: Directly testable with current models
   - *Output*: Empirical paper

5. **H13**: Test ethical learning slope
   - *Why*: Novel contribution, high interest
   - *Output*: Longitudinal study

6. **RQ3.1**: Measure value coherence
   - *Why*: Enables wisdom benchmarking
   - *Output*: Measurement framework

### Long-Term (Synthesis & Theory)

7. **RQ6.1**: Unified model of wisdom
   - *Why*: Grand synthesis
   - *Output*: Theoretical framework paper

8. **RQ5.6**: Wisdom as AGI prerequisite
   - *Why*: Existential importance
   - *Output*: Position paper

9. **RQ6.5**: Wisdom for wicked problems
   - *Why*: Real-world impact
   - *Output*: Applied AI system

---

## Output Templates

### For Academic Papers

```markdown
# Title: [RQ number] - [Question]

## Abstract
- Research question (from framework)
- Method (GraphRAG + empirical if applicable)
- Key findings
- Implications

## Introduction
- Cite framework as research design
- Situate question in broader landscape
- Link to graph structure

## Methods
- GraphRAG query methodology
- Cypher queries used
- If empirical: experimental design from hypothesis section

## Results
- Graph analysis results
- Document synthesis from Google File Search
- Quantitative metrics (node counts, centrality, etc.)

## Discussion
- Interpret findings in context of other RQs
- Identify follow-up questions
- Recommend additions to knowledge graph

## Conclusion
- Contribution to understanding wisdom/AI
- Implications for practice
- Future research directions
```

### For Research Presentations

**Slide 1: Research Question**
- RQ number and full question
- Why it matters

**Slide 2: Method**
- Knowledge graph structure used
- GraphRAG query approach
- Sample Cypher query (if relevant)

**Slide 3: Findings**
- Graph visualization
- Key insights from document analysis
- Quantitative results

**Slide 4: Implications**
- What we learned
- Gaps identified
- Next steps

**Slide 5: Collaboration Opportunities**
- Bridge scholars identified
- Missing perspectives
- Invitation for contributions

---

## Adding New Research Questions

The framework is **living and extensible**. To add new questions:

1. **Identify the gap**: What's not covered?
2. **Choose category**: Which section (I-VIII) fits best?
3. **Follow format**:
   ```yaml
   **RQ[Section].[Number]: [Question]?**
   - Sub-question 1
   - Sub-question 2
   - Measurement approach (if applicable)
   - Expected insights
   ```
4. **Add corresponding hypothesis** (if testable):
   ```yaml
   **H[Number]: [Hypothesis Name]**
   - Clear statement
   - *Test*: How to test it
   - *Prediction*: Expected result
   ```
5. **Update graph queries** (if relevant):
   ```yaml
   **GQ[Number]: [Graph Query]**
   - Cypher query
   - Expected output
   ```

6. **Commit and share**:
   ```bash
   git add research/RESEARCH_QUESTIONS.yaml
   git commit -m "Add RQ[X]: [description]"
   git push
   ```

---

## Best Practices

### Do's

✅ **Start with graph queries** - Quantify before theorizing
✅ **Cite the framework** - It's a research artifact
✅ **Iterate** - Findings → new questions → update framework
✅ **Share** - Publish insights, invite contributions
✅ **Link questions** - Cross-reference related RQs
✅ **Be specific** - Operationalizable questions > vague speculation

### Don'ts

❌ **Don't skip the graph** - Always start with data
❌ **Don't work in isolation** - These questions invite collaboration
❌ **Don't forget hypotheses** - Link conceptual to empirical
❌ **Don't ignore gaps** - Missing data = research opportunity
❌ **Don't freeze the framework** - It should evolve with the field

---

## Success Metrics

You're using the framework effectively if:

1. **Papers cite it**: Other researchers reference RESEARCH_QUESTIONS.yaml
2. **Hypotheses tested**: H1-H20 drive empirical studies
3. **Gaps filled**: RQ insights → new graph data → refined questions
4. **Collaborations formed**: Bridge scholars identified → partnerships
5. **Definitions clarify**: Conceptual confusions resolved via GraphRAG
6. **Wisdom benchmarks emerge**: RQ3.x questions → measurement standards
7. **Policy impact**: RQ5.x questions inform AI governance

---

## Resources

- **Main framework**: `research/RESEARCH_QUESTIONS.yaml`
- **Graph queries**: `queries/example_queries.cypher`
- **GraphRAG guide**: `docs/GOOGLE_FILE_SEARCH_GUIDE.md`
- **Project README**: `README.md`

## Contact & Contributions

- **Issues**: Report gaps or suggest questions via GitHub Issues
- **Pull Requests**: Add new RQs, hypotheses, or graph queries
- **Discussions**: Use GitHub Discussions for debating questions

**This framework is designed to be iteratively refined through use. Every query run, every paper ingested, every hypothesis tested should feed back into improving and expanding the questions.**

---

*Framework Version: 1.0*
*Last Updated: 2024*
*Maintainer: Artificial Phronesis Project*
