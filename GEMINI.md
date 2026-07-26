# GEMINI.md - Guidelines for Gemini Agent

This document outlines key technical principles and operational workflows for Gemini AI agents pair programming on the **Sanskrit Abhidhana** codebase.

---

## 🎯 Primary Operational Objectives

1. **Aesthetic Excellence & Premium UI**:
   - The Saffron web application (`static/`) must deliver state-of-the-art UI styling (glassmorphism, smooth micro-animations, Saffron Light & Saffron Dark theme switching, responsive typography).

2. **Empirical Verification**:
   - Never declare success without executing automated unit tests (`python3 -m unittest discover tests`) or running index verification (`python3 scripts/build_indexes.py`).

3. **Memory & Throughput Integrity**:
   - Maintain RAM usage strictly under **300 MB** (target ~40MB RSS).
   - Ensure REST API latency remains under **5ms**.

4. **No Superficial Symptom Patches**:
   - Trace missing data or errors to their underlying root cause rather than wrapping functions in silent `try...except` blocks or commenting out assertions.

---

## 📁 Key File Map

| File Path | Description |
| :--- | :--- |
| [app/main.py](file:///home/johan/CRINE/sanskrit-abhidhana/app/main.py) | FastAPI app, CORS, static server, metrics |
| [app/database.py](file:///home/johan/CRINE/sanskrit-abhidhana/app/database.py) | SQLite read-only connection pool & FTS5 search |
| [app/parser.py](file:///home/johan/CRINE/sanskrit-abhidhana/app/parser.py) | MW XML parser & human-readable definition builder |
| [app/abbreviations.py](file:///home/johan/CRINE/sanskrit-abhidhana/app/abbreviations.py) | Abbreviation expander (1,295 entries loaded) |
| [app/transliterate.py](file:///home/johan/CRINE/sanskrit-abhidhana/app/transliterate.py) | Script transliteration module |
| [scripts/build_indexes.py](file:///home/johan/CRINE/sanskrit-abhidhana/scripts/build_indexes.py) | SQLite WAL mode, `key_ascii`, and `mw_fts` builder |
| [static/index.html](file:///home/johan/CRINE/sanskrit-abhidhana/static/index.html) | Single-page Web UI |
| [static/style.css](file:///home/johan/CRINE/sanskrit-abhidhana/static/style.css) | Saffron Dark & Light theme stylesheet |
| [static/app.js](file:///home/johan/CRINE/sanskrit-abhidhana/static/app.js) | Frontend JS application logic |
