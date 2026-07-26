<div align="center">

# Sanskrit Abhidhana

### संस्कृत अभिधानम्

**High-Throughput, Low-Latency Sanskrit Lexicon REST API & Web Interface**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI Framework](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite FTS5](https://img.shields.io/badge/SQLite-FTS5-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/fts5.html)
[![RAM RSS](https://img.shields.io/badge/RAM_Usage-%3C100MB-2ea44f?style=for-the-badge)]()
[![License AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue?style=for-the-badge)](LICENSE)

---

</div>

## Overview

**Sanskrit Abhidhana** is a high-throughput, low-memory Python REST API system and interactive single-page web lexicon for Sanskrit-to-English dictionary translations based on the **Monier-Williams** dictionary (286,525 entries).

Engineered for extreme performance, it provides sub-millisecond headword lookups, multi-script Indic transliteration, English full-text search (FTS5), and automated dictionary abbreviation expansion while consuming under 60 MB RAM RSS.

---

## Core Capabilities

| Capability | Description |
| :--- | :--- |
| **Multi-Script Engine** | Native support for **Devanagari** (`कृष्ण`, `शिव`), **IAST** (`kṛṣṇa`, `śiva`), **Harvard-Kyoto** (`kRSNa`), **ITRANS**, **Velthuis**, **SLP1**, and **Loose ASCII Phonetic Fallback** (`krishna`, `shiva`, `dharma`). |
| **Indic Transliteration** | Real-time script conversions across Devanagari, Telugu, Bengali, Kannada, Malayalam, Tamil, Gujarati, Gurmukhi, Oriya, and Grantha via `indic-transliteration`. |
| **Abbreviation Expander** | Automatically expands 1,200+ cryptic dictionary abbreviations (e.g. `f.` -> `feminine`, `mfn.` -> `adjective`, `RV.` -> `Ṛg-veda`, `MBh.` -> `Mahābhārata`). |
| **Full-Text Search (FTS5)** | Sub-millisecond indexed `key_ascii` lookups (~0.7ms) and SQLite **FTS5** reverse English definition search. |
| **Web UI** | Single-Page Application (SPA) with **Saffron Dark** & **Saffron Light** themes, debounced autocomplete, and live script conversion preview. |
| **Micro-Memory Footprint** | Operates at **~40–60 MB RAM RSS** (strict SLA < 300 MB) utilizing SQLite Write-Ahead Logging (WAL) and memory-mapped IO. |

---

## System Architecture

```
+-------------------------------------------------------------------+
|               Web Interface (static/index.html)                   |
|              Saffron Theme Engine & Live Preview                  |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               FastAPI REST Engine (app/main.py)                   |
|   /api/v1/define      /api/v1/search     /api/v1/transliterate   |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|             Sanskrit Transliteration & Parser Modules             |
|              (app/transliterate.py & app/parser.py)               |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                 SQLite Database (data/mw/mw.sqlite)               |
|            WAL Mode | Indexed key_ascii | FTS5 Virtual Table    |
+-------------------------------------------------------------------+
```

---

## Quick Start

### 1. Installation

Clone the repository and install dependencies using `uv` or `pip`:

```bash
git clone https://github.com/hul0/sanskrit-abhidhana.git
cd sanskrit-abhidhana
uv pip install -r requirements.txt
```

### 2. Build Database Indices

Run the database builder script to generate `key_ascii` indices, populate the FTS5 virtual table, and set WAL journal mode:

```bash
python3 scripts/build_indexes.py
```

### 3. Launch the Server

Start the application using `uvicorn`:

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Alternatively, run via the standard launcher:

```bash
python3 run.py
```

Open `http://127.0.0.1:8000/` in your web browser.

---

## REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/define/{word}` | `GET` | Headword definition lookup (Devanagari, IAST, SLP1, HK, loose ASCII) |
| `/api/v1/search` | `GET` | Unified dictionary search (`type=headword`, `type=english`, or `type=autocomplete`) |
| `/api/v1/transliterate` | `GET` | Transliterate text across 15+ Indic & Roman schemes |
| `/api/v1/autocomplete` | `GET` | Fast prefix autocompletion for search bars |
| `/health` | `GET` | System health check & database connection status |
| `/metrics` | `GET` | Live RAM RSS usage and latency telemetry |
| `/docs` | `GET` | Interactive Swagger API documentation |
| `/redoc` | `GET` | ReDoc API documentation |

For comprehensive payload schemas, query parameters, and cURL examples, see [docs/API.md](docs/API.md).

---

## Automated Verification

Run the comprehensive unit test suite:

```bash
python3 -m unittest discover tests
```

---

## Author & Maintainer

- **Creator & Developer**: **Rupam Ghosh**
- **GitHub**: [@hul0](https://github.com/hul0)
- **Email**: [hulo@crine.in](mailto:hulo@crine.in)

---

## Data Attribution

- **Database Source**: Monier-Williams Sanskrit-English Dictionary SQLite Database courtesy of the **Cologne Sanskrit Lexicon** project ([csl-sqlite](https://github.com/sanskrit-lexicon/csl-sqlite)).
- Full attribution guidelines for reuse: [ATTRIBUTION.md](ATTRIBUTION.md).

---

## License & Legal Notices

Licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0). See [LICENSE](LICENSE) and [ATTRIBUTION.md](ATTRIBUTION.md) for full license and attribution terms.
