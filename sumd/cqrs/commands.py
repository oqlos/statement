"""Command pattern implementation for SUMD CQRS architecture."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime

from .events import Event, EventStore


@dataclass(frozen=True)
class Command:
    """Base command class for CQRS pattern."""
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    command_type: str = ""
    aggregate_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommandHandler(ABC):
    """Base command handler interface."""
    
    @abstractmethod
    async def handle(self, command: Command) -> List[Event]:
        """Handle a command and return resulting events."""
        pass
    
    @abstractmethod
    def can_handle(self, command_type: str) -> bool:
        """Check if this handler can handle the given command type."""
        pass


class CommandBus:
    """Command bus for dispatching commands to appropriate handlers."""
    
    def __init__(self, event_store: EventStore):
        self._handlers: Dict[str, CommandHandler] = {}
        self._event_store = event_store
    
    def register_handler(self, command_type: str, handler: CommandHandler) -> None:
        """Register a command handler for a specific command type."""
        self._handlers[command_type] = handler
    
    async def dispatch(self, command: Command) -> List[Event]:
        """Dispatch a command to the appropriate handler."""
        handler = self._handlers.get(command.command_type)
        if not handler:
            raise ValueError(f"No handler registered for command type: {command.command_type}")
        
        if not handler.can_handle(command.command_type):
            raise ValueError(f"Handler cannot handle command type: {command.command_type}")
        
        events = await handler.handle(command)
        
        # Store events
        for event in events:
            self._event_store.save_event(event)
        
        return events


# SUMD-specific commands
@dataclass(frozen=True)
class CreateSumdDocument(Command):
    """Command to create a new SUMD document."""
    command_type: str = "create_sumd_document"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "project_name": "",
        "description": "",
        "file_path": "",
        "profile": "rich",
    })


@dataclass(frozen=True)
class UpdateSumdDocument(Command):
    """Command to update an existing SUMD document."""
    command_type: str = "update_sumd_document"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "project_name": "",
        "description": "",
        "file_path": "",
        "changes": {},
    })


@dataclass(frozen=True)
class AddSumdSection(Command):
    """Command to add a section to a SUMD document."""
    command_type: str = "add_sumd_section"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "section_name": "",
        "section_type": "",
        "content": "",
        "level": 2,
    })


@dataclass(frozen=True)
class RemoveSumdSection(Command):
    """Command to remove a section from a SUMD document."""
    command_type: str = "remove_sumd_section"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "section_name": "",
        "section_type": "",
    })


@dataclass(frozen=True)
class ValidateSumdDocument(Command):
    """Command to validate a SUMD document."""
    command_type: str = "validate_sumd_document"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "file_path": "",
        "profile": "rich",
    })


@dataclass(frozen=True)
class ScanProject(Command):
    """Command to scan a project and generate SUMD."""
    command_type: str = "scan_project"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "project_path": "",
        "profile": "rich",
        "fix": False,
        "analyze": False,
        "depth": None,
    })


@dataclass(frozen=True)
class GenerateMap(Command):
    """Command to generate project map."""
    command_type: str = "generate_map"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "project_path": "",
        "force": False,
        "output": None,
    })


@dataclass(frozen=True)
class ExecuteDslCommand(Command):
    """Command to execute DSL command."""
    command_type: str = "execute_dsl_command"
    data: Dict[str, Any] = field(default_factory=lambda: {
        "dsl_expression": "",
        "context": {},
    })


# SUMD Command Handlers
class SumdCommandHandler(CommandHandler):
    """Base handler for SUMD commands."""
    
    def __init__(self, event_store: EventStore):
        self._event_store = event_store
    
    def can_handle(self, command_type: str) -> bool:
        """Check if this handler can handle SUMD commands."""
        sumd_commands = {
            "create_sumd_document",
            "update_sumd_document", 
            "add_sumd_section",
            "remove_sumd_section",
            "validate_sumd_document",
            "scan_project",
            "generate_map",
            "execute_dsl_command",
        }
        return command_type in sumd_commands
    
    async def handle(self, command: Command) -> List[Event]:
        """Handle SUMD commands."""
        from .events import (
            SumdDocumentCreated,
            SumdDocumentUpdated,
            SumdSectionAdded,
            SumdSectionRemoved,
            SumdDocumentValidated,
            SumdCommandExecuted,
        )
        
        events = []
        
        if command.command_type == "create_sumd_document":
            event = SumdDocumentCreated(
                aggregate_id=command.aggregate_id,
                data=command.data,
            )
            events.append(event)
        
        elif command.command_type == "update_sumd_document":
            event = SumdDocumentUpdated(
                aggregate_id=command.aggregate_id,
                data=command.data,
            )
            events.append(event)
        
        elif command.command_type == "add_sumd_section":
            event = SumdSectionAdded(
                aggregate_id=command.aggregate_id,
                data=command.data,
            )
            events.append(event)
        
        elif command.command_type == "remove_sumd_section":
            event = SumdSectionRemoved(
                aggregate_id=command.aggregate_id,
                data=command.data,
            )
            events.append(event)
        
        elif command.command_type == "validate_sumd_document":
            # Actually validate the document
            from ..parser import validate_sumd_file
            file_path = command.data.get("file_path")
            
            try:
                result = validate_sumd_file(file_path, profile=command.data.get("profile", "rich"))
                validation_result = "valid" if result["ok"] else "invalid"
                errors = [str(e) for e in result.get("markdown", []) + result.get("codeblocks", [])]
                
                event = SumdDocumentValidated(
                    aggregate_id=command.aggregate_id,
                    data={
                        "file_path": file_path,
                        "validation_result": validation_result,
                        "errors": errors,
                        "warnings": [],
                    },
                )
                events.append(event)
            except Exception as e:
                event = SumdDocumentValidated(
                    aggregate_id=command.aggregate_id,
                    data={
                        "file_path": file_path,
                        "validation_result": "error",
                        "errors": [str(e)],
                        "warnings": [],
                    },
                )
                events.append(event)
        
        # Add command execution event for all commands
        exec_event = SumdCommandExecuted(
            aggregate_id=command.aggregate_id,
            data={
                "command": command.command_type,
                "args": command.data,
                "result": "success",
                "duration_ms": 0,  # TODO: implement timing
            },
        )
        events.append(exec_event)
        
        return events
