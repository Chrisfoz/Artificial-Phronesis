// Example Cypher Queries for Artificial Phronesis Knowledge Graph

// =====================================
// Basic Concept Queries
// =====================================

// 1. Find all concepts and their types
MATCH (c:Concept)
RETURN c.name as concept, c.type as type, c.domain as domain
ORDER BY c.name;

// 2. Get all wisdom traits
MATCH (w:Concept {name: "Wisdom"})-[:HAS_TRAIT]->(t:Trait)
RETURN w.name as concept, collect(t.name) as traits;

// 3. Find relationships between Wisdom and Intelligence
MATCH path = (w:Concept {name: "Wisdom"})-[r]-(i:Concept {name: "Intelligence"})
RETURN w.name, type(r) as relationship, i.name, r.basis as basis;

// =====================================
// Architecture and Implementation Queries
// =====================================

// 4. Find which AI architectures implement wisdom-related traits
MATCH (arch:Architecture)-[r:IMPLEMENTS_ASPECT_OF]->(t:Trait)
WHERE (t)<-[:HAS_TRAIT|REQUIRES_TRAIT]-(:Concept {name: "Artificial Wisdom"})
RETURN arch.name as architecture, collect(t.name) as wisdom_traits;

// 5. Identify gaps: Which wisdom traits are NOT implemented by any architecture?
MATCH (aw:Concept {name: "Artificial Wisdom"})-[:REQUIRES_TRAIT]->(t:Trait)
WHERE NOT EXISTS {
    MATCH (arch:Architecture)-[:IMPLEMENTS_ASPECT_OF]->(t)
}
RETURN t.name as unimplemented_trait, t.description as description;

// 6. Find architectures and their capabilities
MATCH (arch:Architecture)
RETURN arch.name as architecture,
       arch.capabilities as capabilities,
       arch.description as description;

// =====================================
// Concept Comparison Queries
// =====================================

// 7. Compare traits of Wisdom vs. Artificial Wisdom
MATCH (w:Concept {name: "Wisdom"})-[:HAS_TRAIT]->(wt:Trait)
MATCH (aw:Concept {name: "Artificial Wisdom"})-[:REQUIRES_TRAIT]->(awt:Trait)
RETURN
    collect(DISTINCT wt.name) as wisdom_traits,
    collect(DISTINCT awt.name) as artificial_wisdom_traits,
    [t in collect(DISTINCT wt.name) WHERE t IN collect(DISTINCT awt.name)] as shared_traits;

// 8. Find all concepts that are contrasted with each other
MATCH (c1:Concept)-[r:CONTRASTED_WITH]->(c2:Concept)
RETURN c1.name as concept1, c2.name as concept2, r.basis as distinction;

// 9. Find the conceptual hierarchy (subtypes)
MATCH path = (sub:Concept)-[:SUBTYPE_OF*]->(super:Concept)
RETURN [node in nodes(path) | node.name] as hierarchy;

// =====================================
// Paper and Author Queries
// =====================================

// 10. Find papers discussing Artificial Wisdom
MATCH (p:Paper)-[:DISCUSSES]->(c:Concept)
WHERE c.name IN ["Artificial Wisdom", "Machine Phronesis", "Computational Sapience"]
RETURN p.title as paper, p.year as year, p.authors_list as authors, c.name as concept
ORDER BY p.year DESC;

// 11. Find most cited/discussed concepts
MATCH (p:Paper)-[:DISCUSSES]->(c:Concept)
RETURN c.name as concept, count(p) as paper_count
ORDER BY paper_count DESC
LIMIT 10;

// 12. Find author collaboration networks
MATCH (a1:Author)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(a2:Author)
WHERE a1.name < a2.name
RETURN a1.name as author1, a2.name as author2, collect(p.title) as co_authored_papers;

// 13. Find papers by year and concepts they discuss
MATCH (p:Paper)-[:DISCUSSES]->(c:Concept)
WITH p.year as year, collect(DISTINCT c.name) as concepts, count(p) as paper_count
WHERE year IS NOT NULL
RETURN year, concepts, paper_count
ORDER BY year DESC;

// =====================================
// Advanced GraphRAG Queries
// =====================================

// 14. Find shortest path between two concepts
MATCH path = shortestPath(
    (c1:Concept {name: "Intelligence"})-[*]-(c2:Concept {name: "Artificial Wisdom"})
)
RETURN [node in nodes(path) | node.name] as path,
       [rel in relationships(path) | type(rel)] as relationships;

// 15. Find concepts that bridge multiple domains
MATCH (c:Concept)
WHERE c.domain CONTAINS ',' OR c.domain CONTAINS 'and'
RETURN c.name as concept, c.domain as domains, c.description as description;

// 16. Identify central concepts (high degree centrality)
MATCH (c:Concept)
OPTIONAL MATCH (c)-[r]-()
WITH c, count(r) as degree
WHERE degree > 3
RETURN c.name as concept, c.type as type, degree
ORDER BY degree DESC;

// 17. Find concepts with similar neighborhoods (potential overlaps)
MATCH (c1:Concept)-[:HAS_TRAIT|REQUIRES_TRAIT]->(t:Trait)<-[:HAS_TRAIT|REQUIRES_TRAIT]-(c2:Concept)
WHERE c1.name < c2.name
WITH c1, c2, collect(t.name) as shared_traits
WHERE size(shared_traits) > 2
RETURN c1.name as concept1, c2.name as concept2, shared_traits, size(shared_traits) as overlap_count
ORDER BY overlap_count DESC;

// =====================================
// Research Gap Analysis
// =====================================

// 18. Find traits that are theorized but not operationalized
MATCH (t:Trait)
WHERE NOT EXISTS {
    MATCH (t)<-[:IMPLEMENTS_ASPECT_OF]-(:Architecture)
}
RETURN t.name as trait, t.category as category, t.description as description
ORDER BY t.category;

// 19. Find papers that bridge psychology and AI
MATCH (p:Paper)-[:DISCUSSES]->(c1:Concept)
WHERE c1.domain CONTAINS 'psychology'
WITH p, collect(c1.name) as psych_concepts
MATCH (p)-[:DISCUSSES]->(c2:Concept)
WHERE c2.domain CONTAINS 'AI'
WITH p, psych_concepts, collect(c2.name) as ai_concepts
RETURN p.title as paper, p.year as year, psych_concepts, ai_concepts;

// 20. Find under-connected concepts (potential research opportunities)
MATCH (c:Concept)
OPTIONAL MATCH (c)-[r]-()
WITH c, count(r) as degree
WHERE degree < 3
RETURN c.name as concept, c.type as type, c.domain as domain, degree
ORDER BY degree;

// =====================================
// Visualization Queries
// =====================================

// 21. Get subgraph for a specific concept (2 hops)
MATCH path = (c:Concept {name: "Phronesis"})-[*1..2]-(related)
RETURN path;

// 22. Get all relationships between Concepts, Traits, and Architectures
MATCH (n)-[r]->(m)
WHERE (n:Concept OR n:Trait OR n:Architecture)
  AND (m:Concept OR m:Trait OR m:Architecture)
RETURN n, r, m;

// =====================================
// Stats and Summaries
// =====================================

// 23. Database summary
MATCH (n)
WITH labels(n) as labels
UNWIND labels as label
RETURN label, count(*) as count
ORDER BY count DESC;

// 24. Relationship type summary
MATCH ()-[r]->()
WITH type(r) as rel_type
RETURN rel_type, count(*) as count
ORDER BY count DESC;
