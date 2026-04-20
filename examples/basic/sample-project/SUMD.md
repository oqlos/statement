# my-api

Sample REST API project for SUMD demo

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Intent](#intent)

## Metadata

- **name**: `my-api`
- **version**: `0.1.0`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **openapi_title**: My API v0.1.0
- **generated_from**: pyproject.toml, Taskfile.yml, openapi(5 ep), project/(1 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

## Workflows

### Taskfile Tasks (`Taskfile.yml`)

```yaml markpact:taskfile path=Taskfile.yml
version: "3"
tasks:
  install:
    desc: Install the project
    cmds:
      - pip install -e .
  run:
    desc: Start the development server
    cmds:
      - uvicorn my_api.main:app --reload
```

## Dependencies

### Runtime

```text markpact:deps python
fastapi
uvicorn
```

## Deployment

```bash markpact:run
pip install my-api

# development install
pip install -e .[dev]
```

## Intent

Sample REST API project for SUMD demo
