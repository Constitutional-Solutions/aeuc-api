"""
Pydantic v2 request / response models for aeuc-api.

Separating models from the internal dataclasses keeps the HTTP boundary
explicit and allows the internal registry types to evolve independently.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Glyph models
# ---------------------------------------------------------------------------

class GlyphPayloadModel(BaseModel):
    type: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class GlyphCreateRequest(BaseModel):
    id: int = Field(..., ge=0, le=143_999, description="Base-144k digit value")
    code: str = Field(..., min_length=1, max_length=64)
    category: str = Field(..., description="GEOMETRY | HARMONIC | PROTOSTATE | STORYEVENT | SPECIAL")
    description: str
    geometry_payload:  Optional[GlyphPayloadModel] = None
    harmonic_payload:  Optional[GlyphPayloadModel] = None
    protocol_payload:  Optional[GlyphPayloadModel] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {"GEOMETRY", "HARMONIC", "PROTOSTATE", "STORYEVENT", "SPECIAL"}
        if v.upper() not in valid:
            raise ValueError(f"category must be one of {valid}")
        return v.upper()


class GlyphUpdateRequest(BaseModel):
    description: str


class GlyphResponse(BaseModel):
    id: int
    code: str
    category: str
    description: str
    geometry_payload:  Optional[GlyphPayloadModel] = None
    harmonic_payload:  Optional[GlyphPayloadModel] = None
    protocol_payload:  Optional[GlyphPayloadModel] = None
    version: str
    timestamp: str


# ---------------------------------------------------------------------------
# Outer context models
# ---------------------------------------------------------------------------

class ContextCreateRequest(BaseModel):
    outer_id: int = Field(..., ge=0, le=9, description="Outer digit [0-9]")
    code: str = Field(..., min_length=1, max_length=32)
    description: str
    layer_info: Dict[str, Any] = Field(default_factory=dict)


class ContextResponse(BaseModel):
    outer_id: int
    code: str
    description: str
    layer_info: Dict[str, Any]
    version: str
    timestamp: str


# ---------------------------------------------------------------------------
# Health / audit
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str = "ok"
    registry_version: str
    total_glyphs: int
    total_contexts: int
    change_entries: int
    current_hash: str


class AuditEntry(BaseModel):
    action: str
    timestamp: str
    hash_before: str
    hash_after: str
    detail: Dict[str, Any] = Field(default_factory=dict)


class AuditResponse(BaseModel):
    entries: List[AuditEntry]
    total: int
