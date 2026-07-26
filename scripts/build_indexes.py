#!/usr/bin/env python3
"""
Sanskrit Abhidhana - Database Indexing & Optimization Script
Populates key_ascii normalized column, creates indices, FTS5 virtual table, and enables WAL mode.
"""

import sqlite3
import os
import sys
import re
import time

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mw', 'mw.sqlite')

SLP1_TO_ASCII_MAP = {
    'a': 'a', 'A': 'a', 'i': 'i', 'I': 'i', 'u': 'u', 'U': 'u',
    'f': 'ri', 'F': 'ri', 'x': 'l', 'X': 'l', 'e': 'e', 'o': 'o',
    'M': 'm', 'H': 'h', '\'': '',
    'k': 'k', 'K': 'kh', 'g': 'g', 'G': 'gh', 'N': 'n',
    'c': 'ch', 'C': 'chh', 'j': 'j', 'J': 'jh', 'Y': 'n',
    'w': 't', 'W': 'th', 'q': 'd', 'Q': 'dh', 'R': 'n',
    't': 't', 'T': 'th', 'd': 'd', 'D': 'dh', 'n': 'n',
    'p': 'p', 'P': 'ph', 'b': 'b', 'B': 'bh', 'm': 'm',
    'y': 'y', 'r': 'r', 'l': 'l', 'v': 'v',
    'S': 'sh', 'z': 'sh', 's': 's', 'h': 'h'
}

def slp1_to_ascii(slp: str) -> str:
    """Convert SLP1 key to loose English ASCII string (e.g., kfzRa -> krishna, Darma -> dharma)."""
    res = []
    i = 0
    n = len(slp)
    while i < n:
        if i + 1 < n and slp[i:i+2] in ('ai', 'au'):
            res.append(slp[i:i+2])
            i += 2
            continue
        res.append(SLP1_TO_ASCII_MAP.get(slp[i], slp[i].lower()))
        i += 1
    return ''.join(res)

def clean_xml_text(raw_xml: str) -> str:
    """Clean Monier-Williams XML tags into plain text for full-text search."""
    cleaned = re.sub(r'<[^>]+>', ' ', raw_xml)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def build_indexes():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Enforce WAL Mode
    c.execute("PRAGMA journal_mode=WAL;")
    wal_mode = c.fetchone()[0]
    print(f"Journal mode set to: {wal_mode}")

    # 2. Add key_ascii column if not existing
    c.execute("PRAGMA table_info(mw);")
    cols = [row[1] for row in c.fetchall()]
    if 'key_ascii' not in cols:
        print("Adding column 'key_ascii' to table 'mw'...")
        c.execute("ALTER TABLE mw ADD COLUMN key_ascii VARCHAR(100);")
        conn.commit()

    # 3. Populate key_ascii
    print("Populating key_ascii column...")
    start_time = time.time()
    c.execute("SELECT rowid, key FROM mw WHERE key_ascii IS NULL;")
    rows = c.fetchall()
    if rows:
        updates = [(slp1_to_ascii(key), rowid) for rowid, key in rows]
        c.executemany("UPDATE mw SET key_ascii = ? WHERE rowid = ?;", updates)
        conn.commit()
        print(f"Updated {len(updates)} key_ascii entries in {time.time() - start_time:.2f}s")
    else:
        print("key_ascii column already fully populated.")

    # 4. Create SQL Indexes
    print("Creating indices on 'mw' table...")
    c.execute("CREATE INDEX IF NOT EXISTS idx_mw_key ON mw(key);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_mw_key_ascii ON mw(key_ascii);")
    c.execute("CREATE INDEX IF NOT EXISTS idx_mw_lnum ON mw(lnum);")
    conn.commit()

    # 5. Create FTS5 Table for English Full-Text Search
    print("Setting up FTS5 full-text search table 'mw_fts'...")
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mw_fts';")
    if not c.fetchone():
        c.execute("CREATE VIRTUAL TABLE mw_fts USING fts5(key UNINDEXED, lnum UNINDEXED, clean_text);")
        print("Populating FTS5 index from 'mw' table...")
        c.execute("SELECT key, lnum, data FROM mw;")
        all_entries = c.fetchall()
        fts_rows = [(key, str(lnum), clean_xml_text(data)) for key, lnum, data in all_entries]
        c.executemany("INSERT INTO mw_fts(key, lnum, clean_text) VALUES (?, ?, ?);", fts_rows)
        conn.commit()
        print(f"Inserted {len(fts_rows)} rows into FTS5 index.")
    else:
        print("FTS5 table 'mw_fts' already exists.")

    print("Optimizing database storage...")
    c.execute("PRAGMA optimize;")
    conn.commit()
    conn.close()
    print("Database build and optimization complete!")

if __name__ == '__main__':
    build_indexes()
