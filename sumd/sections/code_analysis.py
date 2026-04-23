"""sumd.sections.code_analysis — CodeAnalysisSection."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_code_analysis(
    project_analysis: list, skip_files: set[str] | None = None
) -> list[str]:
    """Render Code Analysis section, optionally skipping files handled by other sections."""
    skip_files = skip_files or set()
    entries = [
        e
        for e in project_analysis
        if not any(s in e.get("file", "") for s in skip_files)
    ]
    if not entries:
        return []
    L: list[str] = []
    a = L.append
    a("## Code Analysis")
    a("")
    for entry in entries:
        a(f"### `{entry['file']}`")
        a("")
        lang = entry["lang"]
        if lang == "markdown":
            a(entry["content"])
        elif lang == "text":
            a(f"```text markpact:analysis path={entry['file']}")
            a(entry["content"])
            a("```")
        else:
            a(f"```{lang} markpact:analysis path={entry['file']}")
            a(entry["content"])
            a("```")
        a("")
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class CodeAnalysisSection:
    name = "code_analysis"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        # Skip if ALL entries are calls.toon (handled by CallGraphSection)
        non_calls = [
            e for e in ctx.project_analysis if "calls.toon" not in e.get("file", "")
        ]
        return bool(non_calls)

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_code_analysis(ctx.project_analysis, skip_files={"calls.toon"})


assert isinstance(CodeAnalysisSection(), Section)
