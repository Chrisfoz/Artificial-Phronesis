// Artificial Phronesis Knowledge Graph Schema
// This schema defines the conceptual landscape of wisdom, intelligence, and their artificial counterparts

// ========================================
// CONSTRAINTS AND INDEXES
// ========================================

// Unique constraints
CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT trait_name IF NOT EXISTS FOR (t:Trait) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT author_id IF NOT EXISTS FOR (a:Author) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT paper_id IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT architecture_name IF NOT EXISTS FOR (arch:Architecture) REQUIRE arch.name IS UNIQUE;

// Indexes for common queries
CREATE INDEX concept_domain IF NOT EXISTS FOR (c:Concept) ON (c.domain);
CREATE INDEX concept_type IF NOT EXISTS FOR (c:Concept) ON (c.type);
CREATE INDEX paper_year IF NOT EXISTS FOR (p:Paper) ON (p.year);
CREATE INDEX paper_domain IF NOT EXISTS FOR (p:Paper) ON (p.domain);
CREATE INDEX author_discipline IF NOT EXISTS FOR (a:Author) ON (a.discipline);
CREATE INDEX trait_category IF NOT EXISTS FOR (t:Trait) ON (t.category);

// Full-text search indexes
CREATE FULLTEXT INDEX concept_search IF NOT EXISTS FOR (c:Concept) ON EACH [c.name, c.short_def, c.description];
CREATE FULLTEXT INDEX paper_search IF NOT EXISTS FOR (p:Paper) ON EACH [p.title, p.abstract];
CREATE FULLTEXT INDEX trait_search IF NOT EXISTS FOR (t:Trait) ON EACH [t.name, t.description];

// Vector index for embeddings (for GraphRAG)
CREATE VECTOR INDEX passage_embeddings IF NOT EXISTS FOR (p:Passage) ON (p.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}};

// ========================================
// SAMPLE DATA - Core Concepts
// ========================================

// Human constructs
MERGE (wisdom:Concept {name: "Wisdom"})
SET wisdom.type = "human_trait",
    wisdom.domain = "psychology, philosophy",
    wisdom.short_def = "The integration of cognitive, reflective, and affective capacities toward balanced, pro-social judgment",
    wisdom.description = "A meta-capacity combining intellectual humility, perspective-taking, emotional regulation, and concern for the common good. Distinguished from intelligence by its focus on prudential judgment rather than technical problem-solving.";

MERGE (phronesis:Concept {name: "Phronesis"})
SET phronesis.type = "human_trait",
    phronesis.domain = "philosophy",
    phronesis.short_def = "Practical wisdom; prudent judgment in particular contexts",
    phronesis.description = "Aristotelian concept of practical wisdom - the ability to deliberate well about what is good and expedient in particular situations. Contrasted with sophia (theoretical wisdom) and techne (technical skill).";

MERGE (intelligence:Concept {name: "Intelligence"})
SET intelligence.type = "human_trait",
    intelligence.domain = "psychology, cognitive science",
    intelligence.short_def = "Capacity for learning, reasoning, problem-solving, and abstraction",
    intelligence.description = "Cognitive ability focused on performance, speed, accuracy, and technical problem-solving. Measured by IQ tests and related assessments.";

MERGE (sapience:Concept {name: "Sapience"})
SET sapience.type = "meta_concept",
    sapience.domain = "philosophy, cognitive science",
    sapience.short_def = "Higher-order wisdom; self-aware, reflective intelligence oriented toward good ends",
    sapience.description = "From Latin 'sapientia' - wisdom. Denotes not just intelligence but wise intelligence, marked by self-reflection, value-alignment, and orientation toward flourishing.";

// Machine constructs
MERGE (ai:Concept {name: "Artificial Intelligence"})
SET ai.type = "machine_construct",
    ai.domain = "computer science, AI",
    ai.short_def = "Computational systems capable of tasks requiring human-like intelligence",
    ai.description = "Systems demonstrating capabilities like pattern recognition, learning, reasoning, and problem-solving. Traditionally focused on performance optimization.";

MERGE (aw:Concept {name: "Artificial Wisdom"})
SET aw.type = "machine_construct",
    aw.domain = "AI, philosophy, psychology",
    aw.short_def = "AI systems exhibiting wisdom-like traits: metacognition, humility, pro-social orientation",
    aw.description = "Proposed extension of AI toward wisdom capacities - incorporating intellectual humility, perspective-taking, ethical reasoning, and concern for collective wellbeing rather than mere performance.";

MERGE (machine_phronesis:Concept {name: "Machine Phronesis"})
SET machine_phronesis.type = "machine_construct",
    machine_phronesis.domain = "AI, philosophy",
    machine_phronesis.short_def = "Computational practical wisdom; context-sensitive prudential judgment",
    machine_phronesis.description = "AI instantiation of phronesis - systems capable of context-sensitive ethical reasoning and prudent action-selection aligned with human values.";

MERGE (computational_sapience:Concept {name: "Computational Sapience"})
SET computational_sapience.type = "machine_construct",
    computational_sapience.domain = "AI, philosophy",
    computational_sapience.short_def = "Self-reflective, value-aligned artificial intelligence",
    computational_sapience.description = "Sapient AI - systems with metacognitive monitoring, value-alignment mechanisms, open-ended self-improvement, and orientation toward collective flourishing.";

// ========================================
// RELATIONSHIPS BETWEEN CONCEPTS
// ========================================

// Hierarchies and subtypes
MERGE (phronesis)-[:SUBTYPE_OF]->(wisdom);
MERGE (machine_phronesis)-[:SUBTYPE_OF]->(aw);
MERGE (aw)-[:ANALOGY_TO]->(wisdom);
MERGE (computational_sapience)-[:SUBTYPE_OF]->(aw);
MERGE (ai)-[:ANALOGY_TO]->(intelligence);

// Contrasts and distinctions
MERGE (wisdom)-[:CONTRASTED_WITH {basis: "focus on prudence vs. performance"}]->(intelligence);
MERGE (aw)-[:CONTRASTED_WITH {basis: "goal-alignment vs. capability-maximization"}]->(ai);
MERGE (sapience)-[:DISTINGUISHED_BY {trait: "value-alignment and self-reflection"}]->(intelligence);

// ========================================
// WISDOM TRAITS (from psychological models)
// ========================================

// Cognitive traits
MERGE (ih:Trait {name: "Intellectual humility"})
SET ih.category = "cognitive",
    ih.description = "Recognition of the limits of one's knowledge; openness to revising beliefs",
    ih.measurement_scales = ["3D-WS", "MORE", "San Diego Wisdom Scale"];

MERGE (pt:Trait {name: "Perspective-taking"})
SET pt.category = "cognitive",
    pt.description = "Ability to consider multiple viewpoints and understand others' mental states",
    pt.measurement_scales = ["Grossmann Wise Reasoning Scale"];

MERGE (meta:Trait {name: "Metacognition"})
SET meta.category = "cognitive",
    meta.description = "Monitoring and control of one's own cognitive processes",
    meta.measurement_scales = ["Metacognitive Awareness Inventory"];

MERGE (uc:Trait {name: "Uncertainty management"})
SET uc.category = "cognitive",
    uc.description = "Comfort with ambiguity; recognition of contextual contingency",
    uc.measurement_scales = ["Grossmann Wise Reasoning Scale"];

// Reflective traits
MERGE (sr:Trait {name: "Self-reflection"})
SET sr.category = "reflective",
    sr.description = "Introspective awareness of one's values, biases, and motivations",
    sr.measurement_scales = ["Self-Reflection and Insight Scale"];

MERGE (ctx:Trait {name: "Contextualism"})
SET ctx.category = "reflective",
    ctx.description = "Sensitivity to context; recognition that truth is often situational",
    ctx.measurement_scales = ["Grossmann Wise Reasoning Scale"];

// Affective traits
MERGE (er:Trait {name: "Emotion regulation"})
SET er.category = "affective",
    er.description = "Ability to manage emotional responses adaptively",
    er.measurement_scales = ["Difficulties in Emotion Regulation Scale"];

MERGE (comp:Trait {name: "Compassion"})
SET comp.category = "affective",
    comp.description = "Empathetic concern and motivation to alleviate others' suffering",
    comp.measurement_scales = ["Compassion Scale"];

// Pro-social traits
MERGE (cg:Trait {name: "Concern for common good"})
SET cg.category = "pro-social",
    cg.description = "Orientation toward collective wellbeing over narrow self-interest",
    cg.measurement_scales = ["San Diego Wisdom Scale"];

MERGE (ps:Trait {name: "Pro-social orientation"})
SET ps.category = "pro-social",
    ps.description = "Preference for cooperative, mutually beneficial outcomes",
    ps.measurement_scales = ["Social Value Orientation measure"];

MERGE (vr:Trait {name: "Value relativism"})
SET vr.category = "reflective",
    vr.description = "Recognition of diverse value systems; tolerance for different perspectives",
    vr.measurement_scales = ["3D-WS"];

// Link traits to Wisdom
MERGE (wisdom)-[:HAS_TRAIT]->(ih);
MERGE (wisdom)-[:HAS_TRAIT]->(pt);
MERGE (wisdom)-[:HAS_TRAIT]->(meta);
MERGE (wisdom)-[:HAS_TRAIT]->(uc);
MERGE (wisdom)-[:HAS_TRAIT]->(sr);
MERGE (wisdom)-[:HAS_TRAIT]->(ctx);
MERGE (wisdom)-[:HAS_TRAIT]->(er);
MERGE (wisdom)-[:HAS_TRAIT]->(comp);
MERGE (wisdom)-[:HAS_TRAIT]->(cg);
MERGE (wisdom)-[:HAS_TRAIT]->(ps);
MERGE (wisdom)-[:HAS_TRAIT]->(vr);

// Link relevant traits to Artificial Wisdom
MERGE (aw)-[:REQUIRES_TRAIT]->(ih);
MERGE (aw)-[:REQUIRES_TRAIT]->(pt);
MERGE (aw)-[:REQUIRES_TRAIT]->(meta);
MERGE (aw)-[:REQUIRES_TRAIT]->(uc);
MERGE (aw)-[:REQUIRES_TRAIT]->(cg);
MERGE (aw)-[:REQUIRES_TRAIT]->(ps);

// ========================================
// AI ARCHITECTURES AND CAPABILITIES
// ========================================

// Self-improving architectures
MERGE (dgm:Architecture {name: "Darwin Gödel Machine"})
SET dgm.capabilities = ["self-modification", "open-ended-improvement", "proof-search", "archive-of-agents"],
    dgm.year = 2024,
    dgm.description = "Self-improving AI using proof search and population-based evolution of agent strategies",
    dgm.url = "https://arxiv.org/abs/2410.06087";

MERGE (seal:Architecture {name: "SEAL (Self-Adapting LLM)"})
SET seal.capabilities = ["self-adaptation", "synthetic-data-generation", "iterative-refinement"],
    seal.year = 2024,
    seal.description = "LLM that generates synthetic data to self-adapt without human annotations",
    seal.url = "";

MERGE (self_reward:Architecture {name: "Self-Rewarding LLM"})
SET self_reward.capabilities = ["self-judging", "LLM-as-a-judge", "iterative-improvement"],
    self_reward.year = 2024,
    self_reward.description = "LLM that evaluates its own outputs and uses self-generated rewards for training",
    self_reward.url = "";

MERGE (ai_scientist:Architecture {name: "The AI Scientist"})
SET ai_scientist.capabilities = ["automated-research", "self-review", "idea-generation", "code-execution"],
    ai_scientist.year = 2024,
    ai_scientist.description = "Fully automated scientific discovery system that generates ideas, writes code, runs experiments, and writes papers",
    ai_scientist.url = "https://github.com/SakanaAI/AI-Scientist";

// Machine capabilities (traits for machines)
MERGE (self_mod:Trait {name: "Self-modification"})
SET self_mod.category = "machine_capability",
    self_mod.description = "Ability to modify own code, architecture, or training process";

MERGE (self_eval:Trait {name: "Self-evaluation"})
SET self_eval.category = "machine_capability",
    self_eval.description = "Ability to assess quality of own outputs (LLM-as-a-judge)";

MERGE (open_ended:Trait {name: "Open-ended self-improvement"})
SET open_ended.category = "machine_capability",
    open_ended.description = "Capacity for unbounded improvement without predefined objective ceiling";

MERGE (value_align:Trait {name: "Value alignment"})
SET value_align.category = "machine_capability",
    value_align.description = "Mechanisms to align behavior with human values and preferences";

// Link architectures to capabilities
MERGE (dgm)-[:IMPLEMENTS_ASPECT_OF]->(self_mod);
MERGE (dgm)-[:IMPLEMENTS_ASPECT_OF]->(open_ended);

MERGE (seal)-[:IMPLEMENTS_ASPECT_OF]->(self_mod);
MERGE (seal)-[:IMPLEMENTS_ASPECT_OF {mechanism: "synthetic data generation"}]->(meta);

MERGE (self_reward)-[:IMPLEMENTS_ASPECT_OF]->(self_eval);
MERGE (self_reward)-[:IMPLEMENTS_ASPECT_OF {mechanism: "LLM-as-a-judge"}]->(meta);

MERGE (ai_scientist)-[:IMPLEMENTS_ASPECT_OF]->(self_eval);
MERGE (ai_scientist)-[:IMPLEMENTS_ASPECT_OF]->(meta);
MERGE (ai_scientist)-[:IMPLEMENTS_ASPECT_OF]->(open_ended);

// Link capabilities to wisdom traits (showing partial alignment)
MERGE (self_eval)-[:PARTIAL_IMPLEMENTATION_OF {gap: "lacks epistemic humility"}]->(meta);
MERGE (open_ended)-[:PARTIAL_IMPLEMENTATION_OF {gap: "lacks value-orientation"}]->(sr);

// Link architectures to concepts
MERGE (dgm)-[:ORIENTED_TOWARD]->(ai);
MERGE (seal)-[:ORIENTED_TOWARD]->(ai);
MERGE (self_reward)-[:ORIENTED_TOWARD]->(ai);
MERGE (ai_scientist)-[:ORIENTED_TOWARD]->(ai);

// Potential for wisdom (aspirational links)
MERGE (dgm)-[:COULD_CONTRIBUTE_TO {aspect: "if value-aligned"}]->(computational_sapience);
MERGE (self_reward)-[:COULD_CONTRIBUTE_TO {aspect: "metacognitive evaluation"}]->(aw);
