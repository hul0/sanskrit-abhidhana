/* ==========================================================================
   Sanskrit Abhidhana - Frontend JavaScript Application Logic
   Handles REST API searches, live transliteration, debounced autocompletion,
   and Saffron Light/Dark theme switching with localStorage persistence.
   ========================================================================== */

let currentSearchMode = 'headword';
let autocompleteDebounceTimer = null;

// Initialize theme on DOM load
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  fetchMetrics();
  
  // Input event listeners
  const inputEl = document.getElementById('search-input');
  if (inputEl) {
    inputEl.addEventListener('input', handleInputChange);
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        performSearch();
      }
    });
  }

  // Click outside listener for dropdown
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-card')) {
      hideAutocomplete();
    }
  });
});

/* --------------------------------------------------------------------------
   Theme Switching System (Saffron Dark <-> Saffron Light)
   -------------------------------------------------------------------------- */
function initTheme() {
  const savedTheme = localStorage.getItem('sanskrit_abhidhana_theme') || 'dark';
  setTheme(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  setTheme(newTheme);
}

function setTheme(themeName) {
  document.documentElement.setAttribute('data-theme', themeName);
  localStorage.setItem('sanskrit_abhidhana_theme', themeName);
  
  const labelEl = document.getElementById('theme-toggle-label');
  const iconEl = document.getElementById('theme-toggle-icon');
  
  if (themeName === 'light') {
    if (labelEl) labelEl.innerText = 'Saffron Light';
    if (iconEl) iconEl.innerText = '☀️';
  } else {
    if (labelEl) labelEl.innerText = 'Saffron Dark';
    if (iconEl) iconEl.innerText = '🌙';
  }
}

/* --------------------------------------------------------------------------
   Search Mode & Quick Query Selection
   -------------------------------------------------------------------------- */
function setSearchMode(mode, btnEl) {
  currentSearchMode = mode;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btnEl.classList.add('active');

  const input = document.getElementById('search-input');
  if (mode === 'english') {
    input.placeholder = "Type English word (e.g. liberation, knowledge, universe, sacrifice)...";
  } else if (mode === 'transliterate') {
    input.placeholder = "Type Sanskrit text to preview transliterations...";
  } else {
    input.placeholder = "Type Sanskrit word in Devanagari, IAST, or loose English (e.g. krishna, dharma)...";
  }
}

function quickSearch(query, mode = 'headword') {
  const inputEl = document.getElementById('search-input');
  if (inputEl) inputEl.value = query;

  if (mode === 'english') {
    const engTab = document.querySelectorAll('.tab-btn')[1];
    if (engTab) setSearchMode('english', engTab);
  } else {
    const headTab = document.querySelectorAll('.tab-btn')[0];
    if (headTab) setSearchMode('headword', headTab);
  }
  performSearch();
}

/* --------------------------------------------------------------------------
   Input Handling & Live Autocomplete
   -------------------------------------------------------------------------- */
function handleInputChange(e) {
  const val = e.target.value.strip ? e.target.value.strip() : e.target.value.trim();
  clearTimeout(autocompleteDebounceTimer);

  if (val.length >= 2 && currentSearchMode === 'headword') {
    autocompleteDebounceTimer = setTimeout(() => fetchAutocomplete(val), 200);
  } else {
    hideAutocomplete();
  }

  if (val.length >= 1) {
    fetchTransliteratePreview(val);
  } else {
    const prevEl = document.getElementById('trans-preview');
    if (prevEl) prevEl.style.display = 'none';
  }
}

async function fetchAutocomplete(prefix) {
  try {
    const resp = await fetch(`/api/v1/autocomplete?prefix=${encodeURIComponent(prefix)}&limit=8`);
    const data = await resp.json();

    const dropdown = document.getElementById('autocomplete-dropdown');
    if (data.suggestions && data.suggestions.length > 0) {
      dropdown.innerHTML = data.suggestions.map(s => `
        <div class="autocomplete-item" onclick="selectAutocomplete('${s.slp1}')">
          <span class="ac-devanagari">${s.devanagari}</span>
          <span class="ac-iast">${s.iast} (${s.ascii})</span>
        </div>
      `).join('');
      dropdown.style.display = 'block';
    } else {
      hideAutocomplete();
    }
  } catch (err) {
    hideAutocomplete();
  }
}

function hideAutocomplete() {
  const dropdown = document.getElementById('autocomplete-dropdown');
  if (dropdown) dropdown.style.display = 'none';
}

function selectAutocomplete(word) {
  const inputEl = document.getElementById('search-input');
  if (inputEl) inputEl.value = word;
  hideAutocomplete();
  performSearch();
}

/* --------------------------------------------------------------------------
   Live Transliteration Preview
   -------------------------------------------------------------------------- */
async function fetchTransliteratePreview(text) {
  try {
    const respIAST = await fetch(`/api/v1/transliterate?text=${encodeURIComponent(text)}&to_scheme=iast`);
    const dataIAST = await respIAST.json();

    const respDev = await fetch(`/api/v1/transliterate?text=${encodeURIComponent(text)}&to_scheme=devanagari`);
    const dataDev = await respDev.json();

    const prevIAST = document.getElementById('prev-iast');
    const prevDev = document.getElementById('prev-dev');
    const prevBox = document.getElementById('trans-preview');

    if (prevIAST) prevIAST.innerText = dataIAST.transliterated_text || '--';
    if (prevDev) prevDev.innerText = dataDev.transliterated_text || '--';
    if (prevBox) prevBox.style.display = 'block';
  } catch (err) {
    const prevBox = document.getElementById('trans-preview');
    if (prevBox) prevBox.style.display = 'none';
  }
}

/* --------------------------------------------------------------------------
   Main API Search Execution
   -------------------------------------------------------------------------- */
async function performSearch() {
  const inputEl = document.getElementById('search-input');
  if (!inputEl) return;
  
  const q = inputEl.value.trim();
  if (!q) return;

  hideAutocomplete();
  const spinnerEl = document.getElementById('spinner');
  const resultsListEl = document.getElementById('results-list');
  const resultsCountEl = document.getElementById('results-count');

  if (spinnerEl) spinnerEl.style.display = 'block';
  if (resultsListEl) resultsListEl.innerHTML = '';
  if (resultsCountEl) resultsCountEl.innerHTML = 'Searching...';

  const startTime = performance.now();

  try {
    let url = '';
    if (currentSearchMode === 'english') {
      url = `/api/v1/search?q=${encodeURIComponent(q)}&type=english&limit=50`;
    } else {
      url = `/api/v1/define/${encodeURIComponent(q)}?limit=50`;
    }

    const resp = await fetch(url);
    const data = await resp.json();
    const endTime = performance.now();

    const latency = (endTime - startTime).toFixed(2);
    const latEl = document.getElementById('telemetry-latency');
    if (latEl) latEl.innerText = `${latency} ms`;

    renderResults(data, q);
  } catch (err) {
    if (resultsCountEl) resultsCountEl.innerHTML = '<b style="color: #ef4444;">Search Error</b>';
    if (resultsListEl) {
      resultsListEl.innerHTML = `
        <div class="empty-state">Failed to connect to REST API. Please make sure server is running.</div>
      `;
    }
  } finally {
    if (spinnerEl) spinnerEl.style.display = 'none';
    fetchMetrics();
  }
}

/* --------------------------------------------------------------------------
   Render Search Results Cards
   -------------------------------------------------------------------------- */
function renderResults(data, query) {
  const count = data.count || 0;
  const results = data.results || [];

  const countEl = document.getElementById('results-count');
  if (countEl) {
    countEl.innerHTML = `Found <b>${count}</b> entries for "<b>${query}</b>" (${data.search_type || 'search'})`;
  }

  const listEl = document.getElementById('results-list');
  if (!listEl) return;

  if (results.length === 0) {
    listEl.innerHTML = `
      <div class="empty-state">
        No dictionary entries found for "${query}". Try loose ASCII (e.g. "krishna"), Devanagari ("कृष्ण"), or English definition search.
      </div>
    `;
    return;
  }

  listEl.innerHTML = results.map(item => {
    const dev = item.headword_devanagari || '';
    const iast = item.headword_iast || '';
    const lex = item.grammatical_info ? `<span class="grammatical-tag" title="${item.grammatical_code || ''}">${item.grammatical_info}</span>` : '';
    const hom = item.homonym ? `<span class="homonym-tag">${item.homonym}</span>` : '';
    const line = item.line_number ? `<span class="line-number">Line: ${item.line_number}</span>` : '';
    const snippet = item.fts_snippet ? `<div class="fts-snippet-box">Snippet: ${item.fts_snippet}</div>` : '';

    return `
      <div class="entry-card">
        <div class="entry-header">
          <div class="headword-box">
            <span class="headword-devanagari">${dev}</span>
            <span class="headword-iast">${iast}</span>
            ${lex}
            ${hom}
          </div>
          ${line}
        </div>
        <div class="entry-definition">${item.definition}</div>
        ${snippet}
      </div>
    `;
  }).join('');
}

/* --------------------------------------------------------------------------
   Fetch System Metrics (RAM Usage)
   -------------------------------------------------------------------------- */
async function fetchMetrics() {
  try {
    const resp = await fetch('/metrics');
    const data = await resp.json();
    const ramEl = document.getElementById('telemetry-ram');
    if (ramEl) ramEl.innerText = `${data.memory_rss_mb} MB / 300 MB`;
  } catch (e) {}
}
