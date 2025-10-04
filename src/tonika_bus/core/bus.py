"""
Tonika Bus - Central Event Communication System

The Bus is a centralized event communication system - a message broker where
modules never talk directly to each other.

Goblin Law #37: Never Meddle in Another Goblin's Guts
Goblin Law #8: All Goblins Are Boundary Guards - everything goes to Bus first
Goblin Law #13: Keep the Guest List Clean - single source of truth for events

License: GPL-3.0
Part of the Tonika project - Music as Resistance
"""

import asyncio
import logging
from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Optional


# Import from package (MyPy-friendly)
from tonika_bus.core.events import EventMetadata, TonikaEvent

# Avoid circular import for type hints
if TYPE_CHECKING:
    pass

# Type alias for event handlers
EventHandler = Callable[[TonikaEvent], None]


class TonikaBus:
    """
    The Central Bus - Singleton pattern

    Single source of truth for all inter-module communication.
    Decouples modules completely and provides observable event history.

    Goblin Law #37: Never Meddle in Another Goblin's Guts
    Goblin Law #8: All Goblins Are Boundary Guards - everything goes to Bus first
    Goblin Law #13: Keep the Guest List Clean - Bus maintains the registry

    The Bus enforces that all communication flows through events,
    preventing direct coupling between modules.
    """

    _instance: Optional["TonikaBus"] = None
    _initialized: bool = False

    def __new__(cls):
        """
        Singleton pattern - only one Bus exists.

        Goblin Law #13: Keep the Guest List Clean
        One Bus, one registry, one source of truth.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize Bus components (only once due to singleton).

        The Bus maintains:
        - Event handlers registry (who listens to what)
        - Module registry (who's in the hall)
        - Event log (what happened, when, and who did it)
        - Wait promises (for async event waiting)
        """
        if not TonikaBus._initialized:
            # Event handlers: event_type -> set of handler functions
            self.handlers: dict[str, set[EventHandler]] = {}

            # Module registry: module_name -> module instance
            # Goblin Law #13: Keep the Guest List Clean
            self.module_registry: dict[str, Any] = {}  # Any to avoid circular import

            # Event log: bounded deque to prevent unbounded memory growth
            # Goblin Law #7: No Fat Orcs - keep it lean
            self._event_log_maxlen: int = 1000
            self.event_log: deque[TonikaEvent] = deque(maxlen=self._event_log_maxlen)

            # Debug mode and logging
            self.debug: bool = False
            self.logger = logging.getLogger("TonikaBus")

            # Wait promises for async event waiting
            self._wait_promises: dict[str, list[asyncio.Future]] = {}

            TonikaBus._initialized = True
            self.logger.info("🚌 Tonika Bus initialized - Goblin Law #37 enforcement active")

    def set_debug(self, enabled: bool) -> None:
        """
        Enable or disable debug logging.

        Args:
            enabled: True to enable debug logging, False to disable
        """
        self.debug = enabled
        level = logging.DEBUG if enabled else logging.INFO
        self.logger.setLevel(level)

    def emit(
        self, event_type: str, detail: Any, source: str = "unknown", version: str = "0.0.0"
    ) -> None:
        """
        Emit an event to all subscribers.

        This is the core of the Bus - every interaction flows through here.

        Goblin Law #8: All Goblins Are Boundary Guards
        Everything that happens in Tonika flows through the Bus first.

        Args:
            event_type: Event type (e.g., "midi:note-on", "module:ready")
            detail: The actual payload data
            source: Which module emitted it
            version: Module version for debugging
        """
        # Create event with metadata
        event = TonikaEvent(
            type=event_type, detail=detail, _meta=EventMetadata.create(source, version)
        )

        # Add to event log for debugging
        self.event_log.append(event)

        # Debug logging if enabled
        if self.debug:
            self.logger.debug(f"📢 EMIT: {event}")

        # Notify all handlers for this event type
        # Note: Convert to list to avoid "Set changed size during iteration"
        # if a handler unsubscribes during execution
        if event_type in self.handlers:
            for handler in list(self.handlers[event_type]):
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"❌ Handler error for {event_type}: {e}", exc_info=True)

        # Resolve any wait_for promises
        if event_type in self._wait_promises:
            for future in self._wait_promises[event_type]:
                if not future.done():
                    future.set_result(event)
            del self._wait_promises[event_type]

    def on(self, event_type: str, handler: EventHandler) -> Callable[[], None]:
        """
        Subscribe to an event type.

        Returns an unsubscribe function for cleanup.

        Goblin Law #37: Never Meddle in Another Goblin's Guts
        Modules communicate through the Bus, never directly.

        Args:
            event_type: The event type to listen for
            handler: Function to call when event occurs

        Returns:
            Unsubscribe function (call it to stop listening)
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = set()

        self.handlers[event_type].add(handler)

        if self.debug:
            handler_count = len(self.handlers[event_type])
            self.logger.debug(f"👂 SUBSCRIBE: {event_type} (total handlers: {handler_count})")

        # Return unsubscribe function
        def unsubscribe():
            if event_type in self.handlers and handler in self.handlers[event_type]:
                self.handlers[event_type].remove(handler)
                if self.debug:
                    self.logger.debug(f"🔇 UNSUBSCRIBE: {event_type}")

        return unsubscribe

    def once(self, event_type: str, handler: EventHandler) -> Callable[[], None]:
        """
        Subscribe to an event type, but only fire once.

        Automatically unsubscribes after the first event.

        Args:
            event_type: The event type to listen for
            handler: Function to call when event occurs

        Returns:
            Unsubscribe function (in case you want to cancel early)
        """
        unsub = None

        def one_time_handler(event: TonikaEvent):
            handler(event)
            if unsub:
                unsub()

        unsub = self.on(event_type, one_time_handler)
        return unsub

    async def wait_for(self, event_type: str, timeout_ms: int | None = None) -> TonikaEvent:
        """
        Wait for a specific event before continuing (async).

        Useful for initialization dependencies.

        Example:
            await bus.wait_for("midi:ready", timeout_ms=5000)
            # Now safe to send MIDI commands

        Args:
            event_type: Event type to wait for
            timeout_ms: Timeout in milliseconds (None = no timeout)

        Returns:
            The event that was received

        Raises:
            asyncio.TimeoutError: If timeout is reached
        """
        future = asyncio.get_event_loop().create_future()

        if event_type not in self._wait_promises:
            self._wait_promises[event_type] = []

        self._wait_promises[event_type].append(future)

        if timeout_ms:
            timeout_seconds = timeout_ms / 1000.0
            return await asyncio.wait_for(future, timeout=timeout_seconds)
        return await future

    def get_event_log(self, limit: int | None = None) -> list[TonikaEvent]:
        """
        Get recent events from the log.

        Useful for debugging - see exact sequence of what happened.

        Args:
            limit: Maximum number of events to return (None = all)

        Returns:
            List of recent events
        """
        if limit:
            # deque doesn't support slicing; convert to list first
            return list(self.event_log)[-limit:]
        # Return a copy as list to avoid exposing internal deque
        return list(self.event_log)

    def clear_event_log(self) -> None:
        """
        Clear the event log.

        Useful for testing or resetting debug state.
        """
        self.event_log.clear()
        if self.debug:
            self.logger.debug("🧹 Event log cleared")

    def register_module(self, module: Any) -> None:
        """
        Register a module with the Bus.

        Goblin Law #13: Keep the Guest List Clean
        The Bus maintains the single source of truth for who's in the hall.

        Args:
            module: The module to register
        """
        self.module_registry[module.name] = module
        self.logger.info(f"📝 Module registered: {module.name} v{module.version}")

    def unregister_module(self, module_name: str) -> None:
        """
        Unregister a module from the Bus.

        Args:
            module_name: Name of module to unregister
        """
        if module_name in self.module_registry:
            del self.module_registry[module_name]
            self.logger.info(f"🗑️  Module unregistered: {module_name}")

    def get_module(self, module_name: str) -> Any | None:
        """
        Get a module by name.

        For inspection only, not for direct calls.
        Goblin Law #37: Never Meddle in Another Goblin's Guts

        Args:
            module_name: Name of module to retrieve

        Returns:
            The module if found, None otherwise
        """
        return self.module_registry.get(module_name)

    def list_modules(self) -> list[str]:
        """
        Get list of all registered module names.

        Returns:
            List of module names currently registered
        """
        return list(self.module_registry.keys())
