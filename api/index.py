# This file is the Vercel serverless entry point for the FastAPI backend.
# Vercel looks for an ASGI-compatible callable named `app` in api/index.py.
# All actual route logic lives in ../fastapi_app.py via sys.path injection.
# The API is mounted under /api so it can coexist with the React frontend
# on the same Vercel domain.

from __future__ import annotations

import sys
from pathlib import Path

# Make the project root importable so fastapi_app and vitaledge_core resolve.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi_app import app as _api_app  # noqa: E402

# Wrap in a root app that mounts the API under /api so Vercel routes
# /api/* here and the React SPA handles everything else.
app = FastAPI()
app.mount("/api", _api_app)

__all__ = ["app"]
