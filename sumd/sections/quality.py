"""sumd.sections.quality — QualitySection."""

from __future__ import annotations

from pathlib import Path

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx
from sumd.sections.utils.should_render import has_attr


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_quality_raw(proj_dir: Path, L: list[str]) -> None:
    a = L.append
    pyqual_path = proj_dir / "pyqual.yaml"
    if pyqual_path.exists():
        a("```yaml markpact:pyqual path=pyqual.yaml")
        a(pyqual_path.read_text(encoding="utf-8").rstrip())
        a("```")
        a("")


def _render_quality_parsed(pyqual: dict, L: list[str]) -> None:
    a = L.append
    if pyqual.get("name"):
        a(f"**Pipeline**: `{pyqual['name']}`")
        a("")
    if pyqual.get("metrics"):
        a("### Metrics / Thresholds")
        a("")
        for k, v in pyqual["metrics"].items():
            a(f"- `{k}`: `{v}`")
        a("")
    if pyqual.get("stages"):
        a("### Stages")
        a("")
        for s in pyqual["stages"]:
            opt = " *(optional)*" if s.get("optional") else ""
            a(f"- **{s['name']}**: `{s['tool']}`{opt}")
        a("")
    if pyqual.get("loop"):
        a("### Loop Behavior")
        a("")
        for k, v in pyqual["loop"].items():
            a(f"- `{k}`: `{v}`")
        a("")


def _render_quality(pyqual: dict, proj_dir: Path, raw_sources: bool) -> list[str]:
    if not pyqual:
        return []
    L: list[str] = []
    a = L.append
    a("## Quality Pipeline (`pyqual.yaml`)")
    a("")
    if raw_sources:
        _render_quality_raw(proj_dir, L)
    else:
        _render_quality_parsed(pyqual, L)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class QualitySection:
    name = "quality"
    level = 2
    profiles = frozenset({"light", "rich", "refactor"})

    should_render = has_attr("pyqual")
    render = call_with_ctx(_render_quality, "pyqual", "proj_dir", "raw_sources")


assert isinstance(QualitySection(), Section)
