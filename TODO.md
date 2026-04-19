# sumd — TODO & Refactoring Priorities

Generated: 2026-04-19 (updated for v0.2.0-rc1)

---

## ✅ Done in v0.2.0-rc1

- `sumr` CLI command + `refactor` profile → `SUMR.md`
- Single `.venv` (removed dual-venv split)
- 88 unit tests, 37% branch+statement coverage
- `task doctor` smoke-test (5 checks)
- pyqual publish stage (twine-publish, when: metrics_pass)
- Published to PyPI: https://pypi.org/project/sumd/0.2.0rc1/

---

## P0 — 0.2.0 stable release blockers

- [ ] Raise test coverage to ≥ 50% before 0.2.0 stable
- [ ] Add `sumd/__main__.py` to support `python -m sumd` invocation
- [ ] Real testql CLI scenario file (`sumd-cli.testql.toon.yaml`) replacing smoke placeholder
- [ ] Validate rc1 on CI before promoting to 0.2.0 stable

---

## P1 — Split generator.py (architecture)

`sumd/generator.py` is 1444 lines with 0 classes. Extract into focused modules:

### 1a. `sumd/extractor.py`
Move all `extract_*` functions from `generator.py`:
- `extract_pyproject`, `extract_taskfile`, `extract_doql`, `extract_openapi`
- `extract_dockerfile`, `extract_docker_compose`, `extract_env_example`
- `extract_pyqual`, `extract_goal`, `extract_project_analysis`
- `extract_testql_scenarios`, `_analyse_py_module`

Keep `generator.py` as a re-export shim:
```python
from sumd.extractor import *  # noqa: F401,F403
```

### 1b. `sumd/renderer.py`
Move all `_render_*` functions + `generate_sumd_content`:
- `_render_architecture`, `_render_interfaces`, `_render_workflows`
- `_render_quality`, `_render_dependencies`, `_render_deployment`
- `_render_extras`, `_render_code_analysis`
- `generate_sumd_content`

### 1c. `sumd/toon_parser.py`
Move toon-specific parsing out of `generator.py`:
- `_parse_toon_file`, all `_parse_toon_block_*` helpers
- `_parse_doql_content` and its sub-functions

---

## P2 — Reduce remaining high-CC functions

Current hotspots (CC > 15):

| Function | File | CC | Action |
|---|---|---|---|
| `generate_sumd_content` | generator.py | 33 | Delegate remaining branches to renderer |
| `generate_map_toon` | generator.py | 26 | Split: `_collect_map_files()`, `_render_map_detail()` |
| `_render_interfaces` | generator.py | 25 | Split HTTP vs DOQL vs Async interface rendering |
| `_render_architecture` | generator.py | 19 | Extract `_render_arch_modules()`, `_render_arch_entry()` |
| `scan` | cli.py | 26 | Split: `_detect_projects()`, `_scan_one_project()`, `_print_scan_summary()` |
| `analyze` | cli.py | 18 | Extract `_run_code2llm()`, `_collect_analysis_files()` |
| `scaffold` | cli.py | 18 | Split: `_scaffold_testql()`, `_scaffold_doql()` |
| `validate_markdown` | parser.py | 17 | Split: `_check_required_sections()`, `_check_section_order()` |
| `_parse_doql_content` | generator.py | 13 | Split: `_parse_doql_entities()`, `_parse_doql_workflows()` |

Target: all functions CC ≤ 10.

---

## P3 — Source & test embedding in SUMD.md

SUMD.md currently covers structure, API, config, testql. Missing:

### 3a. Source module embedding
Add `## Source` section — top-N modules by CC as `markpact:file` blocks.

In `generator.py`, add `extract_source_modules(proj_dir, max_modules=5)`:
```python
# scan src/ for .py files, sort by CC desc, embed top-N
```

Control via config in `pyproject.toml` `[tool.sumd]`:
```toml
source_embed_max = 5
source_embed_threshold_cc = 10
```

### 3b. Unit test embedding
Add `## Tests` section — embed `tests/*.py` as `markpact:file` blocks.

Add `extract_tests(proj_dir)` in extractor:
```python
# scan tests/ or test_*.py, embed all test files
```

This allows LLM recovery of business logic from tests (currently unrecoverable from SUMD.md alone).

---

## P4 — testql scenarios for sumd CLI

`testql-scenarios/smoke-generic.testql.toon.yaml` is a placeholder. Replace with real CLI assertions.

### 4a. Add `sumd-cli.testql.toon.yaml`
Test actual CLI commands:
```yaml
- NAVIGATE: cd /tmp/test-sumd-project && sumd scaffold .
  ASSERT: exit_code == 0
  ASSERT: file_exists testql-scenarios/smoke-generic.testql.toon.yaml

- NAVIGATE: sumd scan . --fix
  ASSERT: exit_code == 0
  ASSERT: stdout contains "✅"

- NAVIGATE: sumd lint --workspace .
  ASSERT: exit_code == 0
```

### 4b. Add `sumd-generate.testql.toon.yaml`
Test `sumd generate` on the sumd project itself (dog-fooding):
```yaml
- NAVIGATE: sumd generate ./sumd
  ASSERT: exit_code == 0
  ASSERT: file_exists sumd/SUMD.md
  ASSERT: file_contains sumd/SUMD.md "## Architecture"
```

---

## P5 — parser.py: validate_markdown coverage

`validate_markdown` (CC=17) does NOT check:
- `## Source` section (once added in P3)
- `## Tests` section (once added in P3)
- TOC correctness (anchors match actual headings)
- `markpact:file` block paths exist on disk

Add these validators to `parser.py` after P3 is implemented.

---

## P6 — mcp_server.py review

`sumd/mcp_server.py` exists but is not covered by tests or testql scenarios. Add:
- Unit test: `tests/test_mcp_server.py`
- Verify MCP tool registration matches CLI commands

---

## Done (reference)

- ✅ `generate_sumd_content` CC 148 → ~33 (8 `_render_*` helpers)
- ✅ `_parse_toon_file` CC 41 → ~5 (6 `_parse_toon_block_*` helpers)
- ✅ `extract_doql()` — `app.doql.less` only, no CSS merge
- ✅ `extract_openapi()` — deduplicates `://` paths
- ✅ TOC auto-generated in all SUMD.md
- ✅ `_PROJECT_ANALYSIS_FILES` = `[project.toon.yaml, calls.yaml]`
- ✅ `sumd scaffold ./sumd` → `testql-scenarios/smoke-generic.testql.toon.yaml`
- ✅ All 6 projects: 0 lint errors, scan ✅
- ✅ SUMR.md header updated: "refactorization" instead of "documentation"
- ✅ SUMD.md and SUMR.md regenerated with latest project metadata
