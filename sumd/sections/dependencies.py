"""sumd.sections.dependencies — DependenciesSection."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_deps_runtime(deps: list, node_deps: list, L: list[str]) -> None:
    a = L.append
    if deps:
        a("### Runtime")
        a("")
        a("```text markpact:deps python")
        for dep in deps:
            a(dep)
        a("```")
        a("")
    elif node_deps:
        a("### Runtime (Node.js)")
        a("")
        a("```text markpact:deps node")
        for dep in node_deps[:30]:
            a(dep)
        if len(node_deps) > 30:
            a(f"# (+{len(node_deps) - 30} more)")
        a("```")
        a("")
    else:
        a("### Runtime")
        a("")
        a("*(see pyproject.toml)*")
        a("")


def _render_deps_dev(dev_deps: list, node_dev: list, L: list[str]) -> None:
    a = L.append
    if dev_deps:
        a("### Development")
        a("")
        a("```text markpact:deps python scope=dev")
        for dep in dev_deps:
            a(dep)
        a("```")
        a("")
    elif node_dev:
        a("### Development (Node.js)")
        a("")
        a("```text markpact:deps node scope=dev")
        for dep in node_dev[:20]:
            a(dep)
        if len(node_dev) > 20:
            a(f"# (+{len(node_dev) - 20} more)")
        a("```")
        a("")


def _render_dependencies(
    deps: list, dev_deps: list, pkg_json: dict | None = None
) -> list[str]:
    pkg_json = pkg_json or {}
    L: list[str] = []
    a = L.append
    a("## Dependencies")
    a("")
    _render_deps_runtime(deps, pkg_json.get("dependencies", []), L)
    _render_deps_dev(dev_deps, pkg_json.get("devDependencies", []), L)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class DependenciesSection:
    name = "dependencies"
    level = 2
    profiles = frozenset({"light", "rich"})

    def should_render(self, ctx: RenderContext) -> bool:
        return bool(
            ctx.deps
            or ctx.dev_deps
            or ctx.pkg_json.get("dependencies")
            or ctx.pkg_json.get("devDependencies")
        )

    def render(self, ctx: RenderContext) -> list[str]:
        return _render_dependencies(ctx.deps, ctx.dev_deps, ctx.pkg_json)


assert isinstance(DependenciesSection(), Section)
