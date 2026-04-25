"""sumd.sections.configuration — ConfigurationSection."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx
from sumd.sections.utils.should_render import always


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

    should_render = always
    render = call_with_ctx(_render_configuration_section, "name", "version")


assert isinstance(ConfigurationSection(), Section)
