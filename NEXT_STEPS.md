# AEUC Stack — Archived Next Steps

> Maintained by: Constitutional-Solutions/AEUC Council  
> Last updated: 2026-02-21  
> Status: `aeuc-api v0.1.0` ✅ shipped

---

## Phase 2 — Immediately Next (this sprint)

### 1. `aeuc-harmonic-engine` package
```
Constitutional-Solutions/aeuc-harmonic-engine
```
- Standalone pip-installable package extracted from `family_core_systems_v1.py`
- `HarmonicEngine` class: A432 base frequencies, just-intonation intervals, Fibonacci rhythms
- `chord_from_glyph(glyph_id)` — resolves a Glyph144k harmonic_payload into a playable chord
- `resonance_graph(glyph_ids)` — returns adjacency matrix of pairwise resonance coefficients
- FSOU: every frequency calculation is logged with input/output hash
- Exports: `harmonic_series`, `schumann_harmonics`, `phi_resonance_modes`
- Tests: interval ratio accuracy, Fibonacci convergence, Schumann mode checks

### 2. Persist `aeuc-api` state
```
glyph-registry/aeuc_registry/backends/sqlite_backend.py
```
- Add `SQLiteBackend` storage adapter behind `GlyphRegistry`
- Registry interface unchanged — swap `registry.py` singleton to use SQLite
- Migration: `alembic init` + auto-generated schema from Glyph144k dataclass
- Result: registry survives server restart

### 3. `aeuc-vector-db` → connect to `aeuc-api`
```
GET /vectors/{glyph_id}          — retrieve I/P-Glyph vectors
POST /vectors/search             — φ-weighted cosine similarity query
GET /vectors/cluster/{outer_id}  — cluster by outer context
```
- Add `/vectors` router to `aeuc-api` that proxies to `aeuc-vector-db`
- Or mount vector-db as a FastAPI sub-application

---

## Phase 3 — Next Sprint

### 4. `aeuc-geometry-engine` package
- `GeometryEngine` class from `family_core_systems_v1.py`
- Sacred polyhedra: tetrahedron, octahedron, cube, icosahedron, dodecahedron
- `phi_scaled_polyhedron(name, scale_factor)` — golden ratio scaled forms
- `fibonacci_sphere(n)` — n-point optimal sphere packing
- `glyph_to_solid(glyph_id)` — maps geometry_payload to 3D primitive
- Exports: OBJ / STL for 3D rendering pipelines

### 5. CI/CD: PyPI auto-publish
```yaml
# .github/workflows/publish.yml
on:
  push:
    tags: ['v*']
jobs:
  publish:
    uses: pypa/gh-action-pypi-publish@release/v1
```
- Add to `glyph-registry`, `aeuc-api`, `aeuc-harmonic-engine`
- `pip install glyph-registry` becomes the dependency chain anchor

### 6. `aeuc-docs` — MkDocs site
```
Constitutional-Solutions/aeuc-docs
```
- MkDocs Material theme
- Auto-generated API reference from docstrings (mkdocstrings)
- Architecture diagram: glyph-registry → aeuc-vector-db → aeuc-api → engines
- Deployed to GitHub Pages at `constitutional-solutions.github.io/aeuc-docs`

---

## Phase 4 — Horizon

| Item | Description |
|------|-------------|
| Rust bindings | `pyo3`-wrapped `glyph_registry_rs` for Landauer thermodynamic limits |
| Consciousness Engine | Port `ConsciousnessEvolutionEngine` from `family_core_systems_v1.py` |
| Co-Creation Hub | Port `CoCreationHub` multi-agent synthesis layer |
| LTO cold-storage | JSONL export → Glacier / tape archive automation |
| WebSocket stream | Real-time FSOU hash events over `ws://aeuc-api/ws/audit` |
| gRPC interface | High-throughput binary alternative to REST for engine-to-engine calls |

---

## Git Notation Reference

```
feat:     new feature
fix:      bug fix
perf:     performance improvement
refactor: code restructure, no behaviour change
docs:     documentation only
test:     tests only
chore:    build system, CI, deps
arch:     architectural decision (use for AEUC-specific structural changes)
```

## Branching Convention
```
main          — always deployable
dev           — integration branch
feat/<name>   — feature branches
fix/<name>    — hotfix branches
arch/<name>   — architectural experiments (e.g. arch/sqlite-backend)
```
