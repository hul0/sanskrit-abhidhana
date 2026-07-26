# CLAUDE.md - Guidelines for Claude Agent

This file provides project-specific context, commands, and code conventions for Claude agentic workflows operating on **Sanskrit Abhidhana**.

---

## 🚀 Common Commands

### Development & Execution
- **Run API Server**: `python3 run.py` or `uvicorn app.main:app --reload`
- **Build SQLite Indexes & FTS5**: `python3 scripts/build_indexes.py`
- **Run Automated Tests**: `python3 -m unittest discover tests`
- **Install Dependencies**: `pip install -r requirements.txt` or `uv pip install -r requirements.txt`

---

## 📐 Code Style & Architecture Conventions

1. **Python Conventions**:
   - Use standard library `typing` hints (`Tuple`, `List`, `Dict`, `Optional`, `Any`).
   - Clean docstrings for functions and classes.
   - Do NOT introduce unneeded external dependencies. Keep the system lightweight (<300MB RAM target).

2. **Transliteration Module**:
   - All script conversion must go through `app/transliterate.py` using `indic_transliteration.sanscript`.
   - Never write ad-hoc manual regex transliterators when `sanscript.transliterate()` or `SchemeMap` can be used.

3. **Database Layer**:
   - Connections must be created using `get_db()` read-only context manager in `app/database.py`.
   - SQLite queries must use parameterized placeholders (`?`) to prevent SQL injection.
   - Preserved SQLite pragmas: `PRAGMA query_only = ON;`, `PRAGMA journal_mode = WAL;`, `PRAGMA mmap_size = 268435456;`.

4. **Web Frontend**:
   - Keep HTML (`static/index.html`), CSS (`static/style.css`), and JavaScript (`static/app.js`) strictly separated into modular files.
   - Preserve Saffron Dark (default) and Saffron Light theme switching with `data-theme` attribute and `localStorage`.

5. **Path Resolution**:
   - Include `site.getusersitepackages()` in `sys.path` across executable modules to support sandboxed environment execution.
