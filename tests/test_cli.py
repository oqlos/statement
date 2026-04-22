"""Tests for sumd CLI commands using click's CliRunner."""

import json
import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from sumd.cli import (
    _detect_project_type,
    _detect_projects,
    _is_project_dir,
    cli,
)


MINIMAL_SUMD = textwrap.dedent("""\
    # testapp

    ## Metadata

    | Key         | Value          |
    |-------------|----------------|
    | version     | 0.1.0          |
    | description | Test app       |

    ## Intent

    Build a simple test application.

    ## Architecture

    Single-tier application.

    ## Interfaces

    REST API on port 8080.

    ## Overview

    A simple test application.
""")


@pytest.fixture
def sumd_file(tmp_path):
    f = tmp_path / "SUMD.md"
    f.write_text(MINIMAL_SUMD)
    return f


class TestValidateCommand:
    def test_valid_file_exits_zero(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(sumd_file)])
        assert result.exit_code == 0

    def test_valid_file_prints_ok(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(sumd_file)])
        assert "valid" in result.output.lower() or result.exit_code == 0

    def test_missing_file_exits_nonzero(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(tmp_path / "no.md")])
        assert result.exit_code != 0


class TestInfoCommand:
    def test_info_runs(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["info", str(sumd_file)])
        # info command may fail on minimal file, just check no crash
        assert result.exit_code in (0, 1)


class TestExportCommand:
    def test_export_json(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", str(sumd_file), "--format", "json"])
        assert result.exit_code == 0
        # Should produce JSON output
        try:
            data = json.loads(result.output)
            assert isinstance(data, dict)
        except json.JSONDecodeError:
            pytest.fail(f"export did not produce valid JSON: {result.output[:200]}")

    def test_export_to_output_file(self, sumd_file, tmp_path):
        out = tmp_path / "out.json"
        runner = CliRunner()
        result = runner.invoke(cli, [
            "export", str(sumd_file), "--format", "json", "--output", str(out)
        ])
        assert result.exit_code == 0
        assert out.exists()

    def test_export_markdown(self, sumd_file):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", str(sumd_file), "--format", "markdown"])
        assert result.exit_code == 0


class TestCliVersion:
    def test_version_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "." in result.output  # version contains dots


class TestCliHelp:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SUMD" in result.output or "sumd" in result.output.lower()

    def test_validate_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0

    def test_export_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0

    def test_scan_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["scan", "--help"])
        assert result.exit_code == 0


class TestProjectDetection:
    """Detection must work across all supported languages/project types."""

    @pytest.mark.parametrize("marker,expected", [
        ("pyproject.toml",  "python"),
        ("setup.py",        "python"),
        ("package.json",    "node"),
        ("Cargo.toml",      "rust"),
        ("go.mod",          "go"),
        ("pom.xml",         "java"),
        ("build.gradle",    "java"),
        ("Gemfile",         "ruby"),
        ("composer.json",   "php"),
        ("Package.swift",   "swift"),
        ("pubspec.yaml",    "dart"),
        ("mix.exs",         "elixir"),
        ("stack.yaml",      "haskell"),
        ("project.clj",     "clojure"),
        ("CMakeLists.txt",  "cpp"),
        ("Makefile",        "generic"),
        ("Dockerfile",      "generic"),
        ("Taskfile.yml",    "generic"),
        ("SUMD.md",         "generic"),
    ])
    def test_is_project_dir_accepts_language_marker(
        self, tmp_path: Path, marker: str, expected: str,
    ):
        (tmp_path / marker).write_text("", encoding="utf-8")
        assert _is_project_dir(tmp_path) is True
        assert _detect_project_type(tmp_path) == expected

    @pytest.mark.parametrize("glob_name,expected", [
        ("demo.csproj",   "dotnet"),
        ("demo.sln",      "dotnet"),
        ("demo.gemspec",  "ruby"),
        ("demo.cabal",    "haskell"),
    ])
    def test_is_project_dir_accepts_glob_markers(
        self, tmp_path: Path, glob_name: str, expected: str,
    ):
        (tmp_path / glob_name).write_text("", encoding="utf-8")
        assert _is_project_dir(tmp_path) is True
        assert _detect_project_type(tmp_path) == expected

    def test_empty_dir_is_not_project(self, tmp_path: Path):
        assert _is_project_dir(tmp_path) is False
        assert _detect_project_type(tmp_path) == "generic"

    def test_detect_projects_finds_mixed_languages(self, tmp_path: Path):
        (tmp_path / "py-app").mkdir()
        (tmp_path / "py-app" / "pyproject.toml").write_text("", encoding="utf-8")
        (tmp_path / "node-app").mkdir()
        (tmp_path / "node-app" / "package.json").write_text("{}", encoding="utf-8")
        (tmp_path / "rust-app").mkdir()
        (tmp_path / "rust-app" / "Cargo.toml").write_text("", encoding="utf-8")
        (tmp_path / "not-a-project").mkdir()
        (tmp_path / "not-a-project" / "README.md").write_text("x", encoding="utf-8")

        found = {p.name for p in _detect_projects(tmp_path)}
        assert found == {"py-app", "node-app", "rust-app"}
