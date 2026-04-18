# SUMD — Structured Unified Markdown Descriptor

SUMD to semantyczny format opisu projektu w Markdown. Definiuje intencje, strukturę, punkty wejścia i model mentalny systemu zarówno dla ludzi jak i dla LLM.

## Metadata

- **version**: 0.1.7
- **name**: sumd
- **stack**: Python, Click, PyYAML, TOML, MCP
- **ecosystem**: SUMD + DOQL + testql + taskfile

## Intent

SUMD to semantyczny format opisu projektu w Markdown. Definiuje intencje, strukturę, punkty wejścia i model mentalny systemu zarówno dla ludzi jak i dla LLM.

## Architecture

Projekt jest częścią ekosystemu OQL:

```
SUMD (opis) → DOQL (dane) → taskfile (automatyzacja) → testql (weryfikacja)
```

## Interfaces

- CLI: `sumd validate SUMD.md` — waliduj dokument
- CLI: `sumd export SUMD.md --format json` — eksportuj do JSON/YAML/TOML
- CLI: `sumd generate sumd.json --output SUMD.md` — generuj z JSON
- CLI: `sumd info SUMD.md` — informacje o dokumencie
- MCP: `sumd-mcp` — serwer MCP do odpytywania projektu
- Python API: `from sumd import parse_file, validate`

## Workflows

```yaml
tasks:
  build:
    cmds:
      - pip install -e .
  test:
    cmds:
      - pytest tests/ -v
  validate:
    cmds:
      - sumd validate SUMD.md
  export:
    cmds:
      - sumd export SUMD.md --format json --output sumd.json
  mcp:
    cmds:
      - sumd-mcp
```

## Configuration

```yaml
project:
  name: sumd
  version: 0.1.7
  env: local
```

## Dependencies

- `click>=8.0`
- `pyyaml>=6.0`
- `toml>=0.10.0`
- `mcp>=1.0.0`

## Deployment

```bash
# Instalacja
pip install sumd

# Instalacja deweloperska
pip install -e .
```
