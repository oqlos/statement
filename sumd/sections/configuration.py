"""sumd.sections.configuration — ConfigurationSection."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_configuration_section(name: str, version: str) -> list[str]:
    return [
        "## Configuration",
        "",
        "```yaml",
        "project:",
        f"  name: {name}",
        f"  version: {version}",
        "  env: local",
        "```",
        "",
    ]


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class ConfigurationSection:
    name = "configuration"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return True

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_configuration_section(ctx.name, ctx.version)


assert isinstance(ConfigurationSection(), Section)
