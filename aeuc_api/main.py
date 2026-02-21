"""
aeuc-api — FastAPI application entry point.

Run with:
    uvicorn aeuc_api.main:app --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .registry import registry
from .models import HealthResponse
from .routes.glyphs import router as glyphs_router
from .routes.contexts import router as contexts_router
from .routes.audit import router as audit_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Startup: registry is already initialised at import time (singleton)
    yield
    # Shutdown: nothing to tear down for the in-memory store


app = FastAPI(
    title="AEUC API",
    description=(
        "FSOU-compliant REST interface for the AEUC glyph-registry.\n\n"
        "Part of the [Constitutional-Solutions AEUC open-source stack]("
        "https://github.com/Constitutional-Solutions)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(glyphs_router,   prefix="/glyphs",   tags=["Glyphs"])
app.include_router(contexts_router, prefix="/contexts", tags=["Contexts"])
app.include_router(audit_router,    prefix="/audit",    tags=["Audit"])


# ---------------------------------------------------------------------------
# Root / health
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "AEUC API — see /docs for Swagger UI"}


@app.get("/health", response_model=HealthResponse, summary="Registry health + hash")
async def health() -> HealthResponse:
    """Returns the current Blake2b-256 registry hash and live statistics.
    This hash changes on every ADD / UPDATE / DELETE, providing a
    tamper-evident fingerprint of the entire glyph store.
    """
    s = registry.stats()
    return HealthResponse(
        status="ok",
        registry_version=s["registry_version"],
        total_glyphs=s["total_glyphs"],
        total_contexts=s["total_contexts"],
        change_entries=s["change_entries"],
        current_hash=s["current_hash"],
    )
