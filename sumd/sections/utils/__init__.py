"""sumd.sections.utils — shared utilities for section renderers.

Factories for common ``should_render`` and ``render`` patterns so section
classes stay DRY.
"""

from __future__ import annotations

from sumd.sections.utils.render import call_with_ctx
from sumd.sections.utils.should_render import always, has_attr

__all__ = ["always", "has_attr", "call_with_ctx"]
