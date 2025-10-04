"""
Tonika Module - Base Class for All Tonika Modules

Enforces consistent lifecycle and provides Bus access without direct coupling.
Automatic cleanup on destroy.

Goblin Law #41: Only One Drumbeat of Readiness - lifecycle managed here
Goblin Law #7: No Fat Orcs - each module does one thing well
Goblin Law #37: Never Meddle in Another Goblin's Guts - use the Bus

License: GPL-3.0
Part of the Tonika project - Music as Resistance
"""

import logging
from typing import Any, Callable, Dict, List, Optional

# Handle both package and standalone imports
try:
    from .bus import TonikaBus, EventHandler
    from .events import TonikaEvent, ModuleStatus
except ImportError:
    from bus import TonikaBus, EventHandler
    from events import TonikaEvent, ModuleStatus


class TonikaModule:
    """
    Base class for all Tonika modules.

    Enforces consistent lifecycle and provides Bus access without direct coupling.
    Automatic cleanup on destroy.

    Goblin Law #41: Only One Drumbeat of Readiness
    The base class alone beats the lifecycle drum - initializing, ready, error.
    Modules may emit their own events, but lifecycle is standardized here.

    Goblin Law #7: No Fat Orcs
    Each module does one thing well. The base class handles lifecycle,
    subclasses handle their specific functionality.

    Goblin Law #37: Never Meddle in Another Goblin's Guts
    Modules communicate through the Bus, never directly.
    """

    def __init__(
            self,
            name: str,
            version: str = "0.0.0",
            description: str = ""
    ):
        """
        Initialize a Tonika module.

        Args:
            name: Module name (should be unique)
            version: Module version (for debugging)
            description: Brief description of module purpose
        """
        self.name = name
        self.version = version
        self.description = description
        self.status = ModuleStatus.UNINITIALIZED

        # Track subscriptions for automatic cleanup
        # Goblin Law #7: No Fat Orcs - clean up after yourself
        self._unsubs: List[Callable[[], None]] = []

        # Access to the Bus (singleton)
        self._bus = TonikaBus()

        # Module-specific logger
        self.logger = logging.getLogger(f'TonikaModule.{name}')

        # Register with Bus
        # Goblin Law #13: Keep the Guest List Clean
        self._bus.register_module(self)
        self.logger.info(f"🧩 Module created: {name} v{version}")

    async def init(self) -> None:
        """
        Initialize the module (async).

        Goblin Law #41: Only One Drumbeat of Readiness
        Follows the lifecycle drumbeat:
        1. Emit "module:initializing"
        2. Run custom _initialize()
        3. Emit "module:ready" or "module:error"

        Subclasses should override _initialize(), not this method.
        """
        try:
            self.status = ModuleStatus.INITIALIZING
            self.emit("module:initializing", {
                "name": self.name,
                "version": self.version,
                "status": self.status.value
            })

            # Call custom initialization
            # Goblin Law #32: Never Patch a Monkey - extend, don't overwrite
            await self._initialize()

            self.status = ModuleStatus.READY
            self.emit("module:ready", {
                "name": self.name,
                "version": self.version,
                "status": self.status.value
            })

            self.logger.info(f"✅ Module ready: {self.name}")

        except Exception as e:
            self.status = ModuleStatus.ERROR
            self.emit("module:error", {
                "name": self.name,
                "version": self.version,
                "status": self.status.value,
                "error": str(e)
            })
            self.logger.error(
                f"❌ Module init failed: {self.name} - {e}",
                exc_info=True
            )
            raise

    async def _initialize(self) -> None:
        """
        Custom initialization logic (override in subclass).

        This is where modules set up their internal state and
        subscribe to events they care about.

        Goblin Law #32: Never Patch a Monkey
        Extend this method in subclasses, don't override init().

        Example:
            async def _initialize(self):
                self.on("midi:note_on", self.handle_note)
                self.active_notes = set()
        """
        pass

    def emit(self, event_type: str, detail: Any) -> None:
        """
        Emit an event via the Bus.

        Goblin Law #8: All Goblins Are Boundary Guards
        Everything flows through the Bus first.

        Args:
            event_type: Event type (e.g., "midi:note-on")
            detail: Event payload
        """
        self._bus.emit(
            event_type,
            detail,
            source=self.name,
            version=self.version
        )

    def on(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe to an event type.

        Automatically tracked for cleanup on destroy.

        Goblin Law #37: Never Meddle in Another Goblin's Guts
        Use the Bus for all communication.

        Args:
            event_type: Event type to listen for
            handler: Function to call when event occurs
        """
        unsub = self._bus.on(event_type, handler)
        self._unsubs.append(unsub)

    def once(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe to an event type, but only fire once.

        Automatically tracked for cleanup.

        Args:
            event_type: Event type to listen for
            handler: Function to call when event occurs
        """
        unsub = self._bus.once(event_type, handler)
        self._unsubs.append(unsub)

    async def wait_for(
            self,
            event_type: str,
            timeout_ms: Optional[int] = None
    ) -> TonikaEvent:
        """
        Wait for a specific event before continuing.

        Useful for initialization dependencies.

        Example:
            await self.wait_for("midi:ready", timeout_ms=5000)
            # Now safe to use MIDI

        Args:
            event_type: Event type to wait for
            timeout_ms: Timeout in milliseconds

        Returns:
            The event that was received

        Raises:
            asyncio.TimeoutError: If timeout is reached
        """
        return await self._bus.wait_for(event_type, timeout_ms)

    def destroy(self) -> None:
        """
        Clean up the module.

        Goblin Law #7: No Fat Orcs - clean up after yourself

        Unsubscribes from all events, removes from registry,
        emits destruction event.

        No memory leaks from orphaned event handlers.
        """
        # Unsubscribe from all events
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()

        # Emit destruction event BEFORE unregistering
        # so other modules can react to this module going away
        self.emit("module:destroyed", {
            "name": self.name,
            "version": self.version
        })

        # Remove from registry
        # Goblin Law #13: Keep the Guest List Clean
        self._bus.unregister_module(self.name)

        self.status = ModuleStatus.DESTROYED
        self.logger.info(f"💀 Module destroyed: {self.name}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current module status.

        Returns:
            Dictionary with status information
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": self.status.value
        }
