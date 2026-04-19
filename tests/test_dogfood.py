"""Integration (dogfood) tests — scan the sumd project with its own CLI.

These tests verify the full pipeline end-to-end: CLI invocation → file generation.
They catch regressions that unit tests cannot: e.g. sumd failing to scan itself
after a refactor, profile rendering crashes, missing section sections, etc.

Tests use a *temporary copy* of the project directory so they do not mutate
the real SUMD.md / SUMR.md tracked in git.
"""

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SUMD_BIN = PROJECT_ROOT / ".venv" / "bin" / "sumd"
SUMR_BIN = PROJECT_ROOT / ".venv" / "bin" / "sumr"

# Skip the whole module if the binary is not installed (fresh clone before venv setup)
pytestmark = pytest.mark.skipif(
    not SUMD_BIN.exists(),
    reason="sumd binary not found in .venv — run: scripts/bootstrap.sh",
)


def _run(cmd: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


@pytest.fixture(scope="module")
def project_copy(tmp_path_factory):
    """Shallow copy of the project — only source files, no .venv / .git / build."""
    dst = tmp_path_factory.mktemp("sumd_dogfood")
    _IGNORE = shutil.ignore_patterns(
        ".venv", ".git", ".sumd-tools", "dist", "*.egg-info",
        "__pycache__", ".coverage", "coverage.json", "test-results.json",
        "report.html", "*.pyc",
    )
    shutil.copytree(str(PROJECT_ROOT), str(dst), ignore=_IGNORE, dirs_exist_ok=True)
    return dst


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_sumd_scans_itself(project_copy):
    """sumd scan . --fix --profile rich must exit 0 and produce a valid SUMD.md."""
    result = _run(
        [str(SUMD_BIN), "scan", ".", "--fix", "--profile", "rich"],
        cwd=project_copy,
    )
    assert result.returncode == 0, (
        f"sumd scan failed (rc={result.returncode}):\n"
        f"STDOUT:\n{result.stdout[-2000:]}\n"
        f"STDERR:\n{result.stderr[-2000:]}"
    )
    sumd_md = project_copy / "SUMD.md"
    assert sumd_md.exists(), "SUMD.md was not created"
    content = sumd_md.read_text()
    assert "## Metadata" in content, "Missing ## Metadata section"
    assert "sumd" in content.lower(), "SUMD.md does not mention the project"


@pytest.mark.parametrize("profile", ["minimal", "light", "rich"])
def test_sumd_scans_all_profiles(project_copy, profile):
    """Every profile must exit 0 and produce SUMD.md."""
    result = _run(
        [str(SUMD_BIN), "scan", ".", "--fix", "--profile", profile],
        cwd=project_copy,
    )
    assert result.returncode == 0, (
        f"sumd scan --profile {profile} failed (rc={result.returncode}):\n"
        f"STDOUT:\n{result.stdout[-2000:]}\n"
        f"STDERR:\n{result.stderr[-2000:]}"
    )
    assert (project_copy / "SUMD.md").exists(), f"SUMD.md missing for profile={profile}"


def test_sumr_generates_sumr_md(project_copy):
    """sumr . must exit 0 and produce SUMR.md with expected sections."""
    result = _run(
        [str(SUMR_BIN), "."],
        cwd=project_copy,
    )
    assert result.returncode == 0, (
        f"sumr failed (rc={result.returncode}):\n"
        f"STDOUT:\n{result.stdout[-2000:]}\n"
        f"STDERR:\n{result.stderr[-2000:]}"
    )
    sumr_md = project_copy / "SUMR.md"
    assert sumr_md.exists(), "SUMR.md was not created by sumr"
    content = sumr_md.read_text()
    assert "## Metadata" in content, "SUMR.md missing ## Metadata"
    assert "refactor" in content.lower() or "SUMR" in content, (
        "SUMR.md does not appear to be a refactor report"
    )


def test_sumd_lint_passes_on_generated_output(project_copy):
    """After scan, sumd lint must report no errors on the generated SUMD.md."""
    # First generate
    _run([str(SUMD_BIN), "scan", ".", "--fix"], cwd=project_copy)
    sumd_md = project_copy / "SUMD.md"
    assert sumd_md.exists()

    result = _run([str(SUMD_BIN), "lint", str(sumd_md)], cwd=project_copy)
    assert result.returncode == 0, (
        f"sumd lint failed on generated SUMD.md:\n{result.stdout}\n{result.stderr}"
    )


def test_sumd_version_flag():
    """sumd --version must exit 0 and print a semver-like string."""
    result = _run([str(SUMD_BIN), "--version"], cwd=PROJECT_ROOT)
    assert result.returncode == 0, f"sumd --version failed: {result.stderr}"
    output = result.stdout + result.stderr
    assert any(c.isdigit() for c in output), (
        f"--version output does not contain a version number: {output!r}"
    )


def test_sumd_scan_produces_no_unhandled_exceptions(project_copy):
    """Stderr must not contain Python tracebacks after a successful scan."""
    result = _run(
        [str(SUMD_BIN), "scan", ".", "--fix", "--profile", "rich"],
        cwd=project_copy,
    )
    assert result.returncode == 0
    assert "Traceback (most recent call last)" not in result.stderr, (
        f"Unhandled exception in sumd scan:\n{result.stderr[-3000:]}"
    )
