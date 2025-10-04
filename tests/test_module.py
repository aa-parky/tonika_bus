"""
Comprehensive test suite for TonikaModule (module.py)

Tests all functionality of the TonikaModule base class:
- Module lifecycle (init, destroy)
- Event handling (emit, subscribe)
- Status management
- Automatic cleanup
- Async operations

Goblin Law #41: Only One Drumbeat of Readiness
These tests verify standardized module lifecycle management.
"""

import asyncio

import pytest

from tonika_bus.core.bus import TonikaBus
from tonika_bus.core.events import ModuleStatus, TonikaEvent
from tonika_bus.core.module import TonikaModule

# ============================================================================
# Test Module Implementations
# ============================================================================


class SimpleModule(TonikaModule):
    """Simple test module"""

    def __init__(self, name="SimpleModule"):
        super().__init__(name=name, version="1.0.0")
        self.init_called = False
        self.destroy_called = False

    async def _initialize(self):
        """Initialize the module"""
        self.init_called = True


class EventEmittingModule(TonikaModule):
    """Module that emits events during lifecycle"""

    def __init__(self):
        super().__init__(name="EventEmitter", version="1.0.0")

    async def _initialize(self):
        """Emit event during init"""
        self.emit("module:initialized", {"module": self.name})


class SubscribingModule(TonikaModule):
    """Module that subscribes to events"""

    def __init__(self):
        super().__init__(name="Subscriber", version="1.0.0")
        self.received_events = []

    async def _initialize(self):
        """Subscribe to events during init"""
        self.on("test:event", self._handle_test_event)

    def _handle_test_event(self, event: TonikaEvent):
        """Handle test events"""
        self.received_events.append(event)


class FailingModule(TonikaModule):
    """Module that fails during initialization"""

    def __init__(self):
        super().__init__(name="FailingModule", version="1.0.0")

    async def _initialize(self):
        """Fail during init"""
        raise ValueError("Intentional initialization failure")


class AsyncWaitingModule(TonikaModule):
    """Module that uses wait_for"""

    def __init__(self):
        super().__init__(name="AsyncWaiter", version="1.0.0")
        self.waited_event = None

    async def _initialize(self):
        """Setup"""
        pass

    async def wait_for_event(self, event_type: str):
        """Wait for a specific event"""
        self.waited_event = await self.wait_for(event_type, timeout_ms=1000)


# ============================================================================
# Module Lifecycle Tests
# ============================================================================


@pytest.mark.unit
class TestTonikaModuleLifecycle:
    """Test module lifecycle management"""

    @pytest.mark.asyncio
    async def test_module_initialization_sequence(self, fresh_bus):
        """Test that module initialization follows correct sequence"""
        module = SimpleModule()

        # Before init
        assert module.status == ModuleStatus.UNINITIALIZED
        assert not module.init_called

        # Initialize
        await module.init()

        # After init
        assert module.status == ModuleStatus.READY
        assert module.init_called

    @pytest.mark.asyncio
    async def test_module_initialization_registers_with_bus(self, fresh_bus):
        """Test that module registers with bus during init"""
        module = SimpleModule(name="TestModule")

        await module.init()

        # Should be registered
        assert "TestModule" in fresh_bus.list_modules()
        assert fresh_bus.get_module("TestModule") is module

    @pytest.mark.asyncio
    async def test_module_initialization_error(self, fresh_bus):
        """Test that initialization errors set ERROR status"""
        module = FailingModule()

        with pytest.raises(ValueError, match="Intentional initialization failure"):
            await module.init()

        # Should be in ERROR state
        assert module.status == ModuleStatus.ERROR

    @pytest.mark.asyncio
    async def test_module_destruction(self, fresh_bus):
        """Test module destruction"""
        module = SimpleModule()
        await module.init()

        # Destroy (synchronous!)
        module.destroy()

        # Should be destroyed
        assert module.status == ModuleStatus.DESTROYED

    @pytest.mark.asyncio
    async def test_module_destruction_unregisters_from_bus(self, fresh_bus):
        """Test that module unregisters from bus during destroy"""
        module = SimpleModule(name="TestModule")
        await module.init()

        # Destroy
        module.destroy()

        # Should be unregistered
        assert "TestModule" not in fresh_bus.list_modules()

    @pytest.mark.asyncio
    async def test_module_destruction_cleans_up_subscriptions(self, fresh_bus):
        """Test that destroy cleans up event subscriptions"""
        module = SubscribingModule()
        await module.init()

        # Module should be subscribed
        assert "test:event" in fresh_bus.handlers

        # Destroy
        module.destroy()

        # Emit event - module should not receive it
        fresh_bus.emit("test:event", {})

        # No new events should be received
        assert len(module.received_events) == 0


# ============================================================================
# Event Handling Tests
# ============================================================================


@pytest.mark.unit
class TestTonikaModuleEventHandling:
    """Test module event handling"""

    @pytest.mark.asyncio
    async def test_module_can_subscribe_to_events(self, fresh_bus):
        """Test that module can subscribe to events"""
        module = SubscribingModule()
        await module.init()

        # Emit event
        fresh_bus.emit("test:event", {"data": 123})

        # Module should receive it
        assert len(module.received_events) == 1
        assert module.received_events[0].detail == {"data": 123}

    @pytest.mark.asyncio
    async def test_module_can_emit_events(self, fresh_bus):
        """Test that module can emit events"""
        module = EventEmittingModule()

        # Initialize (which emits event)
        await module.init()

        # Check event log
        events = fresh_bus.get_event_log()
        init_events = [e for e in events if e.type == "module:initialized"]

        assert len(init_events) == 1
        assert init_events[0].detail["module"] == "EventEmitter"

    @pytest.mark.asyncio
    async def test_module_events_have_correct_source(self, fresh_bus):
        """Test that module-emitted events have correct source"""
        module = EventEmittingModule()
        await module.init()

        events = fresh_bus.get_event_log()
        init_event = [e for e in events if e.type == "module:initialized"][0]

        assert init_event._meta.source == "EventEmitter"
        assert init_event._meta.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_module_cleanup_unsubscribes(self, fresh_bus):
        """Test that module cleanup removes subscriptions"""
        module = SubscribingModule()
        await module.init()

        # Emit event - should be received
        fresh_bus.emit("test:event", {"data": 1})
        assert len(module.received_events) == 1

        # Destroy module
        module.destroy()

        # Emit event - should NOT be received
        fresh_bus.emit("test:event", {"data": 2})
        assert len(module.received_events) == 1  # Still 1, not 2

    @pytest.mark.asyncio
    async def test_module_multiple_subscriptions(self, fresh_bus):
        """Test module with multiple event subscriptions"""

        class MultiSubscriber(TonikaModule):
            def __init__(self):
                super().__init__(name="MultiSub", version="1.0.0")
                self.event_a_count = 0
                self.event_b_count = 0

            async def _initialize(self):
                self.on("event:a", lambda e: setattr(self, "event_a_count", self.event_a_count + 1))
                self.on("event:b", lambda e: setattr(self, "event_b_count", self.event_b_count + 1))

        module = MultiSubscriber()
        await module.init()

        # Emit different events
        fresh_bus.emit("event:a", {})
        fresh_bus.emit("event:a", {})
        fresh_bus.emit("event:b", {})

        assert module.event_a_count == 2
        assert module.event_b_count == 1

    @pytest.mark.asyncio
    async def test_module_once_subscription(self, fresh_bus):
        """Test module using once() for one-time subscription"""

        class OnceSubscriber(TonikaModule):
            def __init__(self):
                super().__init__(name="OnceSub", version="1.0.0")
                self.call_count = 0

            async def _initialize(self):
                self.once("test:event", lambda e: setattr(self, "call_count", self.call_count + 1))

        module = OnceSubscriber()
        await module.init()

        # Emit multiple times
        fresh_bus.emit("test:event", {})
        fresh_bus.emit("test:event", {})
        fresh_bus.emit("test:event", {})

        # Should only be called once
        assert module.call_count == 1


# ============================================================================
# Async Operation Tests
# ============================================================================


@pytest.mark.unit
class TestTonikaModuleAsync:
    """Test module async operations"""

    @pytest.mark.asyncio
    async def test_module_can_wait_for_events(self, fresh_bus):
        """Test that module can use wait_for"""
        module = AsyncWaitingModule()
        await module.init()

        # Start waiting in background
        wait_task = asyncio.create_task(module.wait_for_event("test:event"))

        # Give it time to start waiting
        await asyncio.sleep(0.05)

        # Emit event
        fresh_bus.emit("test:event", {"data": 42})

        # Wait for completion
        await wait_task

        # Module should have received event
        assert module.waited_event is not None
        assert module.waited_event.detail == {"data": 42}

    @pytest.mark.asyncio
    async def test_module_wait_for_timeout(self, fresh_bus):
        """Test that module wait_for times out correctly"""
        module = AsyncWaitingModule()
        await module.init()

        # Wait for event that never comes
        with pytest.raises(asyncio.TimeoutError):
            await module.wait_for("nonexistent:event", timeout_ms=100)

    @pytest.mark.asyncio
    async def test_module_async_initialization(self, fresh_bus):
        """Test module with async initialization logic"""

        class AsyncInitModule(TonikaModule):
            def __init__(self):
                super().__init__(name="AsyncInit", version="1.0.0")
                self.async_work_done = False

            async def _initialize(self):
                # Simulate async work
                await asyncio.sleep(0.05)
                self.async_work_done = True

        module = AsyncInitModule()
        await module.init()

        assert module.async_work_done
        assert module.status == ModuleStatus.READY


# ============================================================================
# Status Management Tests
# ============================================================================


@pytest.mark.unit
class TestTonikaModuleStatus:
    """Test module status management"""

    @pytest.mark.asyncio
    async def test_get_status_returns_info(self, fresh_bus):
        """Test that get_status returns module information"""
        module = SimpleModule(name="StatusTest")
        await module.init()

        status = module.get_status()

        assert status["name"] == "StatusTest"
        assert status["version"] == "1.0.0"
        assert status["status"] == ModuleStatus.READY.value

    @pytest.mark.asyncio
    async def test_status_transitions(self, fresh_bus):
        """Test status transitions through lifecycle"""
        module = SimpleModule()

        # Initial state
        assert module.status == ModuleStatus.UNINITIALIZED

        # During/after init
        await module.init()
        assert module.status == ModuleStatus.READY

        # After destroy
        module.destroy()
        assert module.status == ModuleStatus.DESTROYED

    @pytest.mark.asyncio
    async def test_error_status_on_init_failure(self, fresh_bus):
        """Test that status is ERROR after init failure"""
        module = FailingModule()

        try:
            await module.init()
        except ValueError:
            pass

        assert module.status == ModuleStatus.ERROR

    @pytest.mark.asyncio
    async def test_status_in_get_status_dict(self, fresh_bus):
        """Test that get_status includes current status"""
        module = SimpleModule()

        # Before init
        status = module.get_status()
        assert status["status"] == ModuleStatus.UNINITIALIZED.value

        # After init
        await module.init()
        status = module.get_status()
        assert status["status"] == ModuleStatus.READY.value

        # After destroy
        module.destroy()
        status = module.get_status()
        assert status["status"] == ModuleStatus.DESTROYED.value


# ============================================================================
# Module Properties Tests
# ============================================================================


@pytest.mark.unit
class TestTonikaModuleProperties:
    """Test module properties"""

    def test_module_name_and_version(self):
        """Test that module name and version are set correctly"""
        module = SimpleModule(name="TestModule")

        assert module.name == "TestModule"
        assert module.version == "1.0.0"

    def test_module_bus_reference(self, fresh_bus):
        """Test that module has reference to bus (private _bus)"""
        module = SimpleModule()

        # Note: bus is private (_bus), not public
        assert module._bus is fresh_bus
        assert module._bus is TonikaBus()

    def test_module_subscriptions_tracking(self):
        """Test that module tracks its unsubscribe functions"""
        module = SimpleModule()

        # Module tracks unsubscribe functions in _unsubs
        assert hasattr(module, "_unsubs")
        assert isinstance(module._unsubs, list)


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestTonikaModuleIntegration:
    """Integration tests for modules working together"""

    @pytest.mark.asyncio
    async def test_multiple_modules_communication(self, fresh_bus):
        """Test multiple modules communicating via bus"""

        class SenderModule(TonikaModule):
            def __init__(self):
                super().__init__(name="Sender", version="1.0.0")

            async def _initialize(self):
                pass

            def send_message(self, msg):
                self.emit("message", {"text": msg})

        class ReceiverModule(TonikaModule):
            def __init__(self):
                super().__init__(name="Receiver", version="1.0.0")
                self.received_messages = []

            async def _initialize(self):
                self.on("message", self._handle_message)

            def _handle_message(self, event):
                self.received_messages.append(event.detail["text"])

        sender = SenderModule()
        receiver = ReceiverModule()

        await sender.init()
        await receiver.init()

        # Send messages
        sender.send_message("Hello")
        sender.send_message("World")

        # Receiver should have them
        assert len(receiver.received_messages) == 2
        assert receiver.received_messages[0] == "Hello"
        assert receiver.received_messages[1] == "World"

        # Cleanup
        sender.destroy()
        receiver.destroy()

    @pytest.mark.asyncio
    async def test_module_chain_processing(self, fresh_bus):
        """Test chain of modules processing events"""
        results = []

        class InputModule(TonikaModule):
            def __init__(self):
                super().__init__(name="Input", version="1.0.0")

            async def _initialize(self):
                pass

            def process(self, value):
                self.emit("stage1", {"value": value})

        class ProcessorModule(TonikaModule):
            def __init__(self):
                super().__init__(name="Processor", version="1.0.0")

            async def _initialize(self):
                self.on("stage1", self._process)

            def _process(self, event):
                value = event.detail["value"] * 2
                self.emit("stage2", {"value": value})

        class OutputModule(TonikaModule):
            def __init__(self):
                super().__init__(name="Output", version="1.0.0")

            async def _initialize(self):
                self.on("stage2", self._output)

            def _output(self, event):
                results.append(event.detail["value"])

        input_mod = InputModule()
        processor = ProcessorModule()
        output = OutputModule()

        await input_mod.init()
        await processor.init()
        await output.init()

        # Process value through chain
        input_mod.process(10)

        # Should be doubled
        assert len(results) == 1
        assert results[0] == 20

        # Cleanup
        input_mod.destroy()
        processor.destroy()
        output.destroy()

    @pytest.mark.asyncio
    async def test_module_lifecycle_events(self, fresh_bus):
        """Test that module lifecycle generates events"""
        module = EventEmittingModule()

        # Initialize
        await module.init()

        # Check for init event
        events = fresh_bus.get_event_log()
        init_events = [e for e in events if e.type == "module:initialized"]
        assert len(init_events) == 1

        # Destroy
        module.destroy()

        # Check for destroy event
        events = fresh_bus.get_event_log()
        destroy_events = [e for e in events if e.type == "module:destroyed"]
        assert len(destroy_events) == 1
