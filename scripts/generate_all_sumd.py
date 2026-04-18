#!/usr/bin/env python3
"""Generate SUMD.md for all projects in the oqlos workspace and validate them."""

import json
import sys
from pathlib import Path

from sumd.parser import SUMDParser, parse_file

# ---------------------------------------------------------------------------
# Templates per project
# ---------------------------------------------------------------------------

PROJECTS = {
    "doql": {
        "name": "doql",
        "title": "DOQL — Declarative Object Query Language",
        "description": (
            "DOQL (Declarative Object Query Language) to warstwa wykonawcza ekosystemu OQL. "
            "Umożliwia budowanie kompletnych aplikacji, dokumentów, kiosków i integracji API "
            "z pojedynczego pliku deklaracji `.doql`."
        ),
        "version": "0.1.2",
        "stack": "Python, Click, YAML, Jinja2",
        "interfaces": [
            "CLI: `doql run app.doql` — uruchom aplikację z pliku deklaracji",
            "CLI: `doql build app.doql --output dist/` — zbuduj artefakty",
            "CLI: `doql validate app.doql` — waliduj plik deklaracji",
            "Python API: `from doql import run, build, validate`",
        ],
        "workflows": [
            "build: pip install -e .",
            "test: pytest tests/ -v",
            "validate: doql validate app.doql",
        ],
        "deps": ["click>=8.0", "pyyaml>=6.0", "jinja2>=3.0"],
    },
    "testql": {
        "name": "testql",
        "title": "TestQL — Interface Query Language for Testing",
        "description": (
            "TestQL to warstwa weryfikacji ekosystemu OQL. "
            "Zapewnia deklaratywne testowanie interfejsów GUI, API i enkoderów "
            "poprzez scenariusze YAML."
        ),
        "version": "0.4.1",
        "stack": "Python, Click, YAML, requests, pytest",
        "interfaces": [
            "CLI: `testql run testql-scenarios/` — uruchom scenariusze testowe",
            "CLI: `testql validate openapi.yaml --scenarios testql-scenarios/` — walidacja",
            "CLI: `testql report --format json --output results.json`",
            "Python API: `from testql import run_scenarios, validate`",
        ],
        "workflows": [
            "build: pip install -e .",
            "test: pytest tests/ -v",
            "run-scenarios: testql run testql-scenarios/",
            "report: testql run testql-scenarios/ --report json --output test-results.json",
        ],
        "deps": ["click>=8.0", "pyyaml>=6.0", "requests>=2.28"],
    },
    "oql": {
        "name": "oql",
        "title": "OQL — Command Line Interface for OqlOS",
        "description": (
            "OQL to interfejs wiersza poleceń dla środowiska uruchomieniowego OqlOS. "
            "Umożliwia wykonywanie scenariuszy OQL, zarządzanie środowiskiem "
            "oraz integrację z pipeline CI/CD."
        ),
        "version": "0.1.1",
        "stack": "Python, Click, YAML",
        "interfaces": [
            "CLI: `oql run scenario.yaml` — wykonaj scenariusz",
            "CLI: `oql list` — lista dostępnych scenariuszy",
            "CLI: `oql status` — status środowiska",
            "Python API: `from oql import run, list_scenarios`",
        ],
        "workflows": [
            "build: pip install -e .",
            "test: pytest tests/ -v",
            "run: oql run testql-scenarios/",
        ],
        "deps": ["click>=8.0", "pyyaml>=6.0", "oqlos>=0.1.1"],
    },
    "oqlos": {
        "name": "oqlos",
        "title": "OqlOS — Operation Query Language Runtime",
        "description": (
            "OqlOS to środowisko uruchomieniowe dla ekosystemu OQL. "
            "Zapewnia REST API, silnik wykonywania scenariuszy, "
            "diagnostykę sprzętu oraz orkiestrację między serwisami."
        ),
        "version": "0.1.1",
        "stack": "Python, FastAPI, uvicorn, YAML, Docker",
        "interfaces": [
            "REST API: `GET /health` — status serwisu",
            "REST API: `POST /run` — uruchom scenariusz",
            "REST API: `GET /scenarios` — lista scenariuszy",
            "REST API: `GET /diagnostics` — diagnostyka sprzętu",
            "CLI: `oqlos start --port 8080`",
            "Python API: `from oqlos import OqlOSApp`",
        ],
        "workflows": [
            "build: pip install -e .",
            "dev: uvicorn oqlos.api:app --reload --port 8080",
            "test: pytest tests/ -v",
            "docker: docker-compose up -d",
        ],
        "deps": ["fastapi>=0.100.0", "uvicorn>=0.20.0", "pyyaml>=6.0", "click>=8.0"],
    },
    "weboql": {
        "name": "weboql",
        "title": "WebOQL — Web-based OQL Scenario Editor",
        "description": (
            "WebOQL to webowy edytor i przeglądarka scenariuszy OQL. "
            "Zapewnia interfejs graficzny do tworzenia, edytowania "
            "i uruchamiania scenariuszy OQL bezpośrednio w przeglądarce."
        ),
        "version": "0.1.2",
        "stack": "Python, FastAPI, uvicorn, HTML, JavaScript, YAML",
        "interfaces": [
            "Web UI: `http://localhost:8090` — edytor scenariuszy",
            "REST API: `GET /api/scenarios` — lista scenariuszy",
            "REST API: `POST /api/run` — uruchom scenariusz",
            "REST API: `PUT /api/scenarios/{name}` — zapisz scenariusz",
            "CLI: `weboql start --port 8090`",
        ],
        "workflows": [
            "build: pip install -e .",
            "dev: weboql start --port 8090 --reload",
            "test: pytest tests/ -v",
            "docker: docker-compose up -d",
        ],
        "deps": ["fastapi>=0.100.0", "uvicorn>=0.20.0", "pyyaml>=6.0"],
    },
    "sumd": {
        "name": "sumd",
        "title": "SUMD — Structured Unified Markdown Descriptor",
        "description": (
            "SUMD to semantyczny format opisu projektu w Markdown. "
            "Definiuje intencje, strukturę, punkty wejścia i model mentalny systemu "
            "zarówno dla ludzi jak i dla LLM."
        ),
        "version": "0.1.7",
        "stack": "Python, Click, PyYAML, TOML, MCP",
        "interfaces": [
            "CLI: `sumd validate SUMD.md` — waliduj dokument",
            "CLI: `sumd export SUMD.md --format json` — eksportuj do JSON/YAML/TOML",
            "CLI: `sumd generate sumd.json --output SUMD.md` — generuj z JSON",
            "CLI: `sumd info SUMD.md` — informacje o dokumencie",
            "MCP: `sumd-mcp` — serwer MCP do odpytywania projektu",
            "Python API: `from sumd import parse_file, validate`",
        ],
        "workflows": [
            "build: pip install -e .",
            "test: pytest tests/ -v",
            "validate: sumd validate SUMD.md",
            "export: sumd export SUMD.md --format json --output sumd.json",
            "mcp: sumd-mcp",
        ],
        "deps": ["click>=8.0", "pyyaml>=6.0", "toml>=0.10.0", "mcp>=1.0.0"],
    },
}


def generate_sumd_content(meta: dict) -> str:
    """Generate SUMD.md content from project metadata."""
    lines = [
        f"# {meta['title']}",
        "",
        meta["description"],
        "",
        "## Metadata",
        "",
        f"- **version**: {meta['version']}",
        f"- **name**: {meta['name']}",
        f"- **stack**: {meta['stack']}",
        f"- **ecosystem**: SUMD + DOQL + testql + taskfile",
        "",
        "## Intent",
        "",
        meta["description"],
        "",
        "## Architecture",
        "",
        "Projekt jest częścią ekosystemu OQL:",
        "",
        "```",
        "SUMD (opis) → DOQL (dane) → taskfile (automatyzacja) → testql (weryfikacja)",
        "```",
        "",
        "## Interfaces",
        "",
    ]
    for iface in meta["interfaces"]:
        lines.append(f"- {iface}")
    lines.append("")

    lines += [
        "## Workflows",
        "",
        "```yaml",
        "tasks:",
    ]
    for wf in meta["workflows"]:
        task, cmd = wf.split(": ", 1) if ": " in wf else (wf, wf)
        lines.append(f"  {task}:")
        lines.append(f"    cmds:")
        lines.append(f"      - {cmd}")
    lines += ["```", ""]

    lines += [
        "## Configuration",
        "",
        "```yaml",
        f"project:",
        f"  name: {meta['name']}",
        f"  version: {meta['version']}",
        "  env: local",
        "```",
        "",
        "## Dependencies",
        "",
    ]
    for dep in meta["deps"]:
        lines.append(f"- `{dep}`")
    lines.append("")

    lines += [
        "## Deployment",
        "",
        "```bash",
        "# Instalacja",
        f"pip install {meta['name']}",
        "",
        "# Instalacja deweloperska",
        "pip install -e .",
        "```",
        "",
    ]
    return "\n".join(lines)


def main():
    base = Path("/home/tom/github/oqlos")
    parser = SUMDParser()
    results = {}

    for proj_name, meta in PROJECTS.items():
        proj_dir = base / proj_name
        if not proj_dir.is_dir():
            print(f"[SKIP] {proj_name} — directory not found")
            continue

        sumd_path = proj_dir / "SUMD.md"
        content = generate_sumd_content(meta)
        sumd_path.write_text(content, encoding="utf-8")
        print(f"[WRITE] {sumd_path}")

        # Validate
        try:
            doc = parse_file(sumd_path)
            errors = parser.validate(doc)
            if errors:
                results[proj_name] = {"status": "INVALID", "errors": errors}
                print(f"  ❌ Validation errors: {errors}")
            else:
                results[proj_name] = {
                    "status": "OK",
                    "project_name": doc.project_name,
                    "sections": len(doc.sections),
                }
                print(f"  ✅ Valid — {doc.project_name} ({len(doc.sections)} sections)")
        except Exception as exc:
            results[proj_name] = {"status": "ERROR", "error": str(exc)}
            print(f"  ❌ Parse error: {exc}")

    # Summary JSON
    summary_path = base / "sumd-validation-report.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[REPORT] {summary_path}")

    # Also export each SUMD.md to JSON
    for proj_name in PROJECTS:
        proj_dir = base / proj_name
        sumd_path = proj_dir / "SUMD.md"
        json_path = proj_dir / "sumd.json"
        if sumd_path.exists():
            try:
                doc = parse_file(sumd_path)
                data = {
                    "project_name": doc.project_name,
                    "description": doc.description,
                    "sections": [
                        {"name": s.name, "type": s.type.value, "content": s.content, "level": s.level}
                        for s in doc.sections
                    ],
                }
                json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[EXPORT] {json_path}")
            except Exception as exc:
                print(f"[ERROR] export {proj_name}: {exc}")

    # Final result
    ok = all(v["status"] == "OK" for v in results.values())
    print(f"\n{'✅ All SUMD documents valid!' if ok else '❌ Some documents have issues.'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
