"""sumd.sections.deployment — DeploymentSection."""

from __future__ import annotations

from sumd.sections.base import RenderContext, Section
from sumd.sections.utils.render import call_with_ctx
from sumd.sections.utils.should_render import always


# ---------------------------------------------------------------------------
# Private renderers (moved from renderer.py)
# ---------------------------------------------------------------------------


def _render_deployment_install(pkg_json: dict, name: str, L: list[str]) -> None:
    a = L.append
    if pkg_json.get("name"):
        a("```bash markpact:run")
        a(f"npm install {pkg_json['name']}")
        a("```")
    else:
        a("```bash markpact:run")
        a(f"pip install {name}")
        a("")
        a("# development install")
        a("pip install -e .[dev]")
        a("```")
    a("")


def _render_deployment_reqs(reqs: list, L: list[str]) -> None:
    if not reqs:
        return
    a = L.append
    a("### Requirements Files")
    a("")
    for r in reqs:
        a(f"#### `{r['file']}`")
        a("")
        for dep in r["deps"][:20]:
            a(f"- `{dep}`")
        if len(r["deps"]) > 20:
            a(f"- *(+{len(r['deps']) - 20} more)*")
        a("")


def _render_dockerfile_info(dockerfile: dict, a) -> None:
    """Append Dockerfile section lines to output via *a*."""
    a("### Docker")
    a("")
    a(f"- **base image**: `{dockerfile['from']}`")
    if dockerfile["ports"]:
        a(f"- **expose**: {', '.join(f'`{p}`' for p in dockerfile['ports'])}")
    if dockerfile["entrypoint"]:
        a(f"- **entrypoint**: `{dockerfile['entrypoint']}`")
    if dockerfile["labels"]:
        for k, v in dockerfile["labels"].items():
            a(f"- **label** `{k}`: {v}")
    a("")


def _render_deployment_docker(dockerfile: dict, compose: dict, L: list[str]) -> None:
    a = L.append
    if dockerfile:
        _render_dockerfile_info(dockerfile, a)
    if compose.get("services"):
        a(f"### Docker Compose (`{compose['file']}`)")
        a("")
        for svc in compose["services"]:
            ports_str = (
                ", ".join(f"`{p}`" for p in svc["ports"]) if svc["ports"] else ""
            )
            image_str = f" image=`{svc['image']}`" if svc["image"] else ""
            a(
                f"- **{svc['name']}**{image_str}"
                + (f" ports: {ports_str}" if ports_str else "")
            )
        a("")


def _render_deployment(
    pkg_json: dict, name: str, reqs: list, dockerfile: dict, compose: dict
) -> list[str]:
    L: list[str] = []
    a = L.append
    a("## Deployment")
    a("")
    _render_deployment_install(pkg_json, name, L)
    _render_deployment_reqs(reqs, L)
    _render_deployment_docker(dockerfile, compose, L)
    return L


# ---------------------------------------------------------------------------
# Section class
# ---------------------------------------------------------------------------


class DeploymentSection:
    name = "deployment"
    level = 2
    profiles = frozenset({"light", "rich"})

    should_render = always
    render = call_with_ctx(
        _render_deployment, "pkg_json", "name", "reqs", "dockerfile", "compose"
    )


assert isinstance(DeploymentSection(), Section)
