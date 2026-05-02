"""Aggregate Root implementation for CQRS ES architecture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from .events import Event, EventStore


class AggregateRoot(ABC):
    """Base aggregate root for event sourcing."""
    
    def __init__(self, aggregate_id: str):
        self._aggregate_id = aggregate_id
        self._version = 0
        self._uncommitted_events: List[Event] = []
        self._event_store: Optional[EventStore] = None
    
    @property
    def aggregate_id(self) -> str:
        """Get the aggregate ID."""
        return self._aggregate_id
    
    @property
    def version(self) -> int:
        """Get the current version of the aggregate."""
        return self._version
    
    @property
    def uncommitted_events(self) -> List[Event]:
        """Get uncommitted events."""
        return self._uncommitted_events.copy()
    
    def set_event_store(self, event_store: EventStore) -> None:
        """Set the event store for this aggregate."""
        self._event_store = event_store
    
    def apply_event(self, event: Event) -> None:
        """Apply an event to the aggregate."""
        if event.aggregate_id != self._aggregate_id:
            raise ValueError(f"Event aggregate_id {event.aggregate_id} does not match aggregate ID {self._aggregate_id}")
        
        if event.version != self._version + 1:
            raise ValueError(f"Event version {event.version} does not match expected version {self._version + 1}")
        
        # Apply the event
        self._when(event)
        
        # Update version
        self._version = event.version
        
        # Add to uncommitted events
        self._uncommitted_events.append(event)
    
    def mark_events_as_committed(self) -> None:
        """Mark all uncommitted events as committed."""
        self._uncommitted_events.clear()
    
    def load_from_history(self, events: List[Event]) -> None:
        """Load aggregate state from event history."""
        for event in events:
            if event.aggregate_id != self._aggregate_id:
                raise ValueError(f"Event aggregate_id {event.aggregate_id} does not match aggregate ID {self._aggregate_id}")
            
            if event.version != self._version + 1:
                raise ValueError(f"Event version {event.version} does not match expected version {self._version + 1}")
            
            # Apply the event without adding to uncommitted
            self._when(event)
            self._version = event.version
    
    @abstractmethod
    def _when(self, event: Event) -> None:
        """Apply event-specific logic to update aggregate state."""
        pass
    
    def commit(self) -> None:
        """Commit uncommitted events to the event store."""
        if not self._event_store:
            raise ValueError("Event store not set")
        
        for event in self._uncommitted_events:
            self._event_store.save_event(event)
        
        self.mark_events_as_committed()
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the aggregate."""
        return {
            "aggregate_id": self._aggregate_id,
            "version": self._version,
        }


@dataclass
class EntityState:
    """Base entity state for aggregates."""
    id: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class Entity(ABC):
    """Base entity for domain objects."""
    
    def __init__(self, entity_id: str):
        self._id = entity_id
        self._domain_events: List[Event] = []
    
    @property
    def id(self) -> str:
        """Get the entity ID."""
        return self._id
    
    @property
    def domain_events(self) -> List[Event]:
        """Get domain events."""
        return self._domain_events.copy()
    
    def add_domain_event(self, event: Event) -> None:
        """Add a domain event."""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Clear domain events."""
        self._domain_events.clear()
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the entity."""
        return {
            "id": self._id,
        }


class ValueObject(ABC):
    """Base value object."""
    
    def __eq__(self, other: object) -> bool:
        """Value objects are equal if their attributes are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """Value objects should be hashable."""
        return hash(tuple(sorted(self.__dict__.items())))
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the value object."""
        return self.__dict__.copy()


class Repository(ABC):
    """Base repository for aggregates."""
    
    @abstractmethod
    async def get_by_id(self, aggregate_id: str) -> Optional[AggregateRoot]:
        """Get an aggregate by its ID."""
        pass
    
    @abstractmethod
    async def save(self, aggregate: AggregateRoot) -> None:
        """Save an aggregate."""
        pass
    
    @abstractmethod
    async def delete(self, aggregate_id: str) -> None:
        """Delete an aggregate."""
        pass


class EventSourcedRepository(Repository):
    """Event-sourced repository implementation."""
    
    def __init__(self, event_store: EventStore, aggregate_factory):
        self._event_store = event_store
        self._aggregate_factory = aggregate_factory
        self._cache: Dict[str, AggregateRoot] = {}
    
    async def get_by_id(self, aggregate_id: str) -> Optional[AggregateRoot]:
        """Get an aggregate by its ID from event store."""
        # Check cache first
        if aggregate_id in self._cache:
            return self._cache[aggregate_id]
        
        # Create new aggregate instance
        aggregate = self._aggregate_factory(aggregate_id)
        aggregate.set_event_store(self._event_store)
        
        # Load from event history
        events = self._event_store.get_events(aggregate_id)
        if not events:
            return None
        
        aggregate.load_from_history(events)
        
        # Cache the aggregate
        self._cache[aggregate_id] = aggregate
        
        return aggregate
    
    async def save(self, aggregate: AggregateRoot) -> None:
        """Save an aggregate to the event store."""
        aggregate.commit()
        
        # Update cache
        self._cache[aggregate.aggregate_id] = aggregate
    
    async def delete(self, aggregate_id: str) -> None:
        """Delete an aggregate (remove from cache)."""
        if aggregate_id in self._cache:
            del self._cache[aggregate_id]
    
    def clear_cache(self) -> None:
        """Clear the repository cache."""
        self._cache.clear()
