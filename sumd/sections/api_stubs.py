"""sumd.sections.api_stubs — ApiStubsSection.

Renders OpenAPI endpoints as Python-like typed stubs for LLM orientation.
LLM sees function signatures and HTTP method/path without reading full openapi.yaml.
"""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_api_stubs(openapi: dict) -> list[str]:
    """Render OpenAPI endpoints as Python-like typed stubs for LLM orientation."""
    endpoints = openapi.get("endpoints", [])
    schemas = openapi.get("schemas", [])
    if not endpoints:
        return []
    L: list[str] = []
    a = L.append
    a("## API Stubs")
    a("")
    title = openapi.get("title", "")
    version = openapi.get("version", "")
    if title:
        a(f"*{title} v{version} — auto-generated stubs from `openapi.yaml`.*")
        a("")

    # Group by tag for structure
    by_tag: dict[str, list[dict]] = {}
    for ep in endpoints:
        tag = ep["tags"][0] if ep.get("tags") else "default"
        by_tag.setdefault(tag, []).append(ep)

    a("```python markpact:openapi path=openapi.yaml")
    for tag, eps in by_tag.items():
        a(f"# {tag}")
        for ep in eps:
            op_id = (
                ep.get("operationId")
                or f"{ep['method'].lower()}_{ep['path'].replace('/', '_').strip('_')}"
            )
            summary = f"  # {ep['summary']}" if ep.get("summary") else ""
            a(f"def {op_id}() -> Response:{summary}")
            a(f'    "{ep["method"]} {ep["path"]}"')
        a("")
    a("```")
    a("")
    if schemas:
        a("**Schemas**: " + ", ".join(f"`{s}`" for s in schemas))
        a("")
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class ApiStubsSection:
    name = "api_stubs"
    level = 2
    profiles = frozenset({"rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(ctx.openapi.get("endpoints"))

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_api_stubs(ctx.openapi)


assert isinstance(ApiStubsSection(), Section)
