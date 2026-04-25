"""sumd.sections.call_graph — CallGraphSection.

Renders a summary of the call graph (HUBS table + degree stats) from
calls.toon.yaml in project/, followed by the full embed for LLM reference.

Replaces the raw dump that would otherwise appear in CodeAnalysis.
"""

from __future__ import annotations

import re

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _parse_calls_header(lines: list[str]) -> dict:
    """Parse node/edge/module counts and CC average from header comments."""
    result = {"nodes": 0, "edges": 0, "modules_count": 0, "cc_avg": 0.0}
    for line in lines[:5]:
        if line.startswith("# nodes:"):
            m = re.search(
                r"nodes:\s*(\d+).*edges:\s*(\d+).*modules:\s*(\d+)", line
            )
            if m:
                result["nodes"] = int(m.group(1))
                result["edges"] = int(m.group(2))
                result["modules_count"] = int(m.group(3))
        if line.startswith("# CC"):
            m = re.search(r"CC\u0304=?\s*([\d.]+)", line)
            if m:
                result["cc_avg"] = float(m.group(1))
    return result


def _parse_hub_stat_line(line: str) -> dict | None:
    """Extract CC/in/out/total metrics from a hub stats line, or return None."""
    m = re.search(r"CC=(\d+)\s+in:(\d+)\s+out:(\d+)\s+total:(\d+)", line)
    if not m:
        return None
    return {
        "cc": int(m.group(1)),
        "in": int(m.group(2)),
        "out": int(m.group(3)),
        "total": int(m.group(4)),
    }


def _process_in_hubs_line(line: str, hubs: list, current_hub: dict) -> dict:
    """Process a single indented line while inside the HUBS block."""
    if line.startswith("    "):
        stats = _parse_hub_stat_line(line)
        if stats and current_hub:
            current_hub.update(stats)
    elif line.startswith("  "):
        if current_hub:
            hubs.append(current_hub)
        current_hub = {"name": line.strip()}
    return current_hub


def _parse_calls_hubs(lines: list[str]) -> list[dict]:
    """Parse HUBS section into list of hub dicts."""
    hubs: list[dict] = []
    in_hubs = False
    current_hub: dict = {}
    for line in lines:
        if line.startswith("HUBS["):
            in_hubs = True
            continue
        if in_hubs and line and not line.startswith(" "):
            in_hubs = False
        if in_hubs:
            current_hub = _process_in_hubs_line(line, hubs, current_hub)
    if current_hub:
        hubs.append(current_hub)
    return hubs


def _parse_calls_toon(content: str) -> dict:
    """Parse calls.toon.yaml text into structured dict for rendering."""
    lines = content.splitlines()
    return {
        **_parse_calls_header(lines),
        "hubs": _parse_calls_hubs(lines),
        "modules": [],
    }


def _render_call_graph(project_analysis: list) -> list[str]:
    """Render call graph summary from calls.toon.yaml in project_analysis."""
    calls_entry = next(
        (e for e in project_analysis if "calls.toon" in e.get("file", "")), None
    )
    if not calls_entry:
        return []

    data = _parse_calls_toon(calls_entry["content"])
    if not data["hubs"]:
        return []

    L: list[str] = []
    a = L.append
    a("## Call Graph")
    a("")
    a(
        f"*{data['nodes']} nodes · {data['edges']} edges · {data['modules_count']} modules · CC\u0304={data['cc_avg']}*"
    )
    a("")

    # Top hubs table (top 8 by total degree)
    top_hubs = sorted(data["hubs"], key=lambda h: h.get("total", 0), reverse=True)[:8]
    a("### Hubs (by degree)")
    a("")
    a("| Function | CC | in | out | total |")
    a("|----------|----|----|-----|-------|")
    for hub in top_hubs:
        name = hub["name"].split(".")[-1]  # short name
        module = ".".join(hub["name"].split(".")[:-1])
        cc_flag = " ⚠" if hub.get("cc", 0) >= 10 else ""
        a(
            f"| `{name}` *(in {module})* | {hub.get('cc', 0)}{cc_flag} | {hub.get('in', 0)} | {hub.get('out', 0)} | **{hub.get('total', 0)}** |"
        )
    a("")

    # Full embed for LLM reference under markpact tag
    rel = calls_entry["file"]
    a(f"```toon markpact:analysis path={rel}")
    a(calls_entry["content"].rstrip())
    a("```")
    a("")
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class CallGraphSection:
    name = "call_graph"
    level = 2
    profiles = frozenset({"rich", "refactor"})

    def should_render(self, ctx: RenderContext) -> bool:
        return any("calls.toon" in e.get("file", "") for e in ctx.project_analysis)

    render = call_with_ctx(_render_call_graph, "project_analysis")


assert isinstance(CallGraphSection(), Section)
