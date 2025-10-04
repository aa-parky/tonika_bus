"""
Tonika Bus - Event communication system for modular music production.

The Bus is a centralized event broker that enables complete decoupling
between modules. Modules communicate through events, never directly.

Goblin Law #37: Never Meddle in Another Goblin's Guts
"""

from tonika_bus.core.bus import TonikaBus
from tonika_bus.core.events import EventMetadata, ModuleStatus, TonikaEvent
from tonika_bus.core.module import TonikaModule

__version__ = "0.2.0"

__all__ = [
    "TonikaBus",
    "TonikaModule",
    "TonikaEvent",
    "EventMetadata",
    "ModuleStatus",
]
