# sumd — TODO

> **Auto-derived from metrics** — CC hotspots from `ast` analysis, coverage gaps from `coverage.json`.
> Last updated: 2026-04-19 (v0.3.3)
> Manual items in **P0** and **Manual backlog** sections survive regeneration.

---

## P0 — Stable release blockers (manual, v0.2.0)

- [ ] Raise test coverage to ≥ 50% before tagging 0.2.0 stable
- [ ] Add `sumd/__main__.py` to support `python -m sumd`
- [ ] Real testql CLI scenario file (`sumd-cli.testql.toon.yaml`) instead of smoke placeholder
- [ ] Validate rc1 on CI before promoting to 0.2.0 stable

---

## CC hotspots (auto — functions with CC ≥ 10)

| CC | File | Function | Action |
|----|------|----------|--------|
| 15 | `sumd/renderer.py` | `_parse_calls_hubs` | Split hub detection from formatting |
| 14 | `sumd/renderer.py` | `_collect_pkg_sources` | Extract `_scan_sources()` helper |
| 13 | `sumd/parser.py` | `validate_codeblocks` | Split: `_check_fence_format()`, `_check_markpact_kind()` |
| 12 | `sumd/renderer.py` | `_render_test_contracts` | Split by contract type (smoke / crud / api) |
| 12 | `sumd/extractor.py` | `extract_openapi` | Extract `_parse_paths()`, `_build_endpoint()` |
| 12 | `sumd/extractor.py` | `extract_dockerfile` | Separate stage detection from content rendering |
| 10 | `sumd/renderer.py` | `_render_extras` | Extract per-format renderers |
| 10 | `sumd/renderer.py` | `_render_deployment_docker` | Split multi-compose logic |
| 10 | `sumd/extractor.py` | `generate_map_toon` | Split: `_collect_map_files()`, `_render_map_detail()` |
| 10 | `sumd/extractor.py` | `extract_taskfile` | Extract task-type classifiers |
| 10 | `sumd/extractor.py` | `_collect_map_files` | Already a sub-function — revisit call sites |
| 10 | `sumd/extractor.py` | `_analyse_py_top_classes` | Split parsing from formatting |
| 10 | `sumd/cli.py` | `_scan_one_project` | Extract profile dispatch |

Target: CC ≤ 10 for all functions. Current average (production code): ~4.6.

---

## Coverage gaps (auto — modules < 60% covered)

| Coverage | Missing lines | Module |
|----------|--------------|--------|
| 0% | 103 | `sumd/mcp_server.py` |
| 0% | 486 | `sumd/cli.py` |
| 14% | 91 | `sumd/toon_parser.py` |
| 36% | 303 | `sumd/extractor.py` |
| 36% | 417 | `sumd/renderer.py` |

### Action plan

- **`cli.py` (0%)** — add `tests/test_dogfood.py` integration tests (see P1) + CLI unit tests via `click.testing.CliRunner`
- **`mcp_server.py` (0%)** — add `tests/test_mcp_server.py`; at minimum test tool registration and that `main()` doesn't crash
- **`toon_parser.py` (14%)** — add `tests/test_toon_parser.py` covering each `_parse_toon_block_*` function
- **`extractor.py` (36%)** — extend `test_extractor.py` with edge-case fixtures (missing files, empty files, malformed YAML)
- **`renderer.py` (36%)** — add `tests/test_renderer.py` parametrised over section fixtures

---

## P1 — Integration / dogfood tests (high ROI)

Add `tests/test_dogfood.py` — tests that scan the sumd project itself:

```python
def test_sumd_scans_itself():
    # sumd scan . --fix --profile rich must exit 0 and produce valid SUMD.md
    ...

def test_sumd_scans_all_profiles():
    for profile in ['minimal', 'light', 'rich']:
        # each profile must exit 0
        ...

def test_sumr_generates_sumr_md():
    # sumr . must produce SUMR.md with expected sections
    ...
```

These catch full-pipeline regressions not visible via unit tests.

---

## P2 — mcp_server.py tests

`sumd/mcp_server.py` — 103 lines, 0% coverage, no tests anywhere.

```python
# tests/test_mcp_server.py
def test_mcp_tools_registered():
    ...

def test_mcp_main_no_crash():
    ...
```

---

## P3 — Autonomization backlog (manual)

These items improve autonomy of the dev process; not blocking release.

- **Coverage ratchet**: `sumd scan . --update-gates` — only raises `coverage_min`, never lowers it
- **Pre-commit hook**: `task install:hooks` → `.git/hooks/pre-commit` runs `sumd scan . --fix --profile light` on every commit touching `.py` files
- **TODO auto-regeneration**: `sumd scan . --todo` generates this file from live metrics (CC + coverage + duplication)

---

## ✅ Done (reference)

- ✅ `generate_sumd_content` refactored: CC 33 → 1, fan-out 34 → 2 via `RenderPipeline`
- ✅ `generator.py` → 18-line shim re-exporting `extractor.py` and `renderer.py`
- ✅ `sumd/extractor.py`, `sumd/renderer.py`, `sumd/toon_parser.py` extracted
- ✅ `sumd/sections/` package: 15 section classes across 3 profile tiers
- ✅ `SourceSnippetsSection`, `ApiStubsSection`, `TestContractsSection`, `CallGraphSection`, `EnvironmentSection` added
- ✅ `refactor` profile → `SUMR.md` (AI-aware refactorization report)
- ✅ `sumr` CLI command
- ✅ `task doctor` smoke-test (5 checks)
- ✅ pyqual publish stage (twine-publish, when: metrics_pass)
- ✅ Single `.venv` — dual-venv split eliminated
- ✅ 88 unit tests, 37% branch+statement coverage
- ✅ Published to PyPI: https://pypi.org/project/sumd/0.2.0rc1/
- ✅ SUMR `refactor` profile expanded to 9 sections (v0.3.3)
- ✅ `sumd/sections/__init__.py` section registry
- ✅ README AI cost tracking removed; version badge updated to 0.3.3
