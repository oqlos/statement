"""SUMD-specific aggregate implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .aggregates import AggregateRoot
from .events import (
    Event,
    SumdDocumentCreated,
    SumdDocumentUpdated,
    SumdSectionAdded,
    SumdSectionRemoved,
    SumdDocumentValidated,
)


@dataclass
class SumdSection:
    """Represents a section in a SUMD document."""
    name: str
    section_type: str
    content: str
    level: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert section to dictionary."""
        return {
            "name": self.name,
            "type": self.section_type,
            "content": self.content,
            "level": self.level,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SumdSection:
        """Create section from dictionary."""
        return cls(
            name=data["name"],
            section_type=data["type"],
            content=data["content"],
            level=data.get("level", 2),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SumdDocumentState:
    """State of a SUMD document aggregate."""
    project_name: str = ""
    description: str = ""
    file_path: str = ""
    profile: str = "rich"
    sections: List[SumdSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_validated: Optional[datetime] = None
    validation_status: str = "not_validated"
    validation_errors: List[str] = field(default_factory=list)


class SumdAggregate(AggregateRoot):
    """SUMD document aggregate root."""
    
    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id)
        self._state = SumdDocumentState()
    
    @property
    def state(self) -> SumdDocumentState:
        """Get the current state of the SUMD document."""
        return self._state
    
    def _when(self, event: Event) -> None:
        """Apply event-specific logic to update aggregate state."""
        if isinstance(event, SumdDocumentCreated):
            self._when_document_created(event)
        elif isinstance(event, SumdDocumentUpdated):
            self._when_document_updated(event)
        elif isinstance(event, SumdSectionAdded):
            self._when_section_added(event)
        elif isinstance(event, SumdSectionRemoved):
            self._when_section_removed(event)
        elif isinstance(event, SumdDocumentValidated):
            self._when_document_validated(event)
    
    def _when_document_created(self, event: SumdDocumentCreated) -> None:
        """Handle SumdDocumentCreated event."""
        self._state.project_name = event.data.get("project_name", "")
        self._state.description = event.data.get("description", "")
        self._state.file_path = event.data.get("file_path", "")
        self._state.profile = event.data.get("profile", "rich")
        self._state.created_at = event.timestamp
        self._state.updated_at = event.timestamp
    
    def _when_document_updated(self, event: SumdDocumentUpdated) -> None:
        """Handle SumdDocumentUpdated event."""
        changes = event.data.get("changes", {})
        
        if "project_name" in changes:
            self._state.project_name = changes["project_name"]
        if "description" in changes:
            self._state.description = changes["description"]
        if "file_path" in changes:
            self._state.file_path = changes["file_path"]
        if "profile" in changes:
            self._state.profile = changes["profile"]
        if "metadata" in changes:
            self._state.metadata.update(changes["metadata"])
        
        self._state.updated_at = event.timestamp
    
    def _when_section_added(self, event: SumdSectionAdded) -> None:
        """Handle SumdSectionAdded event."""
        section_name = event.data.get("section_name")
        section_type = event.data.get("section_type")
        content = event.data.get("content", "")
        level = event.data.get("level", 2)
        metadata = event.data.get("metadata", {})
        
        # Remove existing section with same name if it exists
        self._state.sections = [
            s for s in self._state.sections 
            if s.name.lower() != section_name.lower()
        ]
        
        # Add new section
        new_section = SumdSection(
            name=section_name,
            section_type=section_type,
            content=content,
            level=level,
            metadata=metadata,
        )
        self._state.sections.append(new_section)
        self._state.updated_at = event.timestamp
    
    def _when_section_removed(self, event: SumdSectionRemoved) -> None:
        """Handle SumdSectionRemoved event."""
        section_name = event.data.get("section_name")
        
        self._state.sections = [
            s for s in self._state.sections 
            if s.name.lower() != section_name.lower()
        ]
        self._state.updated_at = event.timestamp
    
    def _when_document_validated(self, event: SumdDocumentValidated) -> None:
        """Handle SumdDocumentValidated event."""
        self._state.last_validated = event.timestamp
        self._state.validation_status = event.data.get("validation_result", "unknown")
        self._state.validation_errors = event.data.get("errors", [])
    
    # Domain methods
    def create_document(
        self,
        project_name: str,
        description: str,
        file_path: str,
        profile: str = "rich",
    ) -> None:
        """Create a new SUMD document."""
        if self._state.created_at:
            raise ValueError("Document already exists")
        
        event = SumdDocumentCreated(
            aggregate_id=self._aggregate_id,
            version=self._version + 1,
            data={
                "project_name": project_name,
                "description": description,
                "file_path": file_path,
                "profile": profile,
            },
        )
        self.apply_event(event)
    
    def update_document(self, changes: Dict[str, Any]) -> None:
        """Update the SUMD document."""
        if not self._state.created_at:
            raise ValueError("Document does not exist")
        
        event = SumdDocumentUpdated(
            aggregate_id=self._aggregate_id,
            version=self._version + 1,
            data={
                "project_name": self._state.project_name,
                "description": self._state.description,
                "file_path": self._state.file_path,
                "changes": changes,
            },
        )
        self.apply_event(event)
    
    def add_section(
        self,
        section_name: str,
        section_type: str,
        content: str,
        level: int = 2,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a section to the document."""
        if not self._state.created_at:
            raise ValueError("Document does not exist")
        
        event = SumdSectionAdded(
            aggregate_id=self._aggregate_id,
            version=self._version + 1,
            data={
                "section_name": section_name,
                "section_type": section_type,
                "content": content,
                "level": level,
                "metadata": metadata or {},
            },
        )
        self.apply_event(event)
    
    def remove_section(self, section_name: str) -> None:
        """Remove a section from the document."""
        if not self._state.created_at:
            raise ValueError("Document does not exist")
        
        # Check if section exists
        section_exists = any(
            s.name.lower() == section_name.lower() 
            for s in self._state.sections
        )
        if not section_exists:
            raise ValueError(f"Section '{section_name}' does not exist")
        
        event = SumdSectionRemoved(
            aggregate_id=self._aggregate_id,
            version=self._version + 1,
            data={
                "section_name": section_name,
                "section_type": "",  # Will be filled by event handler
            },
        )
        self.apply_event(event)
    
    def validate_document(self, validation_result: str, errors: List[str]) -> None:
        """Record document validation results."""
        if not self._state.created_at:
            raise ValueError("Document does not exist")
        
        event = SumdDocumentValidated(
            aggregate_id=self._aggregate_id,
            version=self._version + 1,
            data={
                "file_path": self._state.file_path,
                "validation_result": validation_result,
                "errors": errors,
                "warnings": [],
            },
        )
        self.apply_event(event)
    
    def get_section(self, section_name: str) -> Optional[SumdSection]:
        """Get a specific section by name."""
        for section in self._state.sections:
            if section.name.lower() == section_name.lower():
                return section
        return None
    
    def has_section(self, section_name: str) -> bool:
        """Check if a section exists."""
        return self.get_section(section_name) is not None
    
    def get_state(self) -> Dict[str, Any]:
        """Get the complete state of the aggregate."""
        base_state = super().get_state()
        base_state.update({
            "project_name": self._state.project_name,
            "description": self._state.description,
            "file_path": self._state.file_path,
            "profile": self._state.profile,
            "sections": [section.to_dict() for section in self._state.sections],
            "metadata": self._state.metadata,
            "created_at": self._state.created_at.isoformat() if self._state.created_at else None,
            "updated_at": self._state.updated_at.isoformat() if self._state.updated_at else None,
            "last_validated": self._state.last_validated.isoformat() if self._state.last_validated else None,
            "validation_status": self._state.validation_status,
            "validation_errors": self._state.validation_errors,
        })
        return base_state
    
    @classmethod
    def create_from_file(cls, file_path: Path) -> SumdAggregate:
        """Create a SUMD aggregate from an existing file."""
        from ..parser import parse_file
        from ..extractor import extract_pyproject, extract_readme_title
        
        try:
            doc = parse_file(file_path)
            proj_dir = file_path.parent
            
            # Extract project info
            pyproj = extract_pyproject(proj_dir)
            title = extract_readme_title(proj_dir)
            
            # Create aggregate
            aggregate_id = str(file_path)
            aggregate = cls(aggregate_id)
            
            # Create document created event
            created_event = SumdDocumentCreated(
                aggregate_id=aggregate_id,
                version=1,
                data={
                    "project_name": doc.project_name or pyproj.get("name", proj_dir.name),
                    "description": doc.description or title or "",
                    "file_path": str(file_path),
                    "profile": "rich",
                },
            )
            aggregate.apply_event(created_event)
            
            # Add section events for each section
            for section in doc.sections:
                section_event = SumdSectionAdded(
                    aggregate_id=aggregate_id,
                    version=aggregate.version + 1,
                    data={
                        "section_name": section.name,
                        "section_type": section.type.value,
                        "content": section.content,
                        "level": section.level,
                        "metadata": {},
                    },
                )
                aggregate.apply_event(section_event)
            
            return aggregate
            
        except Exception as e:
            raise ValueError(f"Failed to create aggregate from file {file_path}: {e}")
