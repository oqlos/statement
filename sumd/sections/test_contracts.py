"""sumd.sections.test_contracts — TestContractsSection.

Renders testql scenarios as contract signatures: endpoint + key assertions.
LLM sees what the system guarantees without reading full scenario files.
"""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx
from sumd.sections.utils.should_render import has_attr


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_scenario_contract(sc: dict, a) -> None:
    """Append contract lines for a single scenario to the output via *a*."""
    a(f"**`{sc['name']}`**")
    if sc.get("endpoints"):
        for ep in sc["endpoints"][:3]:
            status = ep.get("status", "")
            op = f" — `{ep['operationId']}`" if ep.get("operationId") else ""
            a(f"- `{ep['method']} {ep['path']}` → `{status}`{op}")
    if sc.get("asserts"):
        for ass in sc["asserts"][:3]:
            a(f"- assert `{ass['field']} {ass['op']} {ass['expected']}`")
    if sc.get("performance"):
        for p in sc["performance"][:2]:
            a(f"- perf `{p['metric']} < {p['threshold']}`")
    if sc.get("detectors"):
        a(f"- detectors: {sc['detectors']}")
    a("")


def _render_test_contracts(scenarios: list) -> list[str]:
    """Render test scenarios as contract signatures — endpoint + key assertions."""
    if not scenarios:
        return []
    L: list[str] = []
    a = L.append
    a("## Test Contracts")
    a("")
    a("*Scenarios as contract signatures — what the system guarantees.*")
    a("")

    # Group by type
    by_type: dict[str, list[dict]] = {}
    for sc in scenarios:
        sc_type = sc.get("type", "unknown")
        by_type.setdefault(sc_type, []).append(sc)

    for sc_type, scs in sorted(by_type.items()):
        a(f"### {sc_type.title()} ({len(scs)})")
        a("")
        for sc in scs:
            _render_scenario_contract(sc, a)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class TestContractsSection:
    name = "test_contracts"
    level = 2
    profiles = frozenset({"rich"})

    should_render = has_attr("scenarios")
    render = call_with_ctx(_render_test_contracts, "scenarios")


assert isinstance(TestContractsSection(), Section)
