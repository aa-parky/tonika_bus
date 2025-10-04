"""
Core components of the Tonika Bus system.

This module contains the fundamental building blocks:
- TonikaBus: The central event broker
- TonikaModule: Base class for all modules
- Event structures: TonikaEvent, EventMetadata, ModuleStatus
"""

from tonika_bus.core.bus import TonikaBus
from tonika_bus.core.module import TonikaModule
from tonika_bus.core.events import TonikaEvent, EventMetadata, ModuleStatus

__all__ = [
    "TonikaBus",
    "TonikaModule",
    "TonikaEvent",
    "EventMetadata",
    "ModuleStatus",
]
