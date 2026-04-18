"""SUMD CLI - Command-line interface for SUMD operations."""

import sys
from pathlib import Path
from typing import Optional

import click

from sumd.parser import SUMDParser, parse_file


@click.group()
@click.version_option(version="0.1.6")
def cli():
    """SUMD - Structured Unified Markdown Descriptor CLI."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def validate(file: Path):
    """Validate a SUMD document.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        parser = SUMDParser()
        errors = parser.validate(document)
        
        if errors:
            click.echo("❌ Validation failed:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            sys.exit(1)
        else:
            click.echo("✅ SUMD document is valid")
            sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Error parsing file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", type=click.Choice(["markdown", "json", "yaml", "toml"]), default="json", help="Output format")
@click.option("--output", type=click.Path(path_type=Path), help="Output file path")
def export(file: Path, format: str, output: Optional[Path]):
    """Export a SUMD document to structured format.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        
        data = {
            "project_name": document.project_name,
            "description": document.description,
            "sections": [
                {
                    "name": section.name,
                    "type": section.type.value,
                    "content": section.content,
                    "level": section.level,
                }
                for section in document.sections
            ],
        }
        
        result = ""
        if format == "markdown":
            result = document.raw_content
        elif format == "json":
            import json
            result = json.dumps(data, indent=2)
        elif format == "yaml":
            import yaml
            result = yaml.dump(data, default_flow_style=False)
        elif format == "toml":
            import toml
            result = toml.dumps(data)
        
        if output:
            output.write_text(result, encoding="utf-8")
            click.echo(f"✅ Exported to {output}")
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error exporting file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def info(file: Path):
    """Display information about a SUMD document.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        
        click.echo(f"📦 Project: {document.project_name}")
        click.echo(f"📝 Description: {document.description}")
        click.echo(f"📑 Sections: {len(document.sections)}")
        
        for section in document.sections:
            click.echo(f"  - {section.name} ({section.type.value})")
    except Exception as e:
        click.echo(f"❌ Error reading file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--format", type=click.Choice(["json", "yaml", "toml"]), default="json", help="Input format")
@click.option("--output", type=click.Path(path_type=Path), help="Output SUMD file path")
def generate(file: Path, format: str, output: Optional[Path]):
    """Generate a SUMD document from structured format.
    
    FILE: Path to the structured format file (json/yaml/toml)
    """
    try:
        content = file.read_text(encoding="utf-8")
        data = {}
        
        if format == "json":
            import json
            data = json.loads(content)
        elif format == "yaml":
            import yaml
            data = yaml.safe_load(content)
        elif format == "toml":
            import toml
            data = toml.loads(content)
        
        # Generate SUMD markdown
        lines = []
        lines.append(f"# {data.get('project_name', 'Untitled')}")
        if data.get('description'):
            lines.append(f"{data['description']}")
        lines.append("")
        
        for section in data.get('sections', []):
            level_prefix = "#" * section.get('level', 2)
            lines.append(f"{level_prefix} {section['name'].title()}")
            lines.append("")
            lines.append(section.get('content', ''))
            lines.append("")
        
        result = "\n".join(lines)
        
        if output:
            output.write_text(result, encoding="utf-8")
            click.echo(f"✅ Generated SUMD at {output}")
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"❌ Error generating SUMD: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--section", type=str, help="Extract specific section")
def extract(file: Path, section: str):
    """Extract content from a SUMD document.
    
    FILE: Path to the SUMD markdown file
    """
    try:
        document = parse_file(file)
        
        if section:
            for sec in document.sections:
                if sec.name.lower() == section.lower():
                    click.echo(sec.content)
                    return
            click.echo(f"❌ Section '{section}' not found", err=True)
            sys.exit(1)
        else:
            click.echo(document.raw_content)
    except Exception as e:
        click.echo(f"❌ Error extracting content: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
