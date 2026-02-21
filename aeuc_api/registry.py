"""
Singleton GlyphRegistry instance shared across the FastAPI application.

Because aeuc-api is stateless between restarts (the registry lives in RAM
for now), this module owns the single authoritative in-process instance.
Phase 3 will swap this for a persistent backend (SQLite / Postgres).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict


# ---------------------------------------------------------------------------
# Minimal self-contained registry (no external dep on glyph-registry package
# yet — keeps the API bootstrappable without a published PyPI release).
# Once glyph-registry 0.1.0 ships to PyPI this module will become a thin
# import shim:  from glyph_registry import GlyphRegistry, Glyph144k, ...
# ---------------------------------------------------------------------------

class GlyphCategory(str, Enum):
    GEOMETRY    = "GEOMETRY"
    HARMONIC    = "HARMONIC"
    PROTOSTATE  = "PROTOSTATE"
    STORYEVENT  = "STORYEVENT"
    SPECIAL     = "SPECIAL"


@dataclass
class GlyphPayload:
    type: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {"type": self.type, "data": self.data}


@dataclass
class Glyph144k:
    id: int
    code: str
    category: GlyphCategory
    description: str
    geometry_payload:  Optional[GlyphPayload] = None
    harmonic_payload:  Optional[GlyphPayload] = None
    protocol_payload:  Optional[GlyphPayload] = None
    version: str = "1.0.0"
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not (0 <= self.id <= 143_999):
            raise ValueError(f"Glyph ID {self.id} out of range [0, 143999]")

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["category"] = self.category.value
        return d


@dataclass
class OuterContext:
    outer_id: int
    code: str
    description: str
    layer_info: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not (0 <= self.outer_id <= 9):
            raise ValueError(f"Outer ID {self.outer_id} out of range [0, 9]")

    def to_dict(self) -> Dict:
        return asdict(self)


class GlyphRegistry:
    """In-process FSOU-audited glyph store."""

    def __init__(self):
        self.glyphs_144k:    Dict[int, Glyph144k]       = {}
        self.outer_contexts: Dict[int, OuterContext]    = {}
        self.code_to_id:     Dict[str, int]             = {}
        self.category_index: Dict[GlyphCategory, List[int]] = {
            cat: [] for cat in GlyphCategory
        }
        self.registry_version = "1.0.0"
        self.change_history:  List[Dict]                = []
        self.current_hash:    str                       = ""
        self._initialize_default_contexts()
        self._update_hash()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _initialize_default_contexts(self):
        defaults = [
            (0, "CTX_BASE",       "Default base context"),
            (1, "CTX_GEOMETRY",   "Geometry-dominant context"),
            (2, "CTX_RESEARCH",   "Research / experimental context"),
            (3, "CTX_HARMONIC",   "Harmonics-dominant context"),
            (4, "CTX_PROTOCOL",   "Protocol state context"),
            (5, "CTX_STORY",      "Narrative / story context"),
            (6, "CTX_EVOLUTION",  "Consciousness evolution context"),
            (7, "CTX_SYNTHESIS",  "Co-creation synthesis context"),
            (8, "CTX_ARCHIVE",    "Long-term archive / cold-storage context"),
            (9, "CTX_SOVEREIGN",  "Sovereign override context"),
        ]
        for oid, code, desc in defaults:
            self.outer_contexts[oid] = OuterContext(outer_id=oid, code=code, description=desc)

    def _update_hash(self):
        content = json.dumps(
            {
                "glyphs":   {str(k): v.to_dict() for k, v in self.glyphs_144k.items()},
                "contexts": {str(k): v.to_dict() for k, v in self.outer_contexts.items()},
            },
            sort_keys=True,
        )
        self.current_hash = hashlib.blake2b(content.encode(), digest_size=32).hexdigest()

    def _audit(self, action: str, **kwargs):
        old = self.current_hash
        self._update_hash()
        self.change_history.append({
            "action":      action,
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "hash_before": old,
            "hash_after":  self.current_hash,
            **kwargs,
        })

    # ------------------------------------------------------------------
    # CRUD — Glyphs
    # ------------------------------------------------------------------

    def add_glyph(self, glyph: Glyph144k) -> int:
        if glyph.id in self.glyphs_144k:
            raise ValueError(f"Glyph ID {glyph.id} already exists")
        if glyph.code in self.code_to_id:
            raise ValueError(f"Glyph code '{glyph.code}' already exists")
        self.glyphs_144k[glyph.id] = glyph
        self.code_to_id[glyph.code] = glyph.id
        self.category_index[glyph.category].append(glyph.id)
        self._audit("ADD_GLYPH", glyph_id=glyph.id, code=glyph.code)
        return glyph.id

    def update_glyph(self, glyph_id: int, description: str) -> Glyph144k:
        if glyph_id not in self.glyphs_144k:
            raise KeyError(f"Glyph ID {glyph_id} not found")
        self.glyphs_144k[glyph_id].description = description
        self._audit("UPDATE_GLYPH", glyph_id=glyph_id)
        return self.glyphs_144k[glyph_id]

    def delete_glyph(self, glyph_id: int) -> bool:
        if glyph_id not in self.glyphs_144k:
            raise KeyError(f"Glyph ID {glyph_id} not found")
        g = self.glyphs_144k.pop(glyph_id)
        self.code_to_id.pop(g.code, None)
        self.category_index[g.category].remove(glyph_id)
        self._audit("DELETE_GLYPH", glyph_id=glyph_id, code=g.code)
        return True

    def get_glyph(self, glyph_id: int) -> Optional[Glyph144k]:
        return self.glyphs_144k.get(glyph_id)

    def get_glyph_by_code(self, code: str) -> Optional[Glyph144k]:
        gid = self.code_to_id.get(code)
        return self.glyphs_144k.get(gid) if gid is not None else None

    def search_by_category(self, category: GlyphCategory) -> List[Glyph144k]:
        return [self.glyphs_144k[gid] for gid in self.category_index.get(category, [])]

    def all_glyphs(self) -> List[Glyph144k]:
        return sorted(self.glyphs_144k.values(), key=lambda g: g.id)

    # ------------------------------------------------------------------
    # CRUD — Outer Contexts
    # ------------------------------------------------------------------

    def add_context(self, ctx: OuterContext) -> int:
        if ctx.outer_id in self.outer_contexts:
            raise ValueError(f"Context outer_id {ctx.outer_id} already exists")
        self.outer_contexts[ctx.outer_id] = ctx
        self._audit("ADD_CONTEXT", outer_id=ctx.outer_id, code=ctx.code)
        return ctx.outer_id

    def get_context(self, outer_id: int) -> Optional[OuterContext]:
        return self.outer_contexts.get(outer_id)

    def all_contexts(self) -> List[OuterContext]:
        return sorted(self.outer_contexts.values(), key=lambda c: c.outer_id)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict:
        return {
            "total_glyphs":    len(self.glyphs_144k),
            "total_contexts":  len(self.outer_contexts),
            "change_entries":  len(self.change_history),
            "registry_version": self.registry_version,
            "current_hash":    self.current_hash,
        }


# ---------------------------------------------------------------------------
# Module-level singleton — imported by all routers
# ---------------------------------------------------------------------------
registry: GlyphRegistry = GlyphRegistry()
