"""
Tonika Bus - Event Data Structures

Core event types and metadata for the Tonika Bus communication system.

Goblin Law #7: No Fat Orcs - This module does ONE thing: define event structures.
Goblin Law #13: Keep the Guest List Clean - Single source of truth for event types.

License: GPL-3.0
Part of the Tonika project - Music as Resistance
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ModuleStatus(Enum):
    """
    Lifecycle states for Tonika modules.

    Goblin Law #41: Only One Drumbeat of Readiness
    These are the only lifecycle states a module may have.
    """
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DESTROYED = "destroyed"


@dataclass
class EventMetadata:
    """
    Metadata for every Tonika event - who, when, what version.

    Every message carries context to enable time-travel debugging
    and provide audit trail for complex interactions.

    Attributes:
        timestamp: Unix epoch milliseconds (when event occurred)
        source: Module name that emitted the event
        version: Module version for debugging compatibility issues
    """
    timestamp: int  # Unix epoch milliseconds
    source: str  # Which module emitted it
    version: str  # Module version for debugging

    @staticmethod
    def create(source: str, version: str) -> 'EventMetadata':
        """
        Factory method to create metadata with current timestamp.

        Args:
            source: Name of the module emitting the event
            version: Version string of the emitting module

        Returns:
            EventMetadata with current timestamp
        """
        return EventMetadata(
            timestamp=int(datetime.now().timestamp() * 1000),
            source=source,
            version=version
        )


@dataclass
class TonikaEvent:
    """
    Core event structure for all Bus communication.

    Every message has context (who, when, what version) to enable
    time-travel debugging and provide audit trail for complex interactions.

    Goblin Law #8: All Goblins Are Boundary Guards
    Events are the boundary - everything flows through them.

    Attributes:
        type: Event type (e.g., "midi:note-on", "module:ready")
        detail: The actual payload data (can be any type)
        _meta: Context metadata (timestamp, source, version)
    """
    type: str  # e.g., "midi:note-on", "module:ready"
    detail: Any  # The actual payload data
    _meta: EventMetadata  # Context: timestamp, source, version

    def __str__(self) -> str:
        """String representation for logging and debugging"""
        return (
            f"TonikaEvent(type='{self.type}', "
            f"source='{self._meta.source}', "
            f"timestamp={self._meta.timestamp})"
        )
