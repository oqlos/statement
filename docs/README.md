<!-- code2docs:start --># sumd

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-41-green)
> **41** functions | **4** classes | **7** files | CC̄ = 9.9

> Auto-generated project documentation from source code analysis.

**Author:** Tom Sapletta  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/oqlos/statement](https://github.com/oqlos/statement)

## Installation

### From PyPI

```bash
pip install sumd
```

### From Source

```bash
git clone https://github.com/oqlos/statement
cd sumd
pip install -e .
```

### Optional Extras

```bash
pip install sumd[mcp]    # mcp features
```

## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
sumd ./my-project

# Only regenerate README
sumd ./my-project --readme-only

# Preview what would be generated (no file writes)
sumd ./my-project --dry-run

# Check documentation health
sumd check ./my-project

# Sync — regenerate only changed modules
sumd sync ./my-project
```

### Python API

```python
from sumd import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```

## Generated Output

When you run `sumd`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `sumd.yaml` in your project root (or run `sumd init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

sumd can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- sumd:start -->
# Project Title
... auto-generated content ...
<!-- sumd:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
sumd/
├── project├── sumd/    ├── mcp_server    ├── generate_all_sumd    ├── cli    ├── generator    ├── parser```

## API Overview

### Classes

- **`SectionType`** — SUMD section types.
- **`Section`** — Represents a SUMD section.
- **`SUMDDocument`** — Represents a parsed SUMD document.
- **`SUMDParser`** — Parser for SUMD markdown documents.

### Functions

- `list_tools()` — —
- `call_tool(name, arguments)` — —
- `main()` — —
- `cli()` — SUMD - Structured Unified Markdown Descriptor CLI.
- `validate(file)` — Validate a SUMD document.
- `export(file, format, output)` — Export a SUMD document to structured format.
- `info(file)` — Display information about a SUMD document.
- `generate(file, format, output)` — Generate a SUMD document from structured format.
- `extract(file, section)` — Extract content from a SUMD document.
- `scan(workspace, export_json, report, fix)` — Scan a workspace directory and generate SUMD.md for every project found.
- `main()` — Main entry point for the CLI.
- `extract_pyproject(proj_dir)` — —
- `extract_taskfile(proj_dir)` — —
- `extract_testql_scenarios(proj_dir)` — Scan all *.testql.toon.yaml and testql-scenarios/*.yaml files in project.
- `extract_openapi(proj_dir)` — —
- `extract_doql(proj_dir)` — Read app.doql.less and/or app.doql.css and merge into one dict.
- `extract_pyqual(proj_dir)` — —
- `extract_python_modules(proj_dir, pkg_name)` — —
- `extract_readme_title(proj_dir)` — —
- `extract_requirements(proj_dir)` — Parse requirements*.txt files — return list of {file, deps[]}.
- `extract_makefile(proj_dir)` — Parse Makefile — return list of {target, comment}.
- `extract_goal(proj_dir)` — Parse goal.yaml — versioning strategy, git conventions, build strategies.
- `extract_env(proj_dir)` — Parse .env.example — return list of {key, default, comment}.
- `extract_dockerfile(proj_dir)` — Parse Dockerfile — base image, exposed ports, entrypoint, labels.
- `extract_docker_compose(proj_dir)` — Parse docker-compose*.yml — services with images, ports, environment.
- `extract_package_json(proj_dir)` — Parse package.json — name, version, scripts, dependencies.
- `generate_sumd_content(proj_dir, return_sources, raw_sources)` — Generate SUMD.md content from a project directory.
- `parse(content)` — Parse a SUMD markdown document.
- `parse_file(path)` — Parse a SUMD file.
- `validate(document)` — Validate a SUMD document.


## Project Structure

📄 `project`
📄 `scripts.generate_all_sumd`
📦 `sumd`
📄 `sumd.cli` (8 functions)
📄 `sumd.generator` (19 functions)
📄 `sumd.mcp_server` (5 functions)
📄 `sumd.parser` (9 functions, 4 classes)

## Requirements

- Python >= >=3.10
- click >=8.0- pyyaml >=6.0- toml >=0.10.0

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/oqlos/statement
cd sumd

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 📖 [Full Documentation](https://github.com/oqlos/statement/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/oqlos/statement/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/oqlos/statement/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/oqlos/statement/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](./docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](./docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](./docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](./docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](./docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](./docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](./docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](./docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](./CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->