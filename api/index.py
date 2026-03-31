# Vercel serverless entry point for the FastAPI backend.
# Vercel zero-config auto-detects this file as a Python serverless function.
# The rewrite in vercel.json routes /api/:path* here, so Vercel passes the
# full path e.g. /api/health to the ASGI handler. We mount _api_app at /api
# so the root app strips the prefix and the sub-app sees /health, /kpis etc.

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI  # noqa: E402
from fastapi_app import app as _api_app  # noqa: E402

# Wrapper mounts _api_app at /api so route matching works when Vercel
# passes the full request path (e.g. /api/health) to the ASGI handler.
app = FastAPI()
app.mount("/api", _api_app)

__all__ = ["app"]
