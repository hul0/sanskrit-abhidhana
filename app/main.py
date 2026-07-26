"""
Sanskrit Abhidhana - High-Throughput REST API System
Built with FastAPI, featuring sub-5ms Sanskrit dictionary search, multi-script transliteration,
English full-text search, web interface at /, and real-time performance & RAM tracking.
"""

import time
import sys
import os
import site
import psutil
from typing import Optional, List, Dict, Any

# Ensure user site packages in sys.path
user_site = site.getusersitepackages()
if user_site and os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

from fastapi import FastAPI, Query, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import search_by_headword, search_english_fts, autocomplete_headwords
from app.transliterate import convert_script, detect_script, to_slp1_key, slp1_to_iast, slp1_to_devanagari, slp1_to_ascii

app = FastAPI(
    title="Sanskrit Abhidhana REST API",
    description=(
        "High-performance, low-memory (<300MB RAM) Sanskrit Lexicon & Dictionary REST API. "
        "Created by Rupam Ghosh (hul0). Database attribution: Cologne Sanskrit Lexicon (csl-sqlite)."
    ),
    version="1.0.0",
    contact={
        "name": "Rupam Ghosh",
        "url": "https://github.com/hul0",
        "email": "hulo@crine.in",
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory if existing
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Global metrics tracking
REQUEST_COUNT = 0
TOTAL_LATENCY_MS = 0.0


@app.middleware("http")
async def add_performance_metrics(request: Request, call_next):
    global REQUEST_COUNT, TOTAL_LATENCY_MS
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000.0

    REQUEST_COUNT += 1
    TOTAL_LATENCY_MS += duration_ms

    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    return response


@app.get("/")
async def root():
    """Serve the single-page web UI at root URI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "system": "Sanskrit Abhidhana REST API",
        "author": "Rupam Ghosh (hul0 <hulo@crine.in>)",
        "attribution": "Cologne Sanskrit Lexicon (csl-sqlite: https://github.com/sanskrit-lexicon/csl-sqlite)",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "define": "/api/v1/define/{word}",
            "search": "/api/v1/search?q=...",
            "transliterate": "/api/v1/transliterate?text=...",
            "autocomplete": "/api/v1/autocomplete?prefix=...",
            "health": "/health",
            "metrics": "/metrics"
        }
    }


@app.get("/api/v1/define/{word}")
async def define_word(
    word: str,
    script: Optional[str] = Query('auto', description="Script scheme: auto, devanagari, iast, slp1, hk, itrans, ascii"),
    limit: int = Query(50, ge=1, le=200),
    raw_xml: bool = Query(False, description="Include raw Monier-Williams XML entry")
):
    """
    Search Sanskrit headword definitions by Devanagari, IAST, SLP1, HK, ITRANS, or loose ASCII.
    """
    if not word or not word.strip():
        raise HTTPException(status_code=400, detail="Word parameter cannot be empty.")

    res = search_by_headword(word.strip(), script=script, limit=limit, include_raw_xml=raw_xml)
    return res


@app.get("/api/v1/search")
async def search_dictionary(
    q: str = Query(..., description="Query term to search"),
    type: str = Query('headword', description="Search mode: headword, english, autocomplete"),
    script: Optional[str] = Query('auto'),
    limit: int = Query(50, ge=1, le=200),
    raw_xml: bool = Query(False)
):
    """
    Flexible search endpoint for headwords, English definitions, or autocompletion.
    """
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query string 'q' is required.")

    q = q.strip()
    if type == 'english':
        return search_english_fts(q, limit=limit, include_raw_xml=raw_xml)
    elif type == 'autocomplete':
        suggestions = autocomplete_headwords(q, limit=limit)
        return {"query": q, "count": len(suggestions), "suggestions": suggestions}
    else:
        return search_by_headword(q, script=script, limit=limit, include_raw_xml=raw_xml)


@app.get("/api/v1/transliterate")
async def transliterate_text(
    text: str = Query(..., description="Sanskrit text to transliterate"),
    from_scheme: str = Query('auto', description="Source scheme: auto, devanagari, iast, slp1, hk, itrans"),
    to_scheme: str = Query('iast', description="Target scheme: devanagari, iast, slp1, ascii")
):
    """
    Transliterate text across Sanskrit schemes (Devanagari ↔ IAST ↔ SLP1 ↔ HK ↔ Loose ASCII).
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text parameter cannot be empty.")

    text = text.strip()
    if from_scheme == 'auto':
        from_scheme = detect_script(text)

    slp1_key, _ = to_slp1_key(text, script=from_scheme)

    if to_scheme == 'devanagari':
        converted = slp1_to_devanagari(slp1_key)
    elif to_scheme == 'iast':
        converted = slp1_to_iast(slp1_key)
    elif to_scheme == 'ascii':
        converted = slp1_to_ascii(slp1_key)
    elif to_scheme == 'slp1':
        converted = slp1_key
    else:
        converted = convert_script(text, from_scheme, to_scheme)

    return {
        "original_text": text,
        "from_scheme": from_scheme,
        "to_scheme": to_scheme,
        "transliterated_text": converted
    }


@app.get("/api/v1/autocomplete")
async def autocomplete(prefix: str = Query(..., description="Prefix string"), limit: int = Query(20, ge=1, le=50)):
    """
    Fast prefix autocomplete endpoint.
    """
    suggestions = autocomplete_headwords(prefix, limit=limit)
    return {"prefix": prefix, "count": len(suggestions), "suggestions": suggestions}


@app.get("/health")
async def health_check():
    """
    Health check endpoint verifying database connectivity.
    """
    try:
        from app.database import get_db
        with get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT 1;")
            c.fetchone()
        db_healthy = True
    except Exception as e:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "error",
        "timestamp": time.time()
    }


@app.get("/metrics")
async def get_metrics():
    """
    System metrics endpoint reporting RAM usage (MB), request throughput, and latency.
    """
    process = psutil.Process(os.getpid())
    ram_mb = process.memory_info().rss / (1024 * 1024)

    avg_latency = 0.0
    if REQUEST_COUNT > 0:
        # pyrefly: ignore [division-by-zero]
        avg_latency = TOTAL_LATENCY_MS / REQUEST_COUNT

    return {
        "memory_rss_mb": round(ram_mb, 2),
        "memory_limit_mb": 300.0,
        "memory_status": "optimal (<300MB target)" if ram_mb < 300.0 else "warning",
        "total_requests": REQUEST_COUNT,
        "average_latency_ms": round(avg_latency, 2)
    }
