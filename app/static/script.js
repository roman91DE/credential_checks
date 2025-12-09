const searchInput = document.getElementById('search-input');
const searchType = document.getElementById('search-type');
const ignoreCase = document.getElementById('ignore-case');
const substring = document.getElementById('substring');
const output = document.getElementById('output');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const count = document.getElementById('count');

// Allow Enter key to search
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') search();
});

async function search() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('Please enter a search query');
        return;
    }

    loading.style.display = 'block';
    error.style.display = 'none';
    output.innerHTML = '';

    try {
        const endpoint = `/search/${searchType.value}`;
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query_string: query,
                ignore_case: ignoreCase.checked,
                include_substring_matches: substring.checked,
            }),
        });

        if (!response.ok) {
            throw new Error('Search failed');
        }

        const results = await response.json();
        displayResults(results);
    } catch (err) {
        showError('Error during search: ' + err.message);
    } finally {
        loading.style.display = 'none';
    }
}

function displayResults(results) {
    if (results.length === 0) {
        output.innerHTML = '<div style="color: #999; padding: 20px; text-align: center;">No matches found</div>';
        count.textContent = '0 matches';
        return;
    }

    output.innerHTML = results.map((result) => `
        <div class="result-item">
            <div class="result-value">${escapeHtml(result.matched_string)}</div>
            <div class="result-source">${escapeHtml(result.source)}</div>
        </div>
    `).join('');

    count.textContent = `${results.length} match${results.length !== 1 ? 'es' : ''}`;
}

function clearResults() {
    output.innerHTML = '';
    searchInput.value = '';
    count.textContent = '0 matches';
    error.style.display = 'none';
    searchInput.focus();
}

function showError(message) {
    error.textContent = message;
    error.style.display = 'block';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
