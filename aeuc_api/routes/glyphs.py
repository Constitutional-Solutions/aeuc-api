"""
/glyphs router — full CRUD for Glyph144k records.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, Path, Query

from ..registry import GlyphCategory, Glyph144k, GlyphPayload, registry
from ..models import (
    GlyphCreateRequest,
    GlyphUpdateRequest,
    GlyphResponse,
)

router = APIRouter()


def _to_response(g: Glyph144k) -> GlyphResponse:
    return GlyphResponse(
        id=g.id,
        code=g.code,
        category=g.category.value,
        description=g.description,
        geometry_payload=g.geometry_payload.to_dict() if g.geometry_payload else None,
        harmonic_payload=g.harmonic_payload.to_dict() if g.harmonic_payload else None,
        protocol_payload=g.protocol_payload.to_dict() if g.protocol_payload else None,
        version=g.version,
        timestamp=g.timestamp,
    )


@router.get("", response_model=List[GlyphResponse], summary="List all glyphs")
async def list_glyphs(
    category: str = Query(None, description="Filter by category name")
):
    if category:
        try:
            cat = GlyphCategory(category.upper())
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Unknown category: {category}")
        glyphs = registry.search_by_category(cat)
    else:
        glyphs = registry.all_glyphs()
    return [_to_response(g) for g in glyphs]


@router.post("", response_model=GlyphResponse, status_code=201, summary="Add a glyph")
async def add_glyph(body: GlyphCreateRequest):
    try:
        glyph = Glyph144k(
            id=body.id,
            code=body.code,
            category=GlyphCategory(body.category),
            description=body.description,
            geometry_payload=GlyphPayload(**body.geometry_payload.model_dump())
                if body.geometry_payload else None,
            harmonic_payload=GlyphPayload(**body.harmonic_payload.model_dump())
                if body.harmonic_payload else None,
            protocol_payload=GlyphPayload(**body.protocol_payload.model_dump())
                if body.protocol_payload else None,
        )
        registry.add_glyph(glyph)
        return _to_response(glyph)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/code/{code}", response_model=GlyphResponse, summary="Get glyph by short code")
async def get_by_code(code: str = Path(...)):
    g = registry.get_glyph_by_code(code)
    if g is None:
        raise HTTPException(status_code=404, detail=f"Glyph code '{code}' not found")
    return _to_response(g)


@router.get("/{glyph_id}", response_model=GlyphResponse, summary="Get glyph by numeric ID")
async def get_glyph(
    glyph_id: int = Path(..., ge=0, le=143_999)
):
    g = registry.get_glyph(glyph_id)
    if g is None:
        raise HTTPException(status_code=404, detail=f"Glyph ID {glyph_id} not found")
    return _to_response(g)


@router.patch("/{glyph_id}", response_model=GlyphResponse, summary="Update glyph description")
async def update_glyph(
    glyph_id: int = Path(..., ge=0, le=143_999),
    body: GlyphUpdateRequest = ...,
):
    try:
        g = registry.update_glyph(glyph_id, body.description)
        return _to_response(g)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{glyph_id}", status_code=204, summary="Delete a glyph")
async def delete_glyph(
    glyph_id: int = Path(..., ge=0, le=143_999)
):
    try:
        registry.delete_glyph(glyph_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
