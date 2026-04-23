"""sumd.sections.extras — ExtrasSection (Makefile + package.json scripts)."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_makefile_targets(makefile: list, a) -> None:
    """Append Makefile targets section via *a*."""
    a("## Makefile Targets")
    a("")
    for t in makefile:
        desc = f" — {t['desc']}" if t["desc"] else ""
        a(f"- `{t['target']}`{desc}")
    a("")


def _render_pkg_json_scripts(pkg_json: dict, a) -> None:
    """Append Node.js scripts section via *a*."""
    a("## Node.js Scripts (`package.json`)")
    a("")
    if pkg_json.get("description"):
        a(pkg_json["description"])
        a("")
    for script, cmd in pkg_json["scripts"].items():
        a(f"- `npm run {script}` — `{cmd}`")
    a("")
    if pkg_json.get("dependencies"):
        a(
            "**Runtime deps**: "
            + ", ".join(f"`{d}`" for d in pkg_json["dependencies"][:15])
        )
        a("")
    if pkg_json.get("engines"):
        for eng, ver in pkg_json["engines"].items():
            a(f"- **{eng}**: `{ver}`")
        a("")


def _render_extras(makefile: list, pkg_json: dict) -> list[str]:
    L: list[str] = []
    a = L.append
    if makefile:
        _render_makefile_targets(makefile, a)
    if pkg_json.get("scripts"):
        _render_pkg_json_scripts(pkg_json, a)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class ExtrasSection:
    name = "extras"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.makefile or ctx.pkg_json.get("scripts"))

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_extras(ctx.makefile, ctx.pkg_json)


assert isinstance(ExtrasSection(), Section)
