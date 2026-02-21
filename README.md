# aeuc-api

> FSOU-compliant FastAPI REST interface for the AEUC glyph-registry.

Part of the **Constitutional-Solutions / AEUC open-source stack**:

| Layer | Repo |
|-------|------|
| 0 — Glyph substrate | [`glyph-registry`](https://github.com/Constitutional-Solutions/glyph-registry) |
| 1 — Vector field | [`aeuc-vector-db`](https://github.com/Constitutional-Solutions/aeuc-vector-db) |
| 2 — REST API ← **you are here** | `aeuc-api` |
| 3 — Harmonic engine | `aeuc-harmonic-engine` *(coming)* |

## Quick Start

```bash
pip install -e .
uvicorn aeuc_api.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Registry hash + stats |
| GET | `/glyphs` | List all glyphs |
| POST | `/glyphs` | Add a glyph |
| GET | `/glyphs/{glyph_id}` | Get by numeric ID |
| GET | `/glyphs/code/{code}` | Get by short code |
| PATCH | `/glyphs/{glyph_id}` | Update description |
| DELETE | `/glyphs/{glyph_id}` | Delete glyph |
| GET | `/glyphs/category/{category}` | Filter by category |
| GET | `/contexts` | List outer contexts |
| GET | `/contexts/{outer_id}` | Get single context |
| POST | `/contexts` | Add outer context |
| GET | `/audit` | Full change history |

## Architecture

```
aeuc_api/
├── main.py          # FastAPI app + lifespan
├── models.py        # Pydantic v2 request/response models
├── registry.py      # Singleton GlyphRegistry instance
└── routes/
    ├── glyphs.py    # /glyphs router
    ├── contexts.py  # /contexts router
    └── audit.py     # /audit router
```

## FSOU Compliance

Every mutation (`ADD`, `UPDATE`, `DELETE`) appends a `{hash_before, hash_after, timestamp}` entry to the
registry's `change_history`. The current registry hash is always available at `GET /health`.

## License

MIT — part of the AEUC sovereign AI substrate.
