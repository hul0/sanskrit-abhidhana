# AGENT.md - Guidelines for Autonomous AI Coding Agents

This document provides architectural rules, coding standards, performance constraints, and execution workflows for autonomous AI coding agents (such as Antigravity, Gemini, Claude, and Cursor) working on the **Sanskrit Abhidhana** codebase.

---

## 🏛 System Architecture Overview

Sanskrit Abhidhana is a high-throughput, memory-efficient (<300MB RAM) Python REST API system and Web UI for Monier-Williams Sanskrit dictionary lookups.

```
sanskrit-abhidhana/
├── app/
│   ├── main.py          # FastAPI REST API application, CORS, static mounting & telemetry
│   ├── database.py      # Read-only SQLite connection pool, indexed lookups, FTS5 search
│   ├── parser.py        # Monier-Williams XML parser & human-readable definition builder
│   ├── abbreviations.py # Expands 1,295 abbreviations & literary citations from mwab/mwauthtooltips
│   └── transliterate.py # Script conversion engine (indic_transliteration.sanscript)
├── data/
│   └── mw/              # SQLite databases (mw.sqlite, mwab.sqlite, mwauthtooltips.sqlite)
├── scripts/
│   └── build_indexes.py # Index builder script (populates key_ascii, mw_fts FTS5, WAL mode)
├── static/
│   ├── index.html       # Single-page web application HTML
│   ├── style.css        # Saffron Dark & Saffron Light theme stylesheet
│   └── app.js           # Frontend JS application logic (search, autocomplete, theme switcher)
├── tests/
│   └── test_api.py      # Automated test suite
├── docs/
│   └── API.md           # REST API specification
├── run.py               # Uvicorn server launcher
└── requirements.txt     # Dependency manifest
```

---

## ⚠️ Critical Constraints & SLAs

1. **Memory Ceiling (< 300MB RAM RSS)**:
   - The entire application must operate strictly under **300 MB RAM**.
   - Do NOT load large data structures or raw SQLite tables entirely into Python memory.
   - Baseline memory usage should remain between **35 MB – 60 MB RSS**. Verify RAM via `/metrics` endpoint.

2. **Search Latency SLA (< 5ms)**:
   - Headword lookups and FTS5 English searches must respond in **sub-5ms**.
   - SQLite Write-Ahead Logging (WAL) mode, read-only pragmas (`query_only=ON`, `mmap_size=268435456`, `cache_size=-64000`), and indexed lookups (`idx_mw_key`, `idx_mw_key_ascii`) must be preserved.

3. **User Site-Packages Resolution**:
   - Every executable entrypoint (`run.py`, `app/main.py`, `scripts/build_indexes.py`, `tests/test_api.py`) MUST include `site.getusersitepackages()` in `sys.path` to ensure `indic-transliteration` and other user site-packages are resolved cleanly across sandboxed environments.

4. **No Superficial Symptom Patches**:
   - Never resolve errors by masking exceptions, swallowing tracebacks, commenting out broken assertions, or returning dummy fallbacks.

---

## 🛠 Key Commands for Agents

### 1. Build Database Indices
```bash
python3 scripts/build_indexes.py
```

### 2. Run Test Suite
```bash
python3 -m unittest discover tests
```

### 3. Launch Server
```bash
python3 run.py
```
or
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 4. Benchmark API Metrics & RAM
```bash
curl -s http://127.0.0.1:8000/metrics
```

---

## 🎨 Theme & UI Rules

- The web interface supports dual themes: **Saffron Dark** (default) and **Saffron Light**.
- Custom styling must use CSS variables defined in `static/style.css` (`var(--accent-saffron)`, `var(--card-bg)`, `var(--text-main)`, etc.).
- Never hardcode static colors that break theme switching.
