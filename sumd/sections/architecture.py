"""sumd.sections.architecture — ArchitectureSection."""

from __future__ import annotations

from pathlib import Path

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx
from sumd.sections.utils.should_render import always


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_architecture_doql_section(
    doql: dict, proj_dir: Path, raw_sources: bool, L: list[str]
) -> None:
    a = L.append
    doql_sources = ", ".join(f"`{s}`" for s in doql.get("sources", ["app.doql.less"]))
    a(f"### DOQL Application Declaration ({doql_sources})")
    a("")
    if raw_sources:
        for fname in doql.get("sources", ["app.doql.less"]):
            fpath = proj_dir / fname
            if fpath.exists():
                lang = "less" if fname.endswith(".less") else "css"
                a(f"```{lang} markpact:doql path={fname}")
                a(fpath.read_text(encoding="utf-8").rstrip())
                a("```")
                a("")
    else:
        _render_architecture_doql_parsed(doql, L)


def _render_architecture_modules(modules: list[str], name: str, L: list[str]) -> None:
    a = L.append
    a("### Source Modules")
    a("")
    for mod in modules:
        a(f"- `{name}.{mod}`")
    a("")


def _render_doql_app(doql: dict, L: list[str]) -> None:
    if not doql.get("app"):
        return
    a = L.append
    a("```less")
    a("app {")
    for k, v in doql["app"].items():
        a(f"  {k}: {v};")
    a("}")
    a("```")
    a("")


def _render_doql_entities(doql: dict, L: list[str]) -> None:
    if not doql.get("entities"):
        return
    a = L.append
    a("### DOQL Data Model (`entity`)")
    a("")
    for ent in doql["entities"]:
        attrs_str = ""
        if ent.get("attrs"):
            attrs_str = " — " + ", ".join(
                f"`{k}: {v}`" for k, v in ent["attrs"].items()
            )
        page_str = f" page=`{ent['page']}`" if ent.get("page") else ""
        a(f"- `entity[{ent['name']}]`{page_str}{attrs_str}")
    a("")


def _render_doql_interfaces(doql: dict, L: list[str]) -> None:
    if not doql.get("interfaces"):
        return
    a = L.append
    a("### DOQL Interfaces")
    a("")
    for iface in list(doql["interfaces"]):
        sel = iface.get("selector", "")
        attrs = ", ".join(
            f"{k}: {v}" for k, v in iface.items() if k not in ("selector", "page")
        )
        page_str = f" page=`{iface['page']}`" if iface.get("page") else ""
        a(f"- `interface[{sel}]`{page_str} — {attrs}")
    a("")


def _render_doql_integrations(doql: dict, L: list[str]) -> None:
    if not doql.get("integrations"):
        return
    a = L.append
    a("### DOQL Integrations")
    a("")
    for intg in list(doql["integrations"]):
        sel = intg.get("selector", "")
        attrs = ", ".join(f"{k}: {v}" for k, v in intg.items() if k != "selector")
        a(f"- `integration[{sel}]` — {attrs}")
    a("")


def _render_architecture_doql_parsed(doql: dict, L: list[str]) -> None:
    """Render parsed DOQL blocks into L (mutates in place)."""
    _render_doql_app(doql, L)
    _render_doql_entities(doql, L)
    _render_doql_interfaces(doql, L)
    _render_doql_integrations(doql, L)


def _render_architecture(
    doql: dict, modules: list[str], name: str, proj_dir: Path, raw_sources: bool
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Architecture")
    a("")
    a("```")
    a(
        "SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)"
    )
    a("```")
    a("")
    if (
        doql.get("app")
        or doql.get("entities")
        or doql.get("interfaces")
        or doql.get("workflows")
    ):
        _render_architecture_doql_section(doql, proj_dir, raw_sources, L)
    if modules:
        _render_architecture_modules(modules, name, L)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class ArchitectureSection:
    name = "architecture"
    level = 2
    profiles = frozenset({"minimal", "light", "rich"})

    should_render = always
    render = call_with_ctx(
        _render_architecture, "doql", "modules", "name", "proj_dir", "raw_sources"
    )


assert isinstance(ArchitectureSection(), Section)

