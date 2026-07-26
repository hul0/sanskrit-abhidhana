"""
Sanskrit Abhidhana - Database Access Layer
Thread-safe SQLite database manager providing high-throughput read-only connection pooling,
indexed headword lookups, loose ASCII search, and FTS5 English full-text search.
"""

from app.transliterate import slp1_to_ascii
import sqlite3
import os
import contextlib
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mw', 'mw.sqlite')

from app.parser import parse_mw_entry
from app.transliterate import to_slp1_key, convert_script, normalize_ascii, slp1_to_iast, slp1_to_devanagari


def get_db_connection() -> sqlite3.Connection:
    """Create an optimized, read-only SQLite database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA query_only = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA mmap_size = 268435456;") # 256MB mmap
    conn.execute("PRAGMA cache_size = -64000;")   # 64MB RAM cache
    conn.row_factory = sqlite3.Row
    return conn


@contextlib.contextmanager
def get_db():
    """Context manager for SQLite connections."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()


def search_by_headword(query: str, script: str = 'auto', limit: int = 50, include_raw_xml: bool = False) -> Dict[str, Any]:
    """
    Search dictionary headwords by Devanagari, IAST, SLP1, HK, ITRANS, or loose ASCII.
    """
    slp1_key, detected_script = to_slp1_key(query, script)

    results = []
    with get_db() as conn:
        c = conn.cursor()

        # 1. Try exact SLP1 key match
        c.execute("SELECT key, lnum, data FROM mw WHERE key = ? ORDER BY lnum ASC LIMIT ?", (slp1_key, limit))
        rows = c.fetchall()

        # 2. Fallback to loose ASCII match if no exact SLP1 match found
        if not rows:
            ascii_query = normalize_ascii(query)
            c.execute("SELECT key, lnum, data FROM mw WHERE key_ascii = ? ORDER BY lnum ASC LIMIT ?", (ascii_query, limit))
            rows = c.fetchall()

        # 3. Secondary fallback: prefix search on key or key_ascii
        if not rows and len(query) >= 2:
            ascii_query = normalize_ascii(query)
            c.execute("SELECT key, lnum, data FROM mw WHERE key_ascii LIKE ? ORDER BY lnum ASC LIMIT ?", (ascii_query + '%', limit))
            rows = c.fetchall()

        for row in rows:
            parsed = parse_mw_entry(row['key'], row['lnum'], row['data'], include_raw_xml=include_raw_xml)
            results.append(parsed)

    return {
        "query": query,
        "detected_script": detected_script,
        "search_type": "headword",
        "count": len(results),
        "results": results
    }


def search_english_fts(query: str, limit: int = 50, include_raw_xml: bool = False) -> Dict[str, Any]:
    """
    Perform full-text search across English definitions using SQLite FTS5 index.
    """
    results = []
    clean_q = re_sub_fts(query)
    if not clean_q:
        return {"query": query, "search_type": "english_fts", "count": 0, "results": []}

    with get_db() as conn:
        c = conn.cursor()
        sql = """
            SELECT m.key, m.lnum, m.data, snippet(mw_fts, 2, '<b>', '</b>', '...', 15) as snippet
            FROM mw_fts f
            JOIN mw m ON f.key = m.key AND f.lnum = m.lnum
            WHERE mw_fts MATCH ?
            LIMIT ?
        """
        c.execute(sql, (clean_q, limit))
        rows = c.fetchall()

        for row in rows:
            parsed = parse_mw_entry(row['key'], row['lnum'], row['data'], include_raw_xml=include_raw_xml)
            parsed["fts_snippet"] = row['snippet']
            results.append(parsed)

    return {
        "query": query,
        "search_type": "english_fts",
        "count": len(results),
        "results": results
    }


def autocomplete_headwords(prefix: str, limit: int = 20) -> List[Dict[str, str]]:
    """
    Fast prefix autocomplete suggestions for Sanskrit headwords.
    """
    if not prefix or len(prefix.strip()) < 1:
        return []

    slp1_prefix, script = to_slp1_key(prefix)
    ascii_prefix = normalize_ascii(prefix)

    suggestions = []
    seen = set()

    with get_db() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT DISTINCT key, key_ascii FROM mw WHERE key LIKE ? OR key_ascii LIKE ? LIMIT ?",
            (slp1_prefix + '%', ascii_prefix + '%', limit)
        )
        rows = c.fetchall()

        for row in rows:
            key_slp = row['key']
            if key_slp not in seen:
                seen.add(key_slp)
                suggestions.append({
                    "slp1": key_slp,
                    "iast": slp1_to_iast(key_slp),
                    "devanagari": slp1_to_devanagari(key_slp),
                    "ascii": row['key_ascii'] or slp1_to_ascii(key_slp)
                })

    return suggestions


def re_sub_fts(text: str) -> str:
    """Format user query string safely for SQLite FTS5 MATCH syntax."""
    words = [w for w in text.split() if w.isalnum()]
    if not words:
        return ""
    # Join terms with AND operator
    return " AND ".join(words)
