# SUMD

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Quality Pipeline (`pyqual.yaml`)](#quality-pipeline-pyqualyaml)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `sumd`
- **version**: `0.3.37`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, testql(3), app.doql.less, pyqual.yaml, goal.yaml, .env.example, src(10 mod), project/(6 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: sumd;
  version: 0.3.37;
}

dependencies {
  runtime: "click>=8.3.3, pyyaml>=6.0.3, toml>=0.10.2, goal>=2.1.190, costs>=0.1.50, pfix>=0.1.72";
  dev: "pytest>=9.0.3, pytest-cov>=7.1.0, ruff>=0.15.11, build>=1.4.4, twine>=6.2.0, pyqual>=0.1.143, goal>=2.1.190, costs>=0.1.50, pfix>=0.1.72, mcp>=1.27.0";
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="sumd"] {

}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PIP}} install -e .[dev];
}

workflow[name="deps:update"] {
  trigger: manual;
  step-1: run cmd=PIP="{{.VENV_PIP}}"
$PIP install --upgrade pip
OUTDATED=$($PIP list --outdated --format=columns 2>/dev/null | tail -n +3 | awk '{print $1}')
if [ -z "$OUTDATED" ]; then
  echo "✅ All packages are up to date."
else
  echo "📦 Upgrading: $OUTDATED"
  echo "$OUTDATED" | xargs $PIP install --upgrade
  echo "✅ Done."
fi;
}

workflow[name="quality"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pyqual run;
}

workflow[name="quality:fix"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pyqual run --fix;
}

workflow[name="quality:report"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pyqual report;
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pytest -q;
}

workflow[name="test:report"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m pytest --json-report --json-report-file=test-results.json -q;
  step-2: run cmd={{.VENV_PY}} -m testql report test-results.json -o report.html;
}

workflow[name="test:report:example"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m testql report --example -o report.html;
}

workflow[name="lint"] {
  trigger: manual;
  step-1: run cmd=ruff check .;
}

workflow[name="fmt"] {
  trigger: manual;
  step-1: run cmd=ruff format .;
}

workflow[name="build"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m build;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=rm -rf build/ dist/ *.egg-info;
}

workflow[name="structure"] {
  trigger: manual;
  step-1: run cmd=echo "📁 Analyzing sumd project structure..."
{{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force
echo "✅ Structure generated: {{.DOQL_OUTPUT}}";
}

workflow[name="doql:adopt"] {
  trigger: manual;
  step-1: run cmd={{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force;
  step-2: run cmd=echo "✅ Captured in app.doql.less";
}

workflow[name="doql:export"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "app.doql.less" ]; then
  echo "❌ app.doql.less not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}};
  step-3: run cmd=echo "✅ Exported to {{.DOQL_OUTPUT}}";
}

workflow[name="doql:validate"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} validate;
}

workflow[name="doql:doctor"] {
  trigger: manual;
  step-1: run cmd={{.DOQL_CMD}} doctor;
}

workflow[name="doql:build"] {
  trigger: manual;
  step-1: run cmd=if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
  echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
  exit 1
fi;
  step-2: run cmd={{.DOQL_CMD}} build app.doql.less --out build/;
}

workflow[name="docs:build"] {
  trigger: manual;
  step-1: run cmd=echo "Building SUMD documentation...";
  step-2: run cmd={{.VENV_PY}} -m sumd.cli docs/ docs/;
}

workflow[name="sumd"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m sumd.cli scan .;
}

workflow[name="sumr"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m sumd.cli scan . --profile refactor;
}

workflow[name="version:bump"] {
  trigger: manual;
  step-1: run cmd=hatch version patch;
  step-2: run cmd=echo "✅ Version bumped:";
  step-3: run cmd=hatch version;
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd={{.VENV_PY}} -m twine upload dist/*;
}

workflow[name="doctor"] {
  trigger: manual;
  step-1: run cmd=echo "=== sumd doctor ==="
check() { "$@" > /dev/null 2>&1 && echo "  ✅ $1" || echo "  ❌ $1  (command failed: $*)"; }
check {{.VENV_PY}} -m pyqual doctor
check {{.VENV_PY}} -m pytest --version
check ruff --version
check {{.PWD}}/.venv/bin/sumd --version
check {{.PWD}}/.venv/bin/sumd --help
echo "=== done ===";
}

workflow[name="help"] {
  trigger: manual;
  step-1: run cmd=task --list;
}

workflow[name="analyze"] {
  trigger: manual;
  step-1: run cmd=echo "🔬 Running project analysis...";
  step-2: run cmd=sumd analyze . --tools code2llm,redup,vallm;
}

deploy {
  target: docker;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.10;
}
```

### Source Modules

- `sumd.cli`
- `sumd.extractor`
- `sumd.generator`
- `sumd.mcp_server`
- `sumd.models`
- `sumd.parser`
- `sumd.pipeline`
- `sumd.renderer`
- `sumd.toon_parser`
- `sumd.validator`

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
# Taskfile.yml — sumd (Structured Unified Markdown Descriptor) project runner
# https://taskfile.dev

version: "3"

vars:
  APP_NAME: sumd
  DOQL_OUTPUT: app.doql.less
  DOQL_CMD: "{{if eq OS \"windows\"}}doql.exe{{else}}doql{{end}}"
  VENV_PY: "{{.PWD}}/.venv/bin/python"
  VENV_PIP: "{{.PWD}}/.venv/bin/pip"

env:
  PYTHONPATH: "{{.PWD}}"

tasks:
  # ─────────────────────────────────────────────────────────────────────────────
  # Development
  # ─────────────────────────────────────────────────────────────────────────────

  install:
    desc: Install Python dependencies (editable)
    cmds:
      - "{{.VENV_PIP}} install -e .[dev]"

  deps:update:
    desc: Upgrade all outdated Python packages in the project venv
    cmds:
      - |
        PIP="{{.VENV_PIP}}"
        $PIP install --upgrade pip
        OUTDATED=$($PIP list --outdated --format=columns 2>/dev/null | tail -n +3 | awk '{print $1}')
        if [ -z "$OUTDATED" ]; then
          echo "✅ All packages are up to date."
        else
          echo "📦 Upgrading: $OUTDATED"
          echo "$OUTDATED" | xargs $PIP install --upgrade
          echo "✅ Done."
        fi

  quality:
    desc: Run pyqual quality pipeline (uses pyqual.yaml from cwd)
    cmds:
      - "{{.VENV_PY}} -m pyqual run"

  quality:fix:
    desc: Run pyqual with auto-fix (uses pyqual.yaml from cwd)
    cmds:
      - "{{.VENV_PY}} -m pyqual run --fix"

  quality:report:
    desc: Generate pyqual quality report (uses pyqual.yaml from cwd)
    cmds:
      - "{{.VENV_PY}} -m pyqual report"

  test:
    desc: Run pytest suite
    cmds:
      - "{{.VENV_PY}} -m pytest -q"

  test:report:
    desc: Run pytest suite and generate HTML report
    cmds:
      - "{{.VENV_PY}} -m pytest --json-report --json-report-file=test-results.json -q"
      - "{{.VENV_PY}} -m testql report test-results.json -o report.html"

  test:report:example:
    desc: Generate example testql HTML report
    cmds:
      - "{{.VENV_PY}} -m testql report --example -o report.html"

  lint:
    desc: Run ruff lint check
    cmds:
      - ruff check .

  fmt:
    desc: Auto-format with ruff
    cmds:
      - ruff format .

  build:
    desc: Build wheel + sdist
    cmds:
      - "{{.VENV_PY}} -m build"

  clean:
    desc: Remove build artefacts
    cmds:
      - rm -rf build/ dist/ *.egg-info

  all:
    desc: Run install, quality check
    cmds:
      - task: install
      - task: quality

  # ─────────────────────────────────────────────────────────────────────────────
  # Doql Integration
  # ─────────────────────────────────────────────────────────────────────────────

  structure:
    desc: Generate project structure (app.doql.less)
    cmds:
      - |
        echo "📁 Analyzing sumd project structure..."
        {{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force
        echo "✅ Structure generated: {{.DOQL_OUTPUT}}"

  doql:adopt:
    desc: Reverse-engineer sumd project structure (LESS format)
    cmds:
      - "{{.DOQL_CMD}} adopt {{.PWD}} --output app.doql.less --force"
      - echo "✅ Captured in app.doql.less"

  doql:export:
    desc: Export app.doql.less to other formats
    cmds:
      - |
        if [ ! -f "app.doql.less" ]; then
          echo "❌ app.doql.less not found. Run: task structure"
          exit 1
        fi
      - "{{.DOQL_CMD}} export --format less -o {{.DOQL_OUTPUT}}"
      - echo "✅ Exported to {{.DOQL_OUTPUT}}"

  doql:validate:
    desc: Validate app.doql.less syntax
    cmds:
      - |
        if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
          echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
          exit 1
        fi
      - "{{.DOQL_CMD}} validate"

  doql:doctor:
    desc: Run doql health checks
    cmds:
      - "{{.DOQL_CMD}} doctor"

  doql:build:
    desc: Generate code from app.doql.less
    cmds:
      - |
        if [ ! -f "{{.DOQL_OUTPUT}}" ]; then
          echo "❌ {{.DOQL_OUTPUT}} not found. Run: task structure"
          exit 1
        fi
      - "{{.DOQL_CMD}} build app.doql.less --out build/"

  analyze:
    desc: Full doql analysis (structure + validate + doctor)
    cmds:
      - task: structure
      - task: doql:validate
      - task: doql:doctor

  # ─────────────────────────────────────────────────────────────────────────────
  # Documentation
  # ─────────────────────────────────────────────────────────────────────────────

  docs:build:
    desc: Build documentation
    cmds:
      - echo "Building SUMD documentation..."
      - "{{.VENV_PY}} -m sumd.cli docs/ docs/"

  # ─────────────────────────────────────────────────────────────────────────────
  # SUMD Documentation Generation
  # ─────────────────────────────────────────────────────────────────────────────

  sumd:
    desc: Generate SUMD.md (full project documentation)
    cmds:
      - "{{.VENV_PY}} -m sumd.cli scan ."

  sumr:
    desc: Generate SUMR.md (pre-refactoring analysis report)
    cmds:
      - "{{.VENV_PY}} -m sumd.cli scan . --profile refactor"

  # ─────────────────────────────────────────────────────────────────────────────
  # Release
  # ─────────────────────────────────────────────────────────────────────────────

  version:bump:
    desc: Bump patch version (hatch)
    cmds:
      - hatch version patch
      - echo "✅ Version bumped:"
      - hatch version

  publish:
    desc: Build and publish to PyPI
    cmds:
      - task: clean
      - task: build
      - "{{.VENV_PY}} -m twine upload dist/*"

  # ─────────────────────────────────────────────────────────────────────────────
  # Utility
  # ─────────────────────────────────────────────────────────────────────────────

  check:
    desc: Full pre-commit check (lint + test + quality)
    cmds:
      - task: lint
      - task: test
      - task: quality

  doctor:
    desc: Smoke-test all external CLI tools used by this project
    cmds:
      - |
        echo "=== sumd doctor ==="
        check() { "$@" > /dev/null 2>&1 && echo "  ✅ $1" || echo "  ❌ $1  (command failed: $*)"; }
        check {{.VENV_PY}} -m pyqual doctor
        check {{.VENV_PY}} -m pytest --version
        check ruff --version
        check {{.PWD}}/.venv/bin/sumd --version
        check {{.PWD}}/.venv/bin/sumd --help
        echo "=== done ==="

  help:
    desc: Show available tasks
    cmds:
      - task --list

  all:
    desc: Install, full check, generate SUMD docs
    cmds:
      - task: install
      - task: check
      - task: sumd
```

## Quality Pipeline (`pyqual.yaml`)

```yaml markpact:pyqual path=pyqual.yaml
pipeline:
  name: quality-loop

  # Quickstart: replace all of this with a single profile line:
  #   profile: python-minimal   # analyze → validate → lint → fix → test
  #   profile: python-publish   # + git-push and make-publish
  #   profile: python-secure    # + pip-audit, bandit, detect-secrets
  #   profile: python           # standard (needs manual stage config)
  #   profile: ci               # CI-only, no fix
  # See: pyqual profiles

  # Quality gates — pipeline iterates until ALL pass
  metrics:
    cc_max: 15           # cyclomatic complexity per function
    vallm_pass_min: 60   # vallm validation pass rate (%)
    coverage_min: 35     # branch+statement coverage (%) — 37% measured with --cov-branch

  # Pipeline stages — use 'tool:' for built-in presets or 'run:' for custom commands
  # See all presets: pyqual tools
  # when: any_stage_fail    — run only when a prior stage in this iteration failed
  # when: metrics_fail      — run only when quality gates are not yet passing
  # when: first_iteration   — run only on iteration 1 (skip re-runs after fix)
  # when: after_fix         — run only after the fix stage ran in this iteration
  stages:
    - name: analyze
      tool: code2llm-filtered   # uses sensible exclude defaults

    - name: validate
      tool: vallm-filtered      # uses sensible exclude defaults

    - name: prefact
      tool: prefact
      optional: true
      when: any_stage_fail
      timeout: 900

    - name: fix
      tool: llx-fix
      optional: true
      when: any_stage_fail
      timeout: 1800

    - name: test
      tool: pytest

    - name: push
      tool: git-push            # built-in: git add + commit + push
      optional: true
      timeout: 120

    - name: publish
      tool: twine-publish       # built-in: python -m build + twine upload
      optional: true
      when: metrics_pass
      timeout: 120

  # Loop behavior
  loop:
    max_iterations: 3
    on_fail: report      # report | create_ticket | block
    ticket_backends:     # backends to sync when on_fail = create_ticket
      - markdown        # TODO.md (default)
      # - github        # GitHub Issues (requires GITHUB_TOKEN)

  # Environment (optional)
  env:
    LLM_MODEL: openrouter/qwen/qwen3-coder-next
```

## Dependencies

### Runtime

```text markpact:deps python
click>=8.3.3
pyyaml>=6.0.3
toml>=0.10.2
goal>=2.1.190
costs>=0.1.50
pfix>=0.1.72
```

### Development

```text markpact:deps python scope=dev
pytest>=9.0.3
pytest-cov>=7.1.0
ruff>=0.15.11
build>=1.4.4
twine>=6.2.0
pyqual>=0.1.143
goal>=2.1.190
costs>=0.1.50
pfix>=0.1.72
mcp>=1.27.0
```

## Source Map

*Top 5 modules by symbol density — signatures for LLM orientation.*

### `sumd.cli` (`sumd/cli.py`)

```python
def _detect_project_type(proj_dir)  # CC=8, fan=4
def _render_doql_boilerplate(project_name, spec, extra_workflows)  # CC=4, fan=3
def _node_framework(deps)  # CC=5, fan=0
def _node_spec_from_package_json(pkg_json)  # CC=7, fan=5
def _build_doql_spec(proj_dir, project_type)  # CC=3, fan=4
def _generate_doql_less(proj_dir, project_name, version, force, project_type)  # CC=7, fan=8
def cli()  # CC=1, fan=2
def validate(file)  # CC=4, fan=8
def export(file, format, output)  # CC=8, fan=11
def info(file)  # CC=3, fan=7
def generate(file, format, output)  # CC=8, fan=15
def extract(file, section)  # CC=5, fan=8
def _is_project_dir(d)  # CC=8, fan=4
def _walk_projects(path, projects, max_depth, depth)  # CC=10, fan=7 ⚠
def _detect_projects(workspace, max_depth)  # CC=1, fan=1
def _ensure_venv(tools_dir, venv_dir, tool_list)  # CC=4, fan=4
def _tool_bin(bin_dir, name)  # CC=2, fan=1
def _run_one_tool(tool, bin_dir, proj_dir, project_output)  # CC=3, fan=5
def _run_analysis_tools(proj_dir, tool_list, skip_tools)  # CC=5, fan=5
def _export_sumd_json(proj_dir, doc)  # CC=2, fan=2
def _render_write_validate(proj_dir, sumd_path, raw, profile)  # CC=5, fan=5
def _echo_scan_result(proj_dir, doc, sources, cb_warnings)  # CC=2, fan=3
def _maybe_generate_doql(proj_dir, fix)  # CC=7, fan=6
def _finalize_scan(proj_dir, doc, sources, cb_warnings, export_json, run_analyze, tool_list, doql_sync, sumd_path)  # CC=9, fan=9
def _scan_one_project(proj_dir, fix, raw, export_json, run_analyze, tool_list, parser_inst, profile, generate_doql, doql_sync)  # CC=9, fan=8
def scan(workspace, export_json, report, fix, raw, analyze, tools, profile, depth, generate_doql, doql_sync)  # CC=10, fan=18 ⚠
def lint(files, workspace, as_json)  # CC=10, fan=12 ⚠
def _lint_collect_paths(files, workspace)  # CC=6, fan=7
def _lint_print_result(path, r)  # CC=9, fan=2
def _setup_tools_venv(venv_dir, tool_list, force)  # CC=7, fan=6
def _run_code2llm_formats(bin_dir, project, project_output)  # CC=5, fan=4
def _run_tool_subprocess(bin_dir, tool, cmd_args)  # CC=3, fan=4
def analyze(project, tools, force)  # CC=11, fan=17 ⚠
def _api_scenario_template(name, scenario_type, endpoints_block, base_path)  # CC=1, fan=3
def _scaffold_write(path, content, force, generated, skipped)  # CC=3, fan=3
def _scaffold_smoke_scenario(paths, base, out_dir, force, generated, skipped)  # CC=6, fan=5
def _scaffold_crud_scenarios(groups, base, out_dir, force, generated, skipped)  # CC=5, fan=7
def _scaffold_from_openapi(spec, out_dir, scenario_type, force, generated, skipped)  # CC=7, fan=12
def _scaffold_generic(out_dir, force, generated, skipped)  # CC=1, fan=3
def scaffold(project, output, force, scenario_type)  # CC=9, fan=18
def map_cmd(project, output, force, stdout)  # CC=7, fan=12
def main()  # CC=10, fan=3 ⚠
def main_sumr()  # CC=3, fan=2
```

### `sumd.extractor` (`sumd/extractor.py`)

```python
def _read_toml(path)  # CC=2, fan=2
def extract_pyproject(proj_dir)  # CC=3, fan=5
def _first_task_cmd(cmds)  # CC=4, fan=2
def extract_taskfile(proj_dir)  # CC=6, fan=8
def _parse_openapi_endpoints(paths)  # CC=8, fan=7
def extract_openapi(proj_dir)  # CC=5, fan=7
def _parse_doql_entities(content)  # CC=4, fan=5
def _parse_doql_interfaces(content)  # CC=3, fan=7
def _parse_doql_workflows(content)  # CC=7, fan=10
def _parse_doql_content(content)  # CC=6, fan=14
def extract_doql(proj_dir)  # CC=3, fan=3
def extract_pyqual(proj_dir)  # CC=5, fan=5
def extract_python_modules(proj_dir, pkg_name)  # CC=4, fan=4
def extract_readme_title(proj_dir)  # CC=4, fan=5
def extract_requirements(proj_dir)  # CC=7, fan=7
def extract_makefile(proj_dir)  # CC=7, fan=9
def extract_goal(proj_dir)  # CC=3, fan=7
def extract_env(proj_dir)  # CC=10, fan=9 ⚠
def _parse_dockerfile_line(line, parsed)  # CC=8, fan=6
def extract_dockerfile(proj_dir)  # CC=6, fan=5
def extract_docker_compose(proj_dir)  # CC=10, fan=12 ⚠
def extract_package_json(proj_dir)  # CC=3, fan=6
def _lang_of(path)  # CC=1, fan=2
def _fan_out(func_node)  # CC=5, fan=5
def _cc_estimate(func_node)  # CC=4, fan=4
def _try_radon_cc(src)  # CC=3, fan=1
def _analyse_py_top_funcs(tree, radon_cc)  # CC=5, fan=6
def _analyse_class_methods(node, radon_cc)  # CC=6, fan=6
def _analyse_py_top_classes(tree, radon_cc)  # CC=5, fan=7
def _analyse_py_module(path)  # CC=2, fan=6
def _is_map_ignored_path(p)  # CC=4, fan=1
def _collect_map_files(proj_dir)  # CC=7, fan=10
def _render_map_detail(proj_dir, modules)  # CC=5, fan=3
def _map_cc_stats(all_funcs)  # CC=12, fan=8 ⚠
def _render_py_module_detail(rel, info, a)  # CC=7, fan=3
def generate_map_toon(proj_dir)  # CC=5, fan=13
def required_tools_for_profile(profile)  # CC=4, fan=0
def extract_source_snippets(proj_dir, pkg_name)  # CC=6, fan=11
def extract_swop(proj_dir)  # CC=9, fan=8
def extract_project_analysis(proj_dir, refactor)  # CC=6, fan=7
```

### `sumd.pipeline` (`sumd/pipeline.py`)

```python
def _refresh_map_toon(proj_dir)  # CC=3, fan=3
def _find_tools_bin_dir(proj_dir)  # CC=3, fan=1
def _run_tool_if_present(bin_dir, name, args, proj_dir)  # CC=3, fan=3
def _refresh_analysis_files(proj_dir, profile)  # CC=7, fan=5
def _collect_tool_sources(pyproj, reqs, tasks, makefile, scenarios)  # CC=7, fan=3
def _doql_sources(doql)  # CC=4, fan=1
def _collect_pkg_sources(pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars)  # CC=5, fan=6
def _collect_infra_sources(dockerfile, compose, pkg_json, modules, project_analysis)  # CC=6, fan=3
def _collect_sources(pyproj, reqs, tasks, makefile, scenarios, openapi, doql, pyqual, goal, env_vars, dockerfile, compose, pkg_json, modules, project_analysis, swop)  # CC=2, fan=4
def _inject_toc(content)  # CC=3, fan=6
class RenderPipeline:  # Collect project data → build sections → render → inject TOC.
    def __init__(proj_dir, raw_sources)  # CC=1
    def _collect()  # CC=3
    def _build_registered_sections(ctx, profile)  # CC=4
    def _render_legacy_sections(ctx)  # CC=1
    def _assemble(ctx, profile)  # CC=4
    def run(profile, return_sources)  # CC=2
```

### `sumd.validator` (`sumd/validator.py`)

```python
def _validate_yaml_body(body, path)  # CC=2, fan=1
def _validate_less_css_body(body, path)  # CC=2, fan=1
def _validate_mermaid_body(body, path)  # CC=3, fan=4
def _validate_toon_body(body, path)  # CC=2, fan=1
def _validate_bash_body(body, path)  # CC=4, fan=1
def _validate_deps_body(body, path)  # CC=5, fan=6
def _validate_markpact_meta(mp, line_no, lang, meta, issues)  # CC=5, fan=6
def validate_codeblocks(content, source)  # CC=9, fan=11
def _check_h1(lines, source)  # CC=3, fan=2
def _check_required_sections(lines, source, profile)  # CC=7, fan=6
def _check_metadata_fields(lines, source)  # CC=9, fan=6
def _check_unclosed_fences(lines, source)  # CC=4, fan=2
def _check_empty_links(content, source)  # CC=2, fan=1
def validate_markdown(content, source, profile)  # CC=1, fan=6
def validate_sumd_file(path, profile)  # CC=3, fan=5
class CodeBlockIssue:
```

### `sumd.mcp_server` (`sumd/mcp_server.py`)

```python
def _doc_to_dict(doc)  # CC=2, fan=0
def _resolve_path(path)  # CC=2, fan=3
def list_tools()  # CC=1, fan=2
def _tool_parse_sumd(arguments)  # CC=1, fan=5
def _tool_validate_sumd(arguments)  # CC=1, fan=7
def _tool_export_sumd(arguments)  # CC=5, fan=8
def _tool_list_sections(arguments)  # CC=2, fan=4
def _tool_get_section(arguments)  # CC=5, fan=6
def _tool_info_sumd(arguments)  # CC=2, fan=5
def _tool_generate_sumd(arguments)  # CC=5, fan=5
def call_tool(name, arguments)  # CC=3, fan=4
def main()  # CC=1, fan=3
```

## Call Graph

*178 nodes · 160 edges · 26 modules · CC̄=1.2*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `run` *(in examples.mcp.mcp_client)* | 11 ⚠ | 1 | 53 | **54** |
| `print` *(in README)* | 0 | 42 | 0 | **42** |
| `analyze` *(in sumd.cli)* | 11 ⚠ | 0 | 33 | **33** |
| `_collect` *(in sumd.pipeline.RenderPipeline)* | 3 | 0 | 31 | **31** |
| `_render_call_graph` *(in sumd.sections.call_graph)* | 7 | 1 | 28 | **29** |
| `_render_api_stubs` *(in sumd.sections.api_stubs)* | 11 ⚠ | 1 | 27 | **28** |
| `_render_swop_section` *(in sumd.sections.swop)* | 9 | 1 | 24 | **25** |
| `generate_map_toon` *(in sumd.extractor)* | 5 | 0 | 24 | **24** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/sumd
# nodes: 178 | edges: 160 | modules: 26
# CC̄=1.2

HUBS[20]:
  examples.mcp.mcp_client.run
    CC=11  in:1  out:53  total:54
  README.print
    CC=0  in:42  out:0  total:42
  sumd.cli.analyze
    CC=11  in:0  out:33  total:33
  sumd.pipeline.RenderPipeline._collect
    CC=3  in:0  out:31  total:31
  sumd.sections.call_graph._render_call_graph
    CC=7  in:1  out:28  total:29
  sumd.sections.api_stubs._render_api_stubs
    CC=11  in:1  out:27  total:28
  sumd.sections.swop._render_swop_section
    CC=9  in:1  out:24  total:25
  sumd.extractor.generate_map_toon
    CC=5  in:0  out:24  total:24
  sumd.sections.quality._render_quality_parsed
    CC=9  in:1  out:21  total:22
  sumd.cli.map_cmd
    CC=7  in:0  out:20  total:20
  sumd.sections.dependencies._render_deps_runtime
    CC=6  in:1  out:19  total:20
  sumd.sections.interfaces._render_interfaces_openapi
    CC=6  in:1  out:19  total:20
  sumd.extractor._parse_doql_content
    CC=6  in:1  out:19  total:20
  sumd.cli.lint
    CC=10  in:0  out:19  total:19
  sumd.extractor._parse_doql_workflows
    CC=7  in:1  out:18  total:19
  sumd.sections.environment._render_goal_section
    CC=9  in:1  out:17  total:18
  sumd.sections.workflows._render_workflows_taskfile
    CC=6  in:1  out:17  total:18
  sumd.validator.validate_codeblocks
    CC=9  in:1  out:17  total:18
  sumd.extractor.extract_pyproject
    CC=3  in:0  out:17  total:17
  sumd.sections.source_snippets._render_source_snippets
    CC=8  in:1  out:16  total:17

MODULES:
  README  [1 funcs]
    print  CC=0  out:0
  SUMR  [14 funcs]
    _inject_toc  CC=0  out:0
    extract_doql  CC=0  out:0
    extract_makefile  CC=0  out:0
    extract_openapi  CC=0  out:0
    extract_package_json  CC=0  out:0
    extract_pyproject  CC=0  out:0
    extract_pyqual  CC=0  out:0
    extract_python_modules  CC=0  out:0
    extract_readme_title  CC=0  out:0
    extract_requirements  CC=0  out:0
  examples.llm.anthropic_example  [2 funcs]
    ask  CC=1  out:3
    main  CC=2  out:14
  examples.llm.openai_example  [3 funcs]
    ask  CC=1  out:3
    build_context  CC=5  out:9
    main  CC=2  out:15
  examples.mcp.mcp_client  [2 funcs]
    main  CC=3  out:12
    run  CC=11  out:53
  sumd.cli  [37 funcs]
    _api_scenario_template  CC=1  out:3
    _build_doql_spec  CC=3  out:4
    _detect_project_type  CC=8  out:4
    _detect_projects  CC=1  out:1
    _echo_scan_result  CC=2  out:4
    _ensure_venv  CC=4  out:7
    _export_sumd_json  CC=2  out:2
    _finalize_scan  CC=9  out:16
    _generate_doql_less  CC=7  out:10
    _is_project_dir  CC=8  out:4
  sumd.extractor  [25 funcs]
    _analyse_class_methods  CC=6  out:6
    _analyse_py_module  CC=2  out:6
    _analyse_py_top_classes  CC=5  out:8
    _analyse_py_top_funcs  CC=5  out:7
    _cc_estimate  CC=4  out:4
    _collect_map_files  CC=7  out:11
    _fan_out  CC=5  out:8
    _first_task_cmd  CC=4  out:4
    _is_map_ignored_path  CC=4  out:1
    _lang_of  CC=1  out:2
  sumd.mcp_server  [9 funcs]
    _doc_to_dict  CC=2  out:0
    _resolve_path  CC=2  out:4
    _tool_export_sumd  CC=5  out:12
    _tool_generate_sumd  CC=5  out:11
    _tool_get_section  CC=5  out:8
    _tool_info_sumd  CC=2  out:5
    _tool_list_sections  CC=2  out:4
    _tool_parse_sumd  CC=1  out:5
    _tool_validate_sumd  CC=1  out:7
  sumd.parser  [1 funcs]
    parse_file  CC=1  out:2
  sumd.pipeline  [11 funcs]
    _collect  CC=3  out:31
    run  CC=2  out:3
    _collect_infra_sources  CC=6  out:10
    _collect_pkg_sources  CC=5  out:11
    _collect_sources  CC=2  out:4
    _collect_tool_sources  CC=7  out:6
    _doql_sources  CC=4  out:4
    _find_tools_bin_dir  CC=3  out:1
    _refresh_analysis_files  CC=7  out:11
    _refresh_map_toon  CC=3  out:3
  sumd.sections.api_stubs  [2 funcs]
    render  CC=1  out:1
    _render_api_stubs  CC=11  out:27
  sumd.sections.architecture  [8 funcs]
    render  CC=1  out:1
    _render_architecture  CC=6  out:12
    _render_architecture_doql_parsed  CC=1  out:4
    _render_architecture_doql_section  CC=6  out:14
    _render_doql_app  CC=3  out:8
    _render_doql_entities  CC=6  out:9
    _render_doql_integrations  CC=5  out:9
    _render_doql_interfaces  CC=6  out:10
  sumd.sections.call_graph  [7 funcs]
    render  CC=1  out:1
    _parse_calls_header  CC=6  out:12
    _parse_calls_hubs  CC=8  out:4
    _parse_calls_toon  CC=1  out:3
    _parse_hub_stat_line  CC=2  out:9
    _process_in_hubs_line  CC=6  out:6
    _render_call_graph  CC=7  out:28
  sumd.sections.code_analysis  [2 funcs]
    render  CC=1  out:1
    _render_code_analysis  CC=9  out:15
  sumd.sections.configuration  [2 funcs]
    render  CC=1  out:1
    _render_configuration_section  CC=1  out:0
  sumd.sections.dependencies  [4 funcs]
    render  CC=1  out:1
    _render_dependencies  CC=2  out:6
    _render_deps_dev  CC=6  out:15
    _render_deps_runtime  CC=6  out:19
  sumd.sections.deployment  [6 funcs]
    render  CC=1  out:1
    _render_deployment  CC=1  out:5
    _render_deployment_docker  CC=8  out:7
    _render_deployment_install  CC=2  out:11
    _render_deployment_reqs  CC=5  out:9
    _render_dockerfile_info  CC=6  out:9
  sumd.sections.environment  [3 funcs]
    render  CC=1  out:4
    _render_env_section  CC=3  out:7
    _render_goal_section  CC=9  out:17
  sumd.sections.extras  [4 funcs]
    render  CC=1  out:1
    _render_extras  CC=3  out:3
    _render_makefile_targets  CC=3  out:4
    _render_pkg_json_scripts  CC=7  out:16
  sumd.sections.interfaces  [7 funcs]
    render  CC=1  out:1
    _render_interfaces  CC=5  out:9
    _render_interfaces_openapi  CC=6  out:19
    _render_interfaces_testql  CC=3  out:4
    _render_testql_extras  CC=7  out:9
    _render_testql_one_structured  CC=7  out:13
    _render_testql_raw  CC=4  out:12
  sumd.sections.quality  [4 funcs]
    render  CC=1  out:1
    _render_quality  CC=3  out:4
    _render_quality_parsed  CC=9  out:21
    _render_quality_raw  CC=2  out:7
  sumd.sections.source_snippets  [2 funcs]
    render  CC=1  out:1
    _render_source_snippets  CC=8  out:16
  sumd.sections.swop  [2 funcs]
    render  CC=1  out:1
    _render_swop_section  CC=9  out:24
  sumd.sections.workflows  [4 funcs]
    render  CC=1  out:1
    _render_workflows  CC=4  out:5
    _render_workflows_doql  CC=4  out:7
    _render_workflows_taskfile  CC=6  out:17
  sumd.toon_parser  [7 funcs]
    _parse_toon_block_api  CC=6  out:4
    _parse_toon_block_assert  CC=7  out:9
    _parse_toon_block_config  CC=9  out:8
    _parse_toon_block_navigate  CC=7  out:5
    _parse_toon_block_performance  CC=7  out:8
    _parse_toon_file  CC=4  out:16
    extract_testql_scenarios  CC=7  out:12
  sumd.validator  [9 funcs]
    _check_empty_links  CC=2  out:1
    _check_h1  CC=3  out:2
    _check_metadata_fields  CC=9  out:7
    _check_required_sections  CC=7  out:6
    _check_unclosed_fences  CC=4  out:2
    _validate_markpact_meta  CC=5  out:9
    validate_codeblocks  CC=9  out:17
    validate_markdown  CC=1  out:6
    validate_sumd_file  CC=3  out:5

EDGES:
  examples.llm.anthropic_example.ask → sumd.parser.SUMDParser.parse_file
  examples.llm.anthropic_example.main → README.print
  examples.llm.anthropic_example.main → examples.llm.anthropic_example.ask
  examples.llm.openai_example.build_context → sumd.parser.SUMDParser.parse_file
  examples.llm.openai_example.ask → examples.llm.openai_example.build_context
  examples.llm.openai_example.main → README.print
  examples.mcp.mcp_client.run → README.print
  examples.mcp.mcp_client.main → README.print
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_config
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_api
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_assert
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_performance
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_navigate
  sumd.toon_parser.extract_testql_scenarios → sumd.toon_parser._parse_toon_file
  sumd.validator.validate_codeblocks → sumd.validator._validate_markpact_meta
  sumd.validator.validate_markdown → sumd.validator._check_empty_links
  sumd.validator.validate_markdown → sumd.validator._check_unclosed_fences
  sumd.validator.validate_markdown → sumd.validator._check_metadata_fields
  sumd.validator.validate_markdown → sumd.validator._check_h1
  sumd.validator.validate_markdown → sumd.validator._check_required_sections
  sumd.validator.validate_sumd_file → sumd.validator.validate_markdown
  sumd.validator.validate_sumd_file → sumd.validator.validate_codeblocks
  sumd.cli._node_spec_from_package_json → sumd.cli._node_framework
  sumd.cli._build_doql_spec → SUMR.extract_package_json
  sumd.cli._build_doql_spec → sumd.cli._node_spec_from_package_json
  sumd.cli._generate_doql_less → sumd.cli._build_doql_spec
  sumd.cli._generate_doql_less → sumd.cli._render_doql_boilerplate
  sumd.cli.validate → sumd.parser.SUMDParser.parse_file
  sumd.cli.export → sumd.parser.SUMDParser.parse_file
  sumd.cli.info → sumd.parser.SUMDParser.parse_file
  sumd.cli.extract → sumd.parser.SUMDParser.parse_file
  sumd.cli._walk_projects → sumd.cli._is_project_dir
  sumd.cli._detect_projects → sumd.cli._walk_projects
  sumd.cli._run_one_tool → sumd.cli._tool_bin
  sumd.cli._run_analysis_tools → sumd.cli._ensure_venv
  sumd.cli._run_analysis_tools → sumd.cli._run_one_tool
  sumd.cli._render_write_validate → SUMR.validate_sumd_file
  sumd.cli._render_write_validate → sumd.parser.SUMDParser.parse_file
  sumd.cli._maybe_generate_doql → sumd.cli._detect_project_type
  sumd.cli._maybe_generate_doql → SUMR.extract_pyproject
  sumd.cli._maybe_generate_doql → sumd.cli._generate_doql_less
  sumd.cli._maybe_generate_doql → SUMR.extract_package_json
  sumd.cli._finalize_scan → sumd.cli._echo_scan_result
  sumd.cli._finalize_scan → sumd.cli._export_sumd_json
  sumd.cli._finalize_scan → sumd.cli._run_analysis_tools
  sumd.cli._scan_one_project → sumd.cli._render_write_validate
  sumd.cli._scan_one_project → sumd.cli._finalize_scan
  sumd.cli._scan_one_project → sumd.cli._maybe_generate_doql
  sumd.cli.lint → sumd.cli._lint_collect_paths
  sumd.cli.lint → SUMR.validate_sumd_file
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

### Smoke (1)

**`smoke-generic.testql.toon.yaml — smoke tests for sumd CLI`**
- `GET /health` → `200`
- assert `status < 500`

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/sumd
# nodes: 178 | edges: 160 | modules: 26
# CC̄=1.2

HUBS[20]:
  examples.mcp.mcp_client.run
    CC=11  in:1  out:53  total:54
  README.print
    CC=0  in:42  out:0  total:42
  sumd.cli.analyze
    CC=11  in:0  out:33  total:33
  sumd.pipeline.RenderPipeline._collect
    CC=3  in:0  out:31  total:31
  sumd.sections.call_graph._render_call_graph
    CC=7  in:1  out:28  total:29
  sumd.sections.api_stubs._render_api_stubs
    CC=11  in:1  out:27  total:28
  sumd.sections.swop._render_swop_section
    CC=9  in:1  out:24  total:25
  sumd.extractor.generate_map_toon
    CC=5  in:0  out:24  total:24
  sumd.sections.quality._render_quality_parsed
    CC=9  in:1  out:21  total:22
  sumd.cli.map_cmd
    CC=7  in:0  out:20  total:20
  sumd.sections.dependencies._render_deps_runtime
    CC=6  in:1  out:19  total:20
  sumd.sections.interfaces._render_interfaces_openapi
    CC=6  in:1  out:19  total:20
  sumd.extractor._parse_doql_content
    CC=6  in:1  out:19  total:20
  sumd.cli.lint
    CC=10  in:0  out:19  total:19
  sumd.extractor._parse_doql_workflows
    CC=7  in:1  out:18  total:19
  sumd.sections.environment._render_goal_section
    CC=9  in:1  out:17  total:18
  sumd.sections.workflows._render_workflows_taskfile
    CC=6  in:1  out:17  total:18
  sumd.validator.validate_codeblocks
    CC=9  in:1  out:17  total:18
  sumd.extractor.extract_pyproject
    CC=3  in:0  out:17  total:17
  sumd.sections.source_snippets._render_source_snippets
    CC=8  in:1  out:16  total:17

MODULES:
  README  [1 funcs]
    print  CC=0  out:0
  SUMR  [14 funcs]
    _inject_toc  CC=0  out:0
    extract_doql  CC=0  out:0
    extract_makefile  CC=0  out:0
    extract_openapi  CC=0  out:0
    extract_package_json  CC=0  out:0
    extract_pyproject  CC=0  out:0
    extract_pyqual  CC=0  out:0
    extract_python_modules  CC=0  out:0
    extract_readme_title  CC=0  out:0
    extract_requirements  CC=0  out:0
  examples.llm.anthropic_example  [2 funcs]
    ask  CC=1  out:3
    main  CC=2  out:14
  examples.llm.openai_example  [3 funcs]
    ask  CC=1  out:3
    build_context  CC=5  out:9
    main  CC=2  out:15
  examples.mcp.mcp_client  [2 funcs]
    main  CC=3  out:12
    run  CC=11  out:53
  sumd.cli  [37 funcs]
    _api_scenario_template  CC=1  out:3
    _build_doql_spec  CC=3  out:4
    _detect_project_type  CC=8  out:4
    _detect_projects  CC=1  out:1
    _echo_scan_result  CC=2  out:4
    _ensure_venv  CC=4  out:7
    _export_sumd_json  CC=2  out:2
    _finalize_scan  CC=9  out:16
    _generate_doql_less  CC=7  out:10
    _is_project_dir  CC=8  out:4
  sumd.extractor  [25 funcs]
    _analyse_class_methods  CC=6  out:6
    _analyse_py_module  CC=2  out:6
    _analyse_py_top_classes  CC=5  out:8
    _analyse_py_top_funcs  CC=5  out:7
    _cc_estimate  CC=4  out:4
    _collect_map_files  CC=7  out:11
    _fan_out  CC=5  out:8
    _first_task_cmd  CC=4  out:4
    _is_map_ignored_path  CC=4  out:1
    _lang_of  CC=1  out:2
  sumd.mcp_server  [9 funcs]
    _doc_to_dict  CC=2  out:0
    _resolve_path  CC=2  out:4
    _tool_export_sumd  CC=5  out:12
    _tool_generate_sumd  CC=5  out:11
    _tool_get_section  CC=5  out:8
    _tool_info_sumd  CC=2  out:5
    _tool_list_sections  CC=2  out:4
    _tool_parse_sumd  CC=1  out:5
    _tool_validate_sumd  CC=1  out:7
  sumd.parser  [1 funcs]
    parse_file  CC=1  out:2
  sumd.pipeline  [11 funcs]
    _collect  CC=3  out:31
    run  CC=2  out:3
    _collect_infra_sources  CC=6  out:10
    _collect_pkg_sources  CC=5  out:11
    _collect_sources  CC=2  out:4
    _collect_tool_sources  CC=7  out:6
    _doql_sources  CC=4  out:4
    _find_tools_bin_dir  CC=3  out:1
    _refresh_analysis_files  CC=7  out:11
    _refresh_map_toon  CC=3  out:3
  sumd.sections.api_stubs  [2 funcs]
    render  CC=1  out:1
    _render_api_stubs  CC=11  out:27
  sumd.sections.architecture  [8 funcs]
    render  CC=1  out:1
    _render_architecture  CC=6  out:12
    _render_architecture_doql_parsed  CC=1  out:4
    _render_architecture_doql_section  CC=6  out:14
    _render_doql_app  CC=3  out:8
    _render_doql_entities  CC=6  out:9
    _render_doql_integrations  CC=5  out:9
    _render_doql_interfaces  CC=6  out:10
  sumd.sections.call_graph  [7 funcs]
    render  CC=1  out:1
    _parse_calls_header  CC=6  out:12
    _parse_calls_hubs  CC=8  out:4
    _parse_calls_toon  CC=1  out:3
    _parse_hub_stat_line  CC=2  out:9
    _process_in_hubs_line  CC=6  out:6
    _render_call_graph  CC=7  out:28
  sumd.sections.code_analysis  [2 funcs]
    render  CC=1  out:1
    _render_code_analysis  CC=9  out:15
  sumd.sections.configuration  [2 funcs]
    render  CC=1  out:1
    _render_configuration_section  CC=1  out:0
  sumd.sections.dependencies  [4 funcs]
    render  CC=1  out:1
    _render_dependencies  CC=2  out:6
    _render_deps_dev  CC=6  out:15
    _render_deps_runtime  CC=6  out:19
  sumd.sections.deployment  [6 funcs]
    render  CC=1  out:1
    _render_deployment  CC=1  out:5
    _render_deployment_docker  CC=8  out:7
    _render_deployment_install  CC=2  out:11
    _render_deployment_reqs  CC=5  out:9
    _render_dockerfile_info  CC=6  out:9
  sumd.sections.environment  [3 funcs]
    render  CC=1  out:4
    _render_env_section  CC=3  out:7
    _render_goal_section  CC=9  out:17
  sumd.sections.extras  [4 funcs]
    render  CC=1  out:1
    _render_extras  CC=3  out:3
    _render_makefile_targets  CC=3  out:4
    _render_pkg_json_scripts  CC=7  out:16
  sumd.sections.interfaces  [7 funcs]
    render  CC=1  out:1
    _render_interfaces  CC=5  out:9
    _render_interfaces_openapi  CC=6  out:19
    _render_interfaces_testql  CC=3  out:4
    _render_testql_extras  CC=7  out:9
    _render_testql_one_structured  CC=7  out:13
    _render_testql_raw  CC=4  out:12
  sumd.sections.quality  [4 funcs]
    render  CC=1  out:1
    _render_quality  CC=3  out:4
    _render_quality_parsed  CC=9  out:21
    _render_quality_raw  CC=2  out:7
  sumd.sections.source_snippets  [2 funcs]
    render  CC=1  out:1
    _render_source_snippets  CC=8  out:16
  sumd.sections.swop  [2 funcs]
    render  CC=1  out:1
    _render_swop_section  CC=9  out:24
  sumd.sections.workflows  [4 funcs]
    render  CC=1  out:1
    _render_workflows  CC=4  out:5
    _render_workflows_doql  CC=4  out:7
    _render_workflows_taskfile  CC=6  out:17
  sumd.toon_parser  [7 funcs]
    _parse_toon_block_api  CC=6  out:4
    _parse_toon_block_assert  CC=7  out:9
    _parse_toon_block_config  CC=9  out:8
    _parse_toon_block_navigate  CC=7  out:5
    _parse_toon_block_performance  CC=7  out:8
    _parse_toon_file  CC=4  out:16
    extract_testql_scenarios  CC=7  out:12
  sumd.validator  [9 funcs]
    _check_empty_links  CC=2  out:1
    _check_h1  CC=3  out:2
    _check_metadata_fields  CC=9  out:7
    _check_required_sections  CC=7  out:6
    _check_unclosed_fences  CC=4  out:2
    _validate_markpact_meta  CC=5  out:9
    validate_codeblocks  CC=9  out:17
    validate_markdown  CC=1  out:6
    validate_sumd_file  CC=3  out:5

EDGES:
  examples.llm.anthropic_example.ask → sumd.parser.SUMDParser.parse_file
  examples.llm.anthropic_example.main → README.print
  examples.llm.anthropic_example.main → examples.llm.anthropic_example.ask
  examples.llm.openai_example.build_context → sumd.parser.SUMDParser.parse_file
  examples.llm.openai_example.ask → examples.llm.openai_example.build_context
  examples.llm.openai_example.main → README.print
  examples.mcp.mcp_client.run → README.print
  examples.mcp.mcp_client.main → README.print
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_config
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_api
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_assert
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_performance
  sumd.toon_parser._parse_toon_file → sumd.toon_parser._parse_toon_block_navigate
  sumd.toon_parser.extract_testql_scenarios → sumd.toon_parser._parse_toon_file
  sumd.validator.validate_codeblocks → sumd.validator._validate_markpact_meta
  sumd.validator.validate_markdown → sumd.validator._check_empty_links
  sumd.validator.validate_markdown → sumd.validator._check_unclosed_fences
  sumd.validator.validate_markdown → sumd.validator._check_metadata_fields
  sumd.validator.validate_markdown → sumd.validator._check_h1
  sumd.validator.validate_markdown → sumd.validator._check_required_sections
  sumd.validator.validate_sumd_file → sumd.validator.validate_markdown
  sumd.validator.validate_sumd_file → sumd.validator.validate_codeblocks
  sumd.cli._node_spec_from_package_json → sumd.cli._node_framework
  sumd.cli._build_doql_spec → SUMR.extract_package_json
  sumd.cli._build_doql_spec → sumd.cli._node_spec_from_package_json
  sumd.cli._generate_doql_less → sumd.cli._build_doql_spec
  sumd.cli._generate_doql_less → sumd.cli._render_doql_boilerplate
  sumd.cli.validate → sumd.parser.SUMDParser.parse_file
  sumd.cli.export → sumd.parser.SUMDParser.parse_file
  sumd.cli.info → sumd.parser.SUMDParser.parse_file
  sumd.cli.extract → sumd.parser.SUMDParser.parse_file
  sumd.cli._walk_projects → sumd.cli._is_project_dir
  sumd.cli._detect_projects → sumd.cli._walk_projects
  sumd.cli._run_one_tool → sumd.cli._tool_bin
  sumd.cli._run_analysis_tools → sumd.cli._ensure_venv
  sumd.cli._run_analysis_tools → sumd.cli._run_one_tool
  sumd.cli._render_write_validate → SUMR.validate_sumd_file
  sumd.cli._render_write_validate → sumd.parser.SUMDParser.parse_file
  sumd.cli._maybe_generate_doql → sumd.cli._detect_project_type
  sumd.cli._maybe_generate_doql → SUMR.extract_pyproject
  sumd.cli._maybe_generate_doql → sumd.cli._generate_doql_less
  sumd.cli._maybe_generate_doql → SUMR.extract_package_json
  sumd.cli._finalize_scan → sumd.cli._echo_scan_result
  sumd.cli._finalize_scan → sumd.cli._export_sumd_json
  sumd.cli._finalize_scan → sumd.cli._run_analysis_tools
  sumd.cli._scan_one_project → sumd.cli._render_write_validate
  sumd.cli._scan_one_project → sumd.cli._finalize_scan
  sumd.cli._scan_one_project → sumd.cli._maybe_generate_doql
  sumd.cli.lint → sumd.cli._lint_collect_paths
  sumd.cli.lint → SUMR.validate_sumd_file
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 31f 6009L | python:29,shell:2 | 2026-04-23
# CC̄=4.3 | critical:0/230 | dups:0 | cycles:1

HEALTH[0]: ok

REFACTOR[1]:
  1. break 1 circular dependencies

PIPELINES[72]:
  [1] Src [main]: main → ask → build_context → parse_file
      PURITY: 100% pure
  [2] Src [main]: main → ask → parse_file
      PURITY: 100% pure
  [3] Src [main]: main → run
      PURITY: 100% pure
  [4] Src [parse]: parse
      PURITY: 100% pure
  [5] Src [_parse_header]: _parse_header
      PURITY: 100% pure

LAYERS:
  sumd/                           CC̄=4.3    ←in:0  →out:0
  │ !! cli                       1682L  0C   43m  CC=11     ←0
  │ !! extractor                  960L  0C   40m  CC=12     ←2
  │ pipeline                   443L  1C   16m  CC=7      ←0
  │ mcp_server                 358L  0C   12m  CC=5      ←0
  │ validator                  331L  1C   15m  CC=9      ←1
  │ parser                     195L  1C    9m  CC=9      ←4
  │ toon_parser                173L  0C    8m  CC=9      ←1
  │ interfaces                 157L  1C    9m  CC=7      ←0
  │ call_graph                 156L  1C    8m  CC=8      ←0
  │ architecture               156L  1C   10m  CC=6      ←0
  │ deployment                 111L  1C    7m  CC=8      ←0
  │ __init__                   106L  0C    0m  CC=0.0    ←0
  │ dependencies                97L  1C    5m  CC=6      ←0
  │ base                        94L  2C    2m  CC=1      ←0
  │ workflows                   86L  1C    5m  CC=6      ←0
  │ quality                     82L  1C    5m  CC=9      ←0
  │ api_stubs                   76L  1C    3m  CC=11     ←0
  │ extras                      72L  1C    5m  CC=7      ←0
  │ environment                 72L  1C    4m  CC=9      ←0
  │ source_snippets             69L  1C    3m  CC=8      ←0
  │ refactor_analysis           68L  1C    2m  CC=3      ←0
  │ code_analysis               68L  1C    3m  CC=9      ←0
  │ swop                        68L  1C    3m  CC=9      ←0
  │ metadata                    51L  1C    2m  CC=5      ←0
  │ models                      45L  3C    0m  CC=0.0    ←0
  │ configuration               44L  1C    3m  CC=1      ←0
  │ __init__                    35L  0C    0m  CC=0.0    ←0
  │ renderer                    29L  0C    1m  CC=1      ←0
  │ generator                   15L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ project.sh                  41L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=0.0    ←in:0  →out:0
  │ bootstrap.sh                69L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 2 groups | 31f 6113L | 2026-04-23

SUMMARY:
  files_scanned: 31
  total_lines:   6113
  dup_groups:    2
  dup_fragments: 4
  saved_lines:   25
  scan_ms:       12368

HOTSPOTS[2] (files with most duplication):
  sumd/toon_parser.py  dup=28L  groups=1  frags=2  (0.5%)
  sumd/parser.py  dup=22L  groups=1  frags=2  (0.4%)

DUPLICATES[2] (ranked by impact):
  [ec6388d8055c3e57]   STRU  _parse_toon_block_performance  L=14 N=2 saved=14 sim=1.00
      sumd/toon_parser.py:70-83  (_parse_toon_block_performance)
      sumd/toon_parser.py:102-115  (_parse_toon_block_gui)
  [d1ab1a804f1b435b]   STRU  parse  L=11 N=2 saved=11 sim=1.00
      sumd/parser.py:150-160  (parse)
      sumd/parser.py:163-173  (parse_file)

REFACTOR[2] (ranked by priority):
  [1] ○ extract_function   → sumd/utils/_parse_toon_block_performance.py
      WHY: 2 occurrences of 14-line block across 1 files — saves 14 lines
      FILES: sumd/toon_parser.py
  [2] ○ extract_function   → sumd/utils/parse.py
      WHY: 2 occurrences of 11-line block across 1 files — saves 11 lines
      FILES: sumd/parser.py

QUICK_WINS[2] (low risk, high savings — do first):
  [1] extract_function   saved=14L  → sumd/utils/_parse_toon_block_performance.py
      FILES: toon_parser.py
  [2] extract_function   saved=11L  → sumd/utils/parse.py
      FILES: parser.py

EFFORT_ESTIMATE (total ≈ 0.8h):
  easy   _parse_toon_block_performance       saved=14L  ~28min
  easy   parse                               saved=11L  ~22min

METRICS-TARGET:
  dup_groups:  2 → 0
  saved_lines: 25 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 794 func | 32f | 2026-04-23

NEXT[2] (ranked by impact):
  [1] !! SPLIT           sumd/cli.py
      WHY: 1682L, 0 classes, max CC=11
      EFFORT: ~4h  IMPACT: 18502

  [2] !! SPLIT           sumd/extractor.py
      WHY: 960L, 0 classes, max CC=12
      EFFORT: ~4h  IMPACT: 11520


RISKS[2]:
  ⚠ Splitting sumd/cli.py may break 43 import paths
  ⚠ Splitting sumd/extractor.py may break 40 import paths

METRICS-TARGET:
  CC̄:          1.2 → ≤0.8
  max-CC:      12 → ≤6
  god-modules: 2 → 0
  high-CC(≥15): 0 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=1.2 → now CC̄=1.2
```

### Validation (`project/validation.toon.yaml`)

```toon markpact:analysis path=project/validation.toon.yaml
# vallm batch | 102f | 57✓ 0⚠ 7✗ | 2026-04-23

SUMMARY:
  scanned: 102  passed: 57 (55.9%)  warnings: 0  errors: 7  unsupported: 38

ERRORS[7]{path,score}:
  /home/tom/github/oqlos/sumd/sumd/mcp_server.py,0.86
    issues[4]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'mcp.server.stdio' not found,20
      python.import.resolvable,error,Module 'mcp.types' not found,21
      python.import.resolvable,error,Module 'mcp.server' not found,22
      python.import.resolvable,error,Module 'toml' not found,227
  /home/tom/github/oqlos/sumd/tests/test_cli.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,7
  /home/tom/github/oqlos/sumd/tests/test_dogfood.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,17
  /home/tom/github/oqlos/sumd/tests/test_pipeline.py,0.93
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,7
  /home/tom/github/oqlos/sumd/sumd/cli.py,0.96
    issues[2]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'toml' not found,589
      python.import.resolvable,error,Module 'toml' not found,527
  /home/tom/github/oqlos/sumd/sumd/extractor.py,0.96
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'toml' not found,25
  /home/tom/github/oqlos/sumd/tests/test_mcp_server.py,0.96
    issues[1]{rule,severity,message,line}:
      python.import.resolvable,error,Module 'pytest' not found,8

UNSUPPORTED[5]{bucket,count}:
  *.md,20
  Dockerfile*,1
  *.txt,1
  *.yml,6
  other,10
```

## Intent

SUMD - Structured Unified Markdown Descriptor for AI-aware project documentation
