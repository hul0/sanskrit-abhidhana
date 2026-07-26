# Sanskrit Abhidhana (संस्कृत अभिधानम्)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite FTS5](https://img.shields.io/badge/SQLite-FTS5-003B57.svg)](https://www.sqlite.org/fts5.html)
[![RAM Usage](https://img.shields.io/badge/RAM-%3C300MB%20(Target%20~40MB)-success.svg)]()
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)

**Sanskrit Abhidhana** is a high-throughput, low-memory (<300MB RAM) Python REST API system and interactive web lexicon for Sanskrit-to-English dictionary translations based on the **Monier-Williams** dictionary (286,525 entries).

---

## ✨ Key Features

- **Multi-Script & Transliteration Engine**:
  - Seamlessly handles searches in **Devanagari** (`कृष्ण`, `शिव`), **IAST** (`kṛṣṇa`, `śiva`), **Harvard-Kyoto** (`kRSNa`), **ITRANS** (`kR^iShNa`), **Velthuis**, **SLP1**, and **Loose ASCII Phonetic Fallback** (`krishna`, `shiva`, `dharma`, `rigveda`).
  - Supports Indic script transliterations across Devanagari, Telugu, Bengali, Kannada, Malayalam, Tamil, Gujarati, Gurmukhi, Oriya, and Grantha via `indic-transliteration`.
- **Human-Readable Abbreviation Expander**:
  - Automatically expands cryptic dictionary abbreviations (e.g. `f.` → `feminine`, `m.` → `masculine`, `mfn.` → `adjective`, `N.` → `Name`, `L.` → `Lexicographers`, `Comm.` → `Commentary`, `RV.` → `Ṛg-veda`, `MBh.` → `Mahābhārata`).
- **Sub-Millisecond Search & Full-Text English Search (FTS5)**:
  - Indexed `key_ascii` column for instant loose ASCII lookups (~0.7ms).
  - SQLite **FTS5 Virtual Table** (`mw_fts`) for reverse English definition searches (e.g., searching for `"liberation"`, `"knowledge"`, or `"universe"` inside definitions).
- **Interactive Web Interface**:
  - Single-Page Application (SPA) with **Saffron Light** and **Saffron Dark** theme switcher (stored in `localStorage`).
  - Live debounced autocomplete suggestions and instant live transliteration previews.
- **Micro-Memory Footprint & High Throughput**:
  - Uses **~40–60 MB RAM** RSS (far below the 300 MB limit).
  - SQLite Write-Ahead Logging (WAL) and memory-mapped IO (256MB mmap).

---

## 🏗 System Architecture

```
                                  +---------------------------------------+
                                  |     Web Interface (static/index.html)  |
                                  |  Saffron Theme Switcher (Dark/Light)  |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       FastAPI REST Engine (app/main)  |
                                  |  /api/v1/define     /api/v1/search    |
                                  |  /api/v1/transliterate  /health       |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   Sanskrits Transliteration Module    |
                                  |     (app/transliterate.py)            |
                                  |  Devanagari <-> IAST <-> SLP1 <-> HK   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |   Abbreviation Expander (app/parser)  |
                                  |   mwab.sqlite + mwauthtooltips.sqlite |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |      SQLite Database (data/mw)        |
                                  |   WAL Mode, key_ascii index, FTS5     |
                                  +---------------------------------------+
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/sanskrit-abhidhana.git
cd sanskrit-abhidhana
pip install -r requirements.txt
```

### 2. Build Database Indices

Run the index builder script to construct `key_ascii` indices, populates FTS5 virtual tables, and enables WAL mode:

```bash
python3 scripts/build_indexes.py
```

### 3. Launch the Server

Start the application server:

```bash
python3 run.py
```

Or using Uvicorn directly:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open **`http://127.0.0.1:8000/`** in your web browser.

---

## 📖 API Usage Overview

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /api/v1/define/{word}` | `GET` | Look up headword definition (Devanagari, IAST, SLP1, HK, loose ASCII) |
| `GET /api/v1/search` | `GET` | Unified search (`type=headword`, `type=english`, or `type=autocomplete`) |
| `GET /api/v1/transliterate` | `GET` | Transliterate text across 15+ Indic & Roman schemes |
| `GET /api/v1/autocomplete` | `GET` | Fast prefix autocompletion |
| `GET /health` | `GET` | System health check |
| `GET /metrics` | `GET` | Live RAM RSS usage and latency telemetry |
| `GET /docs` | `GET` | Interactive Swagger API documentation |
| `GET /redoc` | `GET` | ReDoc API documentation |

See [docs/API.md](docs/API.md) for full endpoint specifications, JSON schemas, and cURL examples.

---

## 🧪 Running Automated Tests

Run the comprehensive unit & integration test suite:

```bash
python3 -m unittest discover tests
```

---

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0). See [LICENSE](LICENSE) for details.
