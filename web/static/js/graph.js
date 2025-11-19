/**
 * Interactive knowledge graph visualization using vis.js
 */

let network = null;
let allGraphData = null;
let physicsEnabled = true;

// Color scheme for different node types
const colorScheme = {
    Concept: {
        border: '#2B7CE9',
        background: '#97C2FC',
        highlight: { border: '#2B7CE9', background: '#D2E5FF' }
    },
    Trait: {
        border: '#FFA500',
        background: '#FFDB99',
        highlight: { border: '#FFA500', background: '#FFE6B3' }
    },
    Architecture: {
        border: '#7C29F0',
        background: '#C2A5F7',
        highlight: { border: '#7C29F0', background: '#DCC5FF' }
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadStats();
    await loadConcepts();
    await loadGraph();
    setupEventListeners();
});

/**
 * Load database statistics
 */
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('concept-count').textContent = stats.node_count;
        document.getElementById('relationship-count').textContent = stats.relationship_count;

        // Count papers
        const papersResponse = await fetch('/api/papers');
        const papers = await papersResponse.json();
        document.getElementById('paper-count').textContent = papers.length;

    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

/**
 * Load concepts for dropdown
 */
async function loadConcepts() {
    try {
        const response = await fetch('/api/concepts');
        const concepts = await response.json();

        const select = document.getElementById('concept-select');
        concepts.forEach(concept => {
            const option = document.createElement('option');
            option.value = concept.name;
            option.textContent = concept.name;
            select.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading concepts:', error);
    }
}

/**
 * Load and render the full knowledge graph
 */
async function loadGraph(conceptName = null) {
    try {
        let url = '/api/graph/full';
        if (conceptName) {
            url = `/api/graph/concept/${encodeURIComponent(conceptName)}`;
        }

        const response = await fetch(url);
        allGraphData = await response.json();

        renderGraph(allGraphData);

    } catch (error) {
        console.error('Error loading graph:', error);
        alert('Failed to load graph. Make sure the database is initialized and populated.');
    }
}

/**
 * Render the graph using vis.js
 */
function renderGraph(graphData) {
    const container = document.getElementById('knowledge-graph');

    // Transform nodes for vis.js
    const nodes = graphData.nodes.map(node => ({
        id: node.id,
        label: node.name || 'Unknown',
        title: createNodeTooltip(node),
        group: node.label,
        color: colorScheme[node.label] || colorScheme.Concept,
        font: { size: 14, color: '#000000' },
        shape: getNodeShape(node.label),
        data: node  // Store original data
    }));

    // Transform edges for vis.js
    const edges = graphData.edges.map(edge => ({
        from: edge.source,
        to: edge.target,
        label: formatRelationshipLabel(edge.type),
        arrows: 'to',
        font: { size: 10, align: 'middle' },
        color: { color: '#848484', highlight: '#000000' },
        smooth: { type: 'continuous' }
    }));

    const data = { nodes, edges };

    const options = {
        nodes: {
            shape: 'dot',
            size: 16,
            borderWidth: 2,
            borderWidthSelected: 4
        },
        edges: {
            width: 2,
            selectionWidth: 4
        },
        physics: {
            enabled: physicsEnabled,
            stabilization: { iterations: 200 },
            barnesHut: {
                gravitationalConstant: -8000,
                centralGravity: 0.3,
                springLength: 150,
                springConstant: 0.04
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            navigationButtons: true,
            keyboard: true
        },
        layout: {
            improvedLayout: true
        }
    };

    // Create network
    network = new vis.Network(container, data, options);

    // Event handlers
    network.on('click', onNodeClick);
    network.on('stabilizationIterationsDone', () => {
        console.log('Graph stabilized');
    });
}

/**
 * Create tooltip HTML for a node
 */
function createNodeTooltip(node) {
    let tooltip = `<strong>${node.name}</strong><br/>`;
    tooltip += `<em>${node.label}</em><br/>`;

    if (node.short_def) {
        tooltip += `<br/>${node.short_def}`;
    } else if (node.description) {
        const shortDesc = node.description.substring(0, 150) + '...';
        tooltip += `<br/>${shortDesc}`;
    }

    if (node.domain) {
        tooltip += `<br/><br/><small>Domain: ${node.domain}</small>`;
    }

    return tooltip;
}

/**
 * Get node shape based on type
 */
function getNodeShape(label) {
    switch (label) {
        case 'Concept':
            return 'dot';
        case 'Trait':
            return 'diamond';
        case 'Architecture':
            return 'square';
        default:
            return 'dot';
    }
}

/**
 * Format relationship label for display
 */
function formatRelationshipLabel(relType) {
    return relType.replace(/_/g, ' ').toLowerCase();
}

/**
 * Handle node click
 */
async function onNodeClick(params) {
    if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = network.body.data.nodes.get(nodeId);

        if (node && node.data && node.data.name) {
            await loadConceptDetails(node.data.name);
        }
    }
}

/**
 * Load and display concept details
 */
async function loadConceptDetails(conceptName) {
    try {
        const response = await fetch(`/api/concept/${encodeURIComponent(conceptName)}`);
        const details = await response.json();

        // Update details panel
        document.getElementById('detail-name').textContent = details.name;
        document.getElementById('detail-description').textContent =
            details.description || details.short_def || 'No description available.';

        // Show traits
        if (details.traits && details.traits.length > 0) {
            const traitsList = document.getElementById('traits-list');
            traitsList.innerHTML = '';
            details.traits.forEach(trait => {
                const li = document.createElement('li');
                li.textContent = `${trait.name} (${trait.type})`;
                if (trait.description) {
                    li.title = trait.description;
                }
                traitsList.appendChild(li);
            });
            document.getElementById('detail-traits').style.display = 'block';
        } else {
            document.getElementById('detail-traits').style.display = 'none';
        }

        // Show papers
        if (details.papers && details.papers.length > 0) {
            const papersList = document.getElementById('papers-list');
            papersList.innerHTML = '';
            details.papers.forEach(paper => {
                const li = document.createElement('li');
                li.textContent = `${paper.title} (${paper.year || 'n.d.'})`;
                papersList.appendChild(li);
            });
            document.getElementById('detail-papers').style.display = 'block';
        } else {
            document.getElementById('detail-papers').style.display = 'none';
        }

        // Show details panel
        document.getElementById('concept-details').style.display = 'block';

    } catch (error) {
        console.error('Error loading concept details:', error);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Concept selection
    document.getElementById('concept-select').addEventListener('change', (e) => {
        const conceptName = e.target.value;
        if (conceptName) {
            loadGraph(conceptName);
        } else {
            loadGraph();
        }
    });

    // Reset graph
    document.getElementById('reset-graph').addEventListener('click', () => {
        if (network) {
            network.fit();
        }
    });

    // Toggle physics
    document.getElementById('toggle-physics').addEventListener('click', () => {
        physicsEnabled = !physicsEnabled;
        if (network) {
            network.setOptions({ physics: { enabled: physicsEnabled } });
        }
    });

    // Ask question
    document.getElementById('ask-btn').addEventListener('click', askQuestion);
    document.getElementById('question-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            askQuestion();
        }
    });
}

/**
 * Ask a question using GraphRAG
 */
async function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value.trim();

    if (!question) return;

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('answer-container').style.display = 'none';

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });

        const result = await response.json();

        // Show answer
        document.getElementById('answer-text').textContent = result.answer;
        document.getElementById('answer-container').style.display = 'block';

    } catch (error) {
        console.error('Error asking question:', error);
        document.getElementById('answer-text').textContent =
            'Error: Could not get answer. Make sure OpenAI API key is configured.';
        document.getElementById('answer-container').style.display = 'block';
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}
