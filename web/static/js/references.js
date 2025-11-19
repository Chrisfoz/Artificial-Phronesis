/**
 * References page JavaScript
 */

let allPapers = [];
let allAuthors = [];

// Load data on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadPapers();
    await loadAuthors();
    setupEventListeners();
});

/**
 * Load all papers from the knowledge graph
 */
async function loadPapers() {
    try {
        const response = await fetch('/api/papers');
        allPapers = await response.json();

        displayPapers(allPapers);
        updateStats();

    } catch (error) {
        console.error('Error loading papers:', error);
        document.getElementById('papers-list').innerHTML =
            '<p>Error loading papers. Make sure the database is initialized.</p>';
    }
}

/**
 * Load all authors
 */
async function loadAuthors() {
    try {
        const response = await fetch('/api/authors');
        allAuthors = await response.json();

        displayAuthors(allAuthors);

    } catch (error) {
        console.error('Error loading authors:', error);
    }
}

/**
 * Display papers in the list
 */
function displayPapers(papers) {
    const container = document.getElementById('papers-list');

    if (papers.length === 0) {
        container.innerHTML = '<p>No papers found in the knowledge graph yet. Add PDFs to data/papers/ and run the ingestion script.</p>';
        return;
    }

    container.innerHTML = '';

    papers.forEach(paper => {
        const paperDiv = document.createElement('div');
        paperDiv.className = 'paper';

        const title = document.createElement('h4');
        title.textContent = paper.title || 'Untitled';
        paperDiv.appendChild(title);

        if (paper.authors && paper.authors.length > 0) {
            const authors = document.createElement('p');
            authors.className = 'authors';
            authors.textContent = paper.authors.join(', ');
            paperDiv.appendChild(authors);
        }

        if (paper.year || paper.venue) {
            const meta = document.createElement('p');
            meta.className = 'meta';
            let metaText = '';
            if (paper.year) metaText += paper.year;
            if (paper.venue) metaText += ` | ${paper.venue}`;
            meta.textContent = metaText;
            paperDiv.appendChild(meta);
        }

        if (paper.abstract) {
            const abstract = document.createElement('p');
            abstract.className = 'abstract';
            const shortAbstract = paper.abstract.length > 300
                ? paper.abstract.substring(0, 300) + '...'
                : paper.abstract;
            abstract.textContent = shortAbstract;
            paperDiv.appendChild(abstract);
        }

        if (paper.concepts && paper.concepts.length > 0) {
            const concepts = document.createElement('p');
            concepts.className = 'concepts';
            concepts.innerHTML = '<strong>Concepts:</strong> ' +
                paper.concepts.filter(c => c).join(', ');
            paperDiv.appendChild(concepts);
        }

        if (paper.doi) {
            const doi = document.createElement('p');
            doi.className = 'doi';
            doi.innerHTML = `<a href="https://doi.org/${paper.doi}" target="_blank">DOI: ${paper.doi}</a>`;
            paperDiv.appendChild(doi);
        }

        container.appendChild(paperDiv);
    });
}

/**
 * Display authors
 */
function displayAuthors(authors) {
    const container = document.getElementById('authors-list');

    if (authors.length === 0) {
        return;
    }

    container.innerHTML = '';

    authors.forEach(author => {
        const authorDiv = document.createElement('div');
        authorDiv.className = 'author-card';

        const name = document.createElement('h4');
        name.textContent = author.name;
        authorDiv.appendChild(name);

        const paperCount = document.createElement('p');
        paperCount.textContent = `${author.paper_count} paper${author.paper_count !== 1 ? 's' : ''}`;
        authorDiv.appendChild(paperCount);

        if (author.discipline) {
            const discipline = document.createElement('p');
            discipline.className = 'discipline';
            discipline.textContent = author.discipline;
            authorDiv.appendChild(discipline);
        }

        container.appendChild(authorDiv);
    });
}

/**
 * Update statistics
 */
function updateStats() {
    const stats = document.getElementById('paper-stats');
    stats.textContent = `Showing ${allPapers.length} paper${allPapers.length !== 1 ? 's' : ''}`;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search filter
    document.getElementById('search-papers').addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filtered = allPapers.filter(paper =>
            (paper.title && paper.title.toLowerCase().includes(searchTerm)) ||
            (paper.authors && paper.authors.some(a => a.toLowerCase().includes(searchTerm))) ||
            (paper.abstract && paper.abstract.toLowerCase().includes(searchTerm))
        );
        displayPapers(filtered);
    });

    // Domain filter
    document.getElementById('domain-filter').addEventListener('change', (e) => {
        const domain = e.target.value;
        if (domain === 'all') {
            displayPapers(allPapers);
        } else {
            const filtered = allPapers.filter(paper =>
                paper.concepts && paper.concepts.some(c =>
                    c.toLowerCase().includes(domain.toLowerCase())
                )
            );
            displayPapers(filtered);
        }
    });
}
