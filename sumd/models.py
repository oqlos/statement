"""SUMD data models — SectionType, Section, SUMDDocument."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class SectionType(Enum):
    """SUMD section types."""

    PROJECT_HEADER = "project_header"
    METADATA = "metadata"
    INTENT = "intent"
    ARCHITECTURE = "architecture"
    INTERFACES = "interfaces"
    WORKFLOWS = "workflows"
    CONFIGURATION = "configuration"
    DEPENDENCIES = "dependencies"
    DEPLOYMENT = "deployment"
    UNKNOWN = "unknown"


@dataclass
class Section:
    """Represents a SUMD section."""

    name: str
    type: SectionType
    content: str
    level: int
    subsections: List["Section"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SUMDDocument:
    """Represents a parsed SUMD document."""

    project_name: str
    description: str
    sections: List[Section] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_content: str = ""
