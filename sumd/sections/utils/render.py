"""Utility factory for common ``render`` patterns.

Usage::

    class MySection:
        render = call_with_ctx(_render_my_section, "attr1", "attr2")
"""

from __future__ import annotations

from typing import Callable

from sumd.sections.base import RenderContext


def call_with_ctx(render_fn: Callable, *attr_names: str):
    """Return a ``render`` method that calls *render_fn* with ctx attributes.

    The returned callable accepts ``(self, ctx)`` so it works when assigned
    as a class attribute (Python binds ``self`` automatically).
    """
    def render(_self: object, ctx: RenderContext) -> list[str]:
        args = [getattr(ctx, name) for name in attr_names]
        return render_fn(*args)
    return render
