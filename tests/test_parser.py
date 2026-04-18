"""Tests for SUMD parser."""

import pytest
from sumd.parser import SUMDParser, parse, validate


SAMPLE_SUMD = """# doql - Declarative Object Query Language

## Intent

doql provides a declarative language for querying and manipulating structured data.

## Architecture

### System Overview
doql consists of a parser, interpreter, and multiple backend adapters.

### Components
- **Parser**: Converts doql syntax into AST
- **Interpreter**: Executes AST against data sources

## Interfaces

### API
- **Endpoint**: POST /api/v1/query
  - **Description**: Execute doql query

### CLI
- **Command**: `doql query [file]`
  - **Description**: Execute doql query from file

## Workflows

### Query Execution
- **Trigger**: manual
- **Steps**:
  1. Parse query file
  2. Connect to data source
"""


def test_parse_basic():
    """Test basic parsing of SUMD document."""
    document = parse(SAMPLE_SUMD)
    
    assert document.project_name == "doql"
    assert "Declarative Object Query Language" in document.description
    assert len(document.sections) > 0


def test_parse_sections():
    """Test section parsing."""
    document = parse(SAMPLE_SUMD)
    
    section_names = {section.name for section in document.sections}
    assert "intent" in section_names
    assert "architecture" in section_names
    assert "interfaces" in section_names
    assert "workflows" in section_names


def test_validate_valid_document():
    """Test validation of valid document."""
    document = parse(SAMPLE_SUMD)
    errors = validate(document)
    
    assert len(errors) == 0


def test_validate_missing_intent():
    """Test validation fails without intent section."""
    invalid_sumd = """# test

## Architecture

Test architecture.
"""
    document = parse(invalid_sumd)
    errors = validate(document)
    
    assert len(errors) > 0
    assert any("Intent" in error for error in errors)


def test_parse_file(tmp_path):
    """Test parsing from file."""
    sumd_file = tmp_path / "test.sumd.md"
    sumd_file.write_text(SAMPLE_SUMD)
    
    from sumd.parser import parse_file
    document = parse_file(sumd_file)
    
    assert document.project_name == "doql"


def test_parser_class():
    """Test SUMDParser class directly."""
    parser = SUMDParser()
    document = parser.parse(SAMPLE_SUMD)
    
    assert document.project_name == "doql"
    assert parser.validate(document) == []
