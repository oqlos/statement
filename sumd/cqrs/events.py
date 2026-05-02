"""Event Sourcing implementation for SUMD CQRS architecture."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Event:
    """Base event class for event sourcing."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    event_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "data": self.data,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Event:
        """Create event from dictionary."""
        return cls(
            event_id=data["event_id"],
            aggregate_id=data["aggregate_id"],
            event_type=data["event_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            version=data["version"],
            data=data["data"],
        )


class EventStore:
    """In-memory event store with optional file persistence."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self._events: Dict[str, List[Event]] = {}
        self._storage_path = storage_path
        if storage_path:
            self._load_events()
    
    def save_event(self, event: Event) -> None:
        """Save an event to the store."""
        if event.aggregate_id not in self._events:
            self._events[event.aggregate_id] = []
        self._events[event.aggregate_id].append(event)
        
        if self._storage_path:
            self._persist_event(event)
    
    def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get all events for an aggregate from a specific version."""
        events = self._events.get(aggregate_id, [])
        return [e for e in events if e.version > from_version]
    
    def get_all_events(self) -> List[Event]:
        """Get all events from the store."""
        all_events = []
        for events in self._events.values():
            all_events.extend(events)
        return sorted(all_events, key=lambda e: e.timestamp)
    
    def _persist_event(self, event: Event) -> None:
        """Persist event to file storage."""
        if not self._storage_path:
            return
        
        self._storage_path.mkdir(parents=True, exist_ok=True)
        event_file = self._storage_path / f"{event.aggregate_id}.jsonl"
        
        with open(event_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict()) + "\n")
    
    def _load_events(self) -> None:
        """Load events from file storage."""
        if not self._storage_path or not self._storage_path.exists():
            return
        
        for event_file in self._storage_path.glob("*.jsonl"):
            aggregate_id = event_file.stem
            self._events[aggregate_id] = []
            
            try:
                with open(event_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            event_data = json.loads(line)
                            event = Event.from_dict(event_data)
                            self._events[aggregate_id].append(event)
            except Exception:
                # Skip corrupted files
                continue


# SUMD-specific events
@dataclass(frozen=True)
class SumdDocumentCreated(Event):
    """Event fired when a SUMD document is created."""
    event_type: str = "sumd_document_created"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "project_name": "",
        "description": "",
        "file_path": "",
    })


@dataclass(frozen=True)
class SumdDocumentUpdated(Event):
    """Event fired when a SUMD document is updated."""
    event_type: str = "sumd_document_updated"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "project_name": "",
        "description": "",
        "file_path": "",
        "changes": {},
    })


@dataclass(frozen=True)
class SumdSectionAdded(Event):
    """Event fired when a section is added to SUMD document."""
    event_type: str = "sumd_section_added"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "section_name": "",
        "section_type": "",
        "content": "",
    })


@dataclass(frozen=True)
class SumdSectionRemoved(Event):
    """Event fired when a section is removed from SUMD document."""
    event_type: str = "sumd_section_removed"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "section_name": "",
        "section_type": "",
    })


@dataclass(frozen=True)
class SumdDocumentValidated(Event):
    """Event fired when a SUMD document is validated."""
    event_type: str = "sumd_document_validated"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "file_path": "",
        "validation_result": "valid",
        "errors": [],
        "warnings": [],
    })


@dataclass(frozen=True)
class SumdCommandExecuted(Event):
    """Event fired when a SUMD command is executed."""
    event_type: str = "sumd_command_executed"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "command": "",
        "args": {},
        "result": "success",
        "duration_ms": 0,
    })
