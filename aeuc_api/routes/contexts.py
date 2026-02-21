"""
/contexts router — Outer context management (base-1.44M outer digit).
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Path

from ..registry import OuterContext, registry
from ..models import ContextCreateRequest, ContextResponse

router = APIRouter()


def _to_response(c: OuterContext) -> ContextResponse:
    return ContextResponse(
        outer_id=c.outer_id,
        code=c.code,
        description=c.description,
        layer_info=c.layer_info or {},
        version=c.version,
        timestamp=c.timestamp,
    )


@router.get("", response_model=List[ContextResponse], summary="List all outer contexts")
async def list_contexts():
    return [_to_response(c) for c in registry.all_contexts()]


@router.post("", response_model=ContextResponse, status_code=201, summary="Add outer context")
async def add_context(body: ContextCreateRequest):
    try:
        ctx = OuterContext(
            outer_id=body.outer_id,
            code=body.code,
            description=body.description,
            layer_info=body.layer_info,
        )
        registry.add_context(ctx)
        return _to_response(ctx)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/{outer_id}", response_model=ContextResponse, summary="Get outer context")
async def get_context(
    outer_id: int = Path(..., ge=0, le=9)
):
    c = registry.get_context(outer_id)
    if c is None:
        raise HTTPException(status_code=404, detail=f"Context outer_id {outer_id} not found")
    return _to_response(c)
