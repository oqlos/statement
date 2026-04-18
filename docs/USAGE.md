# SUMD — dokumentacja użytkowania

## Przegląd ekosystemu

SUMD jest częścią trójwarstwowego ekosystemu narzędzi:

| Warstwa | Pakiet | Rola |
|---------|--------|------|
| Opis | `sumd` | Strukturalny opis projektu dla ludzi i LLM |
| Dane | `doql` | Deklaratywne zapytania i transformacje danych |
| Automatyzacja | `taskfile` | Task runner, deploy, CI/CD |
| Testy | `testql` | Testowanie interfejsów API, GUI, CLI |

---

## Instalacja

```bash
pip install sumd
```

---

## Komendy CLI

### `sumd scan` — generowanie SUMD.md

Skanuje workspace, wykrywa projekty Python (po obecności `pyproject.toml`) i generuje `SUMD.md`.

```bash
sumd scan .                    # pomiń projekty z istniejącym plikiem
sumd scan . --fix              # nadpisz istniejące pliki
sumd scan . --fix --no-raw     # tryb strukturalny zamiast surowych code bloków
sumd scan . --fix --report summary.json
sumd scan . --fix --analyze    # + uruchom code2llm, redup, vallm
sumd scan . --fix --analyze --tools code2llm,redup
```

**Co jest osadzane w SUMD.md:**

| Źródło | Sposób osadzenia | markpact kind |
|--------|-----------------|---------------|
| `pyproject.toml` | parsowany (wersja, deps, entry points) | — |
| `Taskfile.yml` | surowy YAML | `markpact:file` |
| `openapi.yaml` | pełna spec + endpointy jako sekcje | `markpact:file` |
| `testql-scenarios/**/*.testql.toon.yaml` | surowy toon | `markpact:file` |
| `app.doql.less` / `.css` | surowy Less/CSS | `markpact:file` |
| `pyqual.yaml` | surowy YAML | `markpact:file` |
| `goal.yaml` | sekcja intent | — |
| `.env.example` | lista zmiennych | — |
| `Dockerfile` / `docker-compose.*.yml` | lista plików | — |
| `src/**/*.py` moduły | lista nazw | — |
| `project/analysis.toon.yaml` | statyczna analiza kodu (CC, pipelines) | `markpact:file` |
| `project/project.toon.yaml` | topologia projektu | `markpact:file` |
| `project/evolution.toon.yaml` | historia commitów | `markpact:file` |
| `project/map.toon.yaml` | mapa zależności modułów | `markpact:file` |
| `project/duplication.toon.yaml` | raport duplikacji kodu | `markpact:file` |
| `project/validation.toon.yaml` | wyniki walidacji vallm | `markpact:file` |
| `project/compact_flow.mmd` | diagram przepływu wywołań | `markpact:file` |
| `project/calls.mmd` | pełny call graph | `markpact:file` |
| `project/flow.mmd` | diagram przepływu | `markpact:file` |
| `project/context.md` | analiza architektury (code2llm) | inline markdown |
| `project/README.md` | opis wyników analizy | inline markdown |
| `project/prompt.txt` | prompt użyty przez code2llm | `markpact:file` |

**Nie osadzane:** `*.png`, `index.html`, `refactor-progress.txt`, `project/testql-scenarios/`.

Folder `project/` jest generowany przez `sumd analyze` (narzędzia `code2llm`, `redup`, `vallm`).

---

### `sumd lint` — walidacja SUMD.md

```bash
sumd lint SUMD.md
sumd lint --workspace .
sumd lint --workspace . --json
```

Walidatory sprawdzają:

- **Markdown**: H1, wymagane sekcje `## Metadata/Intent/Architecture/Workflows/Dependencies/Deployment`, pola `name`+`version`, niezamknięte fenced blocki
- **`toon`**: obecność nagłówków sekcji (`CONFIG[...]`, `API[...]` itp.)
- **`yaml`**: poprawność parsowania przez PyYAML
- **`mermaid`**: prawidłowy typ diagramu
- **`less`/`css`**: zbilansowane nawiasy klamrowe
- **`bash`**: brak placeholderów `<YOUR_...>` i TODO
- **`text`** (deps): poprawny format nazw pakietów pip

---

### `sumd scaffold` — generowanie szkieletów testql

#### Dlaczego `sumd scan` nie generuje testql automatycznie?

`sumd scan` tylko **czyta** istniejące pliki testql i osadza je w SUMD.md.
Nie może ich generować, ponieważ scenariusze testql kodują **oczekiwane zachowanie biznesowe** —
asercje, warunki brzegowe, logikę domenową — której sumd nie zna.

`sumd scaffold` generuje **szkielet strukturalny** (endpointy, nazwy plików, konfigurację bazy)
ze specyfikacji OpenAPI. Asercje i logika domenowa muszą być uzupełnione przez człowieka lub LLM.

```bash
sumd scaffold ./my-project                          # wszystkie scenariusze z openapi.yaml
sumd scaffold ./my-project --type smoke             # tylko smoke testy (GET /health itp.)
sumd scaffold ./my-project --type crud              # scenariusze per zasób
sumd scaffold ./my-project --force                  # nadpisz istniejące pliki
sumd scaffold ./my-project --output ./my-scenarios/ # inny katalog wyjściowy
```

**Przepływ pracy scaffold → scan → testql:**

```bash
# 1. Wygeneruj szkielety ze spec OpenAPI
sumd scaffold ./oqlos
# → tworzy oqlos/testql-scenarios/smoke-health.testql.toon.yaml
# → tworzy oqlos/testql-scenarios/api-execution.testql.toon.yaml
# → ...

# 2. Uzupełnij asercje (każdy plik ma sekcję # ASSERT[0] z TODO)
vim oqlos/testql-scenarios/api-execution.testql.toon.yaml

# 3. Osadź w SUMD.md
sumd scan . --fix

# 4. Waliduj
sumd lint --workspace .

# 5. Uruchom testy
testql run oqlos/testql-scenarios/
```

**Przykład wygenerowanego pliku** (`api-execution.testql.toon.yaml`):

```toon
# SCENARIO: api-execution.testql.toon.yaml — api execution
# TYPE: api
# VERSION: 1.0
# GENERATED: true

# ── Konfiguracja ──────────────────────────────────────
CONFIG[1]{key, value}:
  base_path,  http://localhost:8101

# ── Wywołania API ─────────────────────────────────────
API[3]{method, endpoint, status}:
  POST,   /api/v1/execution/run,     200
  GET,    /api/v1/execution/status,  200
  DELETE, /api/v1/execution/{id},    200
# ── Asercje ───────────────────────────────────────────
# ASSERT[0]{field, op, expected}:
#   TODO: fill in assertions
```

---

### `sumd map` — generowanie project/map.toon.yaml

Generuje `project/map.toon.yaml` — mapę kodu w formacie toon (identyczną z wyjściem `code2llm map`), bez potrzeby instalowania zewnętrznych narzędzi.

```bash
sumd map ./my-project            # → project/map.toon.yaml
sumd map ./my-project --force    # nadpisz istniejący plik
sumd map ./my-project --stdout   # wydrukuj na stdout
```

Zawartość wygenerowanego pliku:

```toon
# oqlos | 128f 19993L | python:124,shell:2,css:1,less:1 | 2026-04-18
# stats: 287 func | 42 cls | 128 mod | CC̄=5.2 | critical:12 | cycles:0
# alerts[5]: CC interpret=55; fan-out run=31; ...
# hotspots[5]: interpret fan=31; parse fan=28; ...
M[128]:
  oqlos/core/interpreter.py,1243
  oqlos/core/executor.py,512
  ...
D:
  oqlos/core/interpreter.py:
    e: Interpreter,run,parse,...
    Interpreter: __init__(3),run(2),...
    run(script;context)
```

Plik `project/map.toon.yaml` jest automatycznie osadzany w SUMD.md przy `sumd scan --fix`.

Relacja do `code2llm`:
- `sumd map` — wbudowane, zawsze dostępne, analizuje statycznie przez `ast` + `radon`
- `sumd analyze --tools code2llm` — zewnętrzne narzędzie, wymaga instalacji, generuje więcej metryk

---

### `sumd analyze` — analiza statyczna kodu

Uruchamia narzędzia `code2llm`, `redup`, `vallm` i zapisuje wyniki w `project/`.
Pliki z `project/` są automatycznie osadzane w SUMD.md przy kolejnym `sumd scan --fix`.

```bash
sumd analyze ./my-project
sumd analyze ./my-project --tools code2llm,redup
sumd analyze ./my-project --force    # wymuś reinstalację narzędzi
```

**Pełna lista plików generowanych w `project/`:**

| Plik | Generuje | Polecenie / flaga |
|------|---------|-------------------|
| `analysis.toon.yaml` | `code2llm` | `-f toon` |
| `evolution.toon.yaml` | `code2llm` | `-f evolution` |
| `map.toon.yaml` | `sumd map` lub `code2llm` | `sumd map` / `-f map` |
| `context.md` | `code2llm` | `-f context` |
| `calls.mmd` | `code2llm` | `-f calls` |
| `flow.mmd`, `compact_flow.mmd`, `calls.mmd` | `code2llm` | `-f mermaid --no-png` |
| `duplication.toon.yaml` | `redup` | `redup scan --format toon` |
| `validation.toon.yaml` | `vallm` | `vallm batch --format toon` |

**Nie osadzane do SUMD.md:** `*.png`, `index.html`, `refactor-progress.txt`.

| Narzędzie | Co robi | Generuje |
|-----------|---------|----------|
| `code2llm` | Analiza architektury, modułów, call graph | `context.md`, `analysis.toon.yaml`, `evolution.toon.yaml`, `*.mmd` |
| `redup` | Wykrywanie duplikacji kodu | `duplication.toon.yaml` |
| `vallm` | Walidacja kodu przez LLM | `validation.toon.yaml` |

---

## Dlaczego SUMD.md nie wystarczy do odtworzenia projektu przez LLM?

SUMD.md zawiera **specyfikację i kontekst**, ale nie **kod źródłowy**.

### ✅ Co jest (pozwala odtworzyć strukturę):

- Pełna specyfikacja OpenAPI (endpointy, schematy)
- Scenariusze testql (kontrakt zachowania API)
- Taskfile (workflow CI/CD)
- Zależności Python
- Architektura modułów, call-graph (`project/`)
- Historia commitów, topologia projektu

### ❌ Czego brakuje (implementacja):

| Brak | Dlaczego to problem |
|------|---------------------|
| **Kod źródłowy `.py`** | Tylko nazwy modułów — bez ciał funkcji |
| **Docstringi / sygnatury typów** | `analysis.toon.yaml` podaje CC i nazwy, nie kod |
| **Testy jednostkowe** (`tests/`) | Tylko scenariusze testql, nie pytest |
| **Logika interpreter/parser** | Złożone algorytmy nieosiągalne z diagramów |
| **Modele danych** | Brak definicji Pydantic/dataclass |
| **Komentarze w kodzie** | Tracone przy listowaniu modułów |

### Czego brakuje w specyfikacji SUMD:

1. **Sekcja `## Source`** — osadzenie kluczowych modułów źródłowych (top N wg CC z `analysis.toon.yaml`)
2. **`markpact:test` dla `tests/`** — testy jednostkowe jako kontrakt niższego poziomu
3. **Sygnatury publicznego API** — `__all__`, stubs typów, definicje Pydantic schemas
4. **`markpact:file` dla `.env.example`** — teraz tylko listowany, nie osadzony jako blok kodu
5. **Diagram sekwencji** — brak sequence diagram dla kluczowych przepływów (jest tylko call-graph)
6. **Pinowane wersje zależności** — `requirements.txt` z pełnymi pinami

---

## Format `.testql.toon.yaml`

```toon
# SCENARIO: nazwa.testql.toon.yaml — opis
# TYPE: api|smoke|crud|e2e|gui
# VERSION: 1.0
# GENERATED: true|false

CONFIG[N]{key, value}:
  base_path,  http://localhost:8080

API[N]{method, endpoint, status}:
  GET,    /api/v1/users,      200
  POST,   /api/v1/users,      201  # create - create new user
  DELETE, /api/v1/users/{id}, 204

ASSERT[N]{field, op, expected}:
  body.items, !=, null
  body.count, >=, 0

PERFORMANCE[N]{metric, threshold}:
  response_time, <500ms
```

Sekcje opcjonalne: `NAVIGATE[N]` (GUI), `GUI[N]` (akcje przeglądarki), `SETUP[N]`, `TEARDOWN[N]`.

---

## Python API

```python
from sumd import parse, parse_file
from sumd.parser import validate_sumd_file
from pathlib import Path

# Parsuj SUMD.md
doc = parse_file("SUMD.md")
print(doc.project_name, doc.description)
for s in doc.sections:
    print(s.name, s.type.value)

# Waliduj plik
result = validate_sumd_file(Path("SUMD.md"))
# result = {"source": "SUMD.md", "markdown": [...], "codeblocks": [...], "ok": True}
if not result["ok"]:
    for issue in result["markdown"] + result["codeblocks"]:
        print(issue)
```
