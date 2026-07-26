#!/usr/bin/env python3
"""
Sanskrit Abhidhana REST API - Server Launcher
Starts Uvicorn ASGI web server.
"""

import sys
import os
import site

# Include user site packages in sys.path
user_site = site.getusersitepackages()
if user_site and os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Ensure root directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import uvicorn

if __name__ == '__main__':
    host = "127.0.0.1"
    port = 8000
    print(f"Starting Sanskrit Abhidhana REST API server on http://{host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=False, log_level="info")
