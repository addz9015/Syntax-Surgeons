# This file is the Vercel serverless entry point for the FastAPI backend.
# Vercel looks for an ASGI-compatible callable named `app` in api/index.py.
# All actual route logic lives in ../fastapi_app.py via sys.path injection.

from __future__ import annotations

import sys
from pathlib import Path

# Make the project root importable so fastapi_app and vitaledge_core resolve.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Re-export the FastAPI app as the Vercel handler entry point.
from fastapi_app import app  # noqa: E402  # re-exported as the ASGI handler

__all__ = ["app"]
