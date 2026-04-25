"""Utility factories for common ``should_render`` patterns.

Usage::

    class MySection:
        should_render = always
        # or
        should_render = has_attr("my_data")
"""

from __future__ import annotations

from sumd.sections.base import RenderContext


def always(_self: object, _ctx: RenderContext) -> bool:
    """Always render the section."""
    return True


def has_attr(attr: str):
    """Return a ``should_render`` that checks ``bool(ctx.<attr>)``."""
    def should_render(_self: object, ctx: RenderContext) -> bool:
        return bool(getattr(ctx, attr))
    return should_render
