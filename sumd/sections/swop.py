"""sumd.sections.swop — SwopSection for SWOP manifest files."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx


def _render_swop_section(swop: dict, raw_sources: bool) -> list[str]:
    """Render SWOP manifest section."""
    L: list[str] = []
    a = L.append

    if not swop.get("contexts"):
        return L

    contexts = swop["contexts"]
    sources = swop.get("sources", [])

    a("## SWOP")
    a("")
    a("SWOP - Bi-directional runtime reconciler and drift-aware state graph for full-stack systems.")
    a("")

    if raw_sources:
        # Render raw YAML files
        for context_name, context_data in sorted(contexts.items()):
            a(f"### Context: `{context_name}`")
            a("")

            for manifest_type in ("commands", "queries", "events"):
                if manifest_type in context_data:
                    manifest = context_data[manifest_type]
                    file_path = manifest["file"]
                    content = manifest["content"]
                    a(f"#### {manifest_type.capitalize()} (`{file_path}`)")
                    a("")
                    a(f"```yaml markpact:swop path={file_path}")
                    a(content)
                    a("```")
                    a("")
    else:
        # Render parsed/structured view
        for context_name, context_data in sorted(contexts.items()):
            a(f"### Context: `{context_name}`")
            a("")

            for manifest_type in ("commands", "queries", "events"):
                if manifest_type in context_data:
                    file_path = context_data[manifest_type]["file"]
                    a(f"- **{manifest_type.capitalize()}**: `{file_path}`")
            a("")

    return L


class SwopSection:
    name = "swop"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.swop.get("contexts"))

    render = call_with_ctx(_render_swop_section, "swop", "raw_sources")


assert isinstance(SwopSection(), Section)
