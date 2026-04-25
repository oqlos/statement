"""sumd.sections.source_snippets — SourceSnippetsSection.

Renders top-N modules with function/class signatures for LLM orientation.
Gives the model a structural map of the codebase without requiring it
to read full source files.
"""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx
from sumd.sections.utils.should_render import has_attr


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_source_snippets(source_snippets: list, top_n: int = 5) -> list[str]:
    """Render top-N modules with function/class signatures for LLM orientation."""
    if not source_snippets:
        return []
    L: list[str] = []
    a = L.append
    a("## Source Map")
    a("")
    a(
        f"*Top {min(top_n, len(source_snippets))} modules by symbol density — signatures for LLM orientation.*"
    )
    a("")
    for entry in source_snippets[:top_n]:
        a(f"### `{entry['module']}` (`{entry['path']}`)")
        a("")
        a("```python")
        for fn in entry["funcs"]:
            args_str = ", ".join(fn["args"])
            cc_flag = " ⚠" if fn["cc"] >= 10 else ""
            a(
                f"def {fn['name']}({args_str})  # CC={fn['cc']}, fan={fn['fan']}{cc_flag}"
            )
        for cls in entry["classes"]:
            doc = cls["doc"]  # already formatted as "  # ..." or ""
            a(f"class {cls['name']}:{doc}")
            for m in cls["methods"]:
                args_str = ", ".join(m["args"])
                cc_flag = " ⚠" if m["cc"] >= 10 else ""
                a(f"    def {m['name']}({args_str})  # CC={m['cc']}{cc_flag}")
        a("```")
        a("")
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class SourceSnippetsSection:
    name = "source_snippets"
    level = 2
    profiles = frozenset({"rich"})

    should_render = has_attr("source_snippets")
    render = call_with_ctx(_render_source_snippets, "source_snippets")


assert isinstance(SourceSnippetsSection(), Section)
