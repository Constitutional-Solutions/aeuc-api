"""
/audit router — FSOU change-history log.
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from ..registry import registry
from ..models import AuditEntry, AuditResponse

router = APIRouter()


@router.get("", response_model=AuditResponse, summary="Full FSOU change history")
async def get_audit(
    limit: int = Query(100, ge=1, le=1000, description="Max entries to return"),
    action: str = Query(None, description="Filter by action type e.g. ADD_GLYPH"),
):
    entries = registry.change_history
    if action:
        entries = [e for e in entries if e.get("action") == action.upper()]
    # newest first
    entries = list(reversed(entries))[:limit]
    return AuditResponse(
        entries=[
            AuditEntry(
                action=e["action"],
                timestamp=e["timestamp"],
                hash_before=e["hash_before"],
                hash_after=e["hash_after"],
                detail={k: v for k, v in e.items()
                        if k not in {"action", "timestamp", "hash_before", "hash_after"}},
            )
            for e in entries
        ],
        total=len(registry.change_history),
    )
