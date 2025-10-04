"""
Comprehensive test suite for TonikaBus (bus.py)

Tests all functionality of the Bus including:
- Singleton pattern
- Event emission and handling
- Subscription management
- Async operations
- Event logging
- Module registry
- Error handling
- Edge cases

Goblin Law #37: Never Meddle in Another Goblin's Guts
These tests verify the Bus enforces proper communication patterns.
"""

import pytest
import asyncio
from unittest.mock import Mock

from tonika_bus.core.bus import TonikaBus
from tonika_bus.core.events import TonikaEvent, EventMetadata


# ============================================================================
# Singleton Pattern Tests
# ============================================================================

@pytest.mark.unit
class TestTonikaBusSingleton:
    """Test singleton pattern implementation"""
    
    def test_singleton_returns_same_instance(self):
        """Test that multiple calls return the same instance"""
        TonikaBus._instance = None
        TonikaBus._initialized = False
        
        bus1 = TonikaBus()
        bus2 = TonikaBus()
        bus3 = TonikaBus()
        
        assert bus1 is bus2
        assert bus2 is bus3
        assert id(bus1) == id(bus2) == id(bus3)
    
    def test_singleton_initialized_only_once(self):
        """Test that __init__ only runs once"""
        TonikaBus._instance = None
        TonikaBus._initialized = False
        
        bus1 = TonikaBus()
        initial_handlers = bus1.handlers
        
        bus2 = TonikaBus()
        
        # Should be the same object
        assert bus2.handlers is initial_handlers
    
    def test_singleton_persists_state(self, fresh_bus):
        """Test that state persists across multiple references"""
        fresh_bus.emit("test:event", {"data": 123})
        
        bus2 = TonikaBus()
        events = bus2.get_event_log()
        
        assert len(events) == 1
        assert events[0].type == "test:event"


# ============================================================================
# Event Emission Tests
# ============================================================================

@pytest.mark.unit
class TestTonikaBusEmit:
    """Test event emission functionality"""
    
    def test_emit_creates_event(self, fresh_bus):
        """Test that emit creates a proper TonikaEvent"""
        fresh_bus.emit("test:event", {"data": 123}, source="TestSource", version="1.0.0")
        
        events = fresh_bus.get_event_log()
        assert len(events) == 1
        
        event = events[0]
        assert isinstance(event, TonikaEvent)
        assert event.type == "test:event"
        assert event.detail == {"data": 123}
        assert event._meta.source == "TestSource"
        assert event._meta.version == "1.0.0"
    
    def test_emit_with_default_source_and_version(self, fresh_bus):
        """Test emit with default source and version"""
        fresh_bus.emit("test:event", {"data": 456})
        
        event = fresh_bus.get_event_log()[0]
        assert event._meta.source == "unknown"
        assert event._meta.version == "0.0.0"
    
    def test_emit_with_various_detail_types(self, fresh_bus):
        """Test that emit handles various detail types"""
        # Dict
        fresh_bus.emit("test:dict", {"key": "value"})
        # List
        fresh_bus.emit("test:list", [1, 2, 3])
        # String
        fresh_bus.emit("test:string", "simple string")
        # Number
        fresh_bus.emit("test:number", 42)
        # None
        fresh_bus.emit("test:none", None)
        # Boolean
        fresh_bus.emit("test:bool", True)
        
        events = fresh_bus.get_event_log()
        assert len(events) == 6
        assert events[0].detail == {"key": "value"}
        assert events[1].detail == [1, 2, 3]
        assert events[2].detail == "simple string"
        assert events[3].detail == 42
        assert events[4].detail is None
        assert events[5].detail is True
    
    def test_emit_notifies_handlers(self, fresh_bus):
        """Test that emit notifies all subscribed handlers"""
        received_events = []
        
        def handler(event: TonikaEvent):
            received_events.append(event)
        
        fresh_bus.on("test:event", handler)
        fresh_bus.emit("test:event", {"msg": "hello"})
        
        assert len(received_events) == 1
        assert received_events[0].detail == {"msg": "hello"}
    
    def test_emit_notifies_multiple_handlers(self, fresh_bus):
        """Test that emit notifies all handlers for an event type"""
        handler1_calls = []
        handler2_calls = []
        handler3_calls = []
        
        def handler1(event):
            handler1_calls.append(event)
        
        def handler2(event):
            handler2_calls.append(event)
        
        def handler3(event):
            handler3_calls.append(event)
        
        fresh_bus.on("test:event", handler1)
        fresh_bus.on("test:event", handler2)
        fresh_bus.on("test:event", handler3)
        
        fresh_bus.emit("test:event", {"data": 1})
        
        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1
        assert len(handler3_calls) == 1
    
    def test_emit_only_notifies_correct_event_type(self, fresh_bus):
        """Test that handlers only receive their subscribed event types"""
        event_a_count = 0
        event_b_count = 0
        
        def handler_a(event):
            nonlocal event_a_count
            event_a_count += 1
        
        def handler_b(event):
            nonlocal event_b_count
            event_b_count += 1
        
        fresh_bus.on("event:a", handler_a)
        fresh_bus.on("event:b", handler_b)
        
        fresh_bus.emit("event:a", {})
        fresh_bus.emit("event:a", {})
        fresh_bus.emit("event:b", {})
        
        assert event_a_count == 2
        assert event_b_count == 1
    
    def test_emit_handles_handler_exceptions(self, fresh_bus):
        """Test that exceptions in handlers don't break the Bus"""
        successful_handler_called = False
        
        def failing_handler(event):
            raise ValueError("Intentional error")
        
        def successful_handler(event):
            nonlocal successful_handler_called
            successful_handler_called = True
        
        fresh_bus.on("test:event", failing_handler)
        fresh_bus.on("test:event", successful_handler)
        
        # Should not raise
        fresh_bus.emit("test:event", {})
        
        # Other handlers should still be called
        assert successful_handler_called
    
    def test_emit_with_no_handlers(self, fresh_bus):
        """Test that emit works even with no handlers"""
        # Should not raise
        fresh_bus.emit("test:event", {"data": 123})
        
        # Event should still be logged
        events = fresh_bus.get_event_log()
        assert len(events) == 1


# ============================================================================
# Subscription Tests
# ============================================================================

@pytest.mark.unit
class TestTonikaBusSubscription:
    """Test subscription and unsubscription"""
    
    def test_on_returns_unsubscribe_function(self, fresh_bus):
        """Test that on() returns a callable unsubscribe function"""
        def handler(event):
            pass
        
        unsub = fresh_bus.on("test:event", handler)
        
        assert callable(unsub)
    
    def test_on_registers_handler(self, fresh_bus):
        """Test that on() registers the handler"""
        def handler(event):
            pass
        
        fresh_bus.on("test:event", handler)
        
        assert "test:event" in fresh_bus.handlers
        assert handler in fresh_bus.handlers["test:event"]
    
    def test_unsubscribe_removes_handler(self, fresh_bus):
        """Test that calling unsubscribe removes the handler"""
        call_count = 0
        
        def handler(event):
            nonlocal call_count
            call_count += 1
        
        unsub = fresh_bus.on("test:event", handler)
        
        fresh_bus.emit("test:event", {})
        assert call_count == 1
        
        unsub()
        
        fresh_bus.emit("test:event", {})
        assert call_count == 1  # Should not increase
    
    def test_unsubscribe_only_removes_specific_handler(self, fresh_bus):
        """Test that unsubscribe only removes the specific handler"""
        handler1_count = 0
        handler2_count = 0
        
        def handler1(event):
            nonlocal handler1_count
            handler1_count += 1
        
        def handler2(event):
            nonlocal handler2_count
            handler2_count += 1
        
        unsub1 = fresh_bus.on("test:event", handler1)
        fresh_bus.on("test:event", handler2)
        
        unsub1()
        
        fresh_bus.emit("test:event", {})
        
        assert handler1_count == 0
        assert handler2_count == 1
    
    def test_unsubscribe_is_idempotent(self, fresh_bus):
        """Test that calling unsubscribe multiple times is safe"""
        def handler(event):
            pass
        
        unsub = fresh_bus.on("test:event", handler)
        
        # Should not raise
        unsub()
        unsub()
        unsub()
    
    def test_once_only_fires_once(self, fresh_bus):
        """Test that once() only fires handler once"""
        call_count = 0
        
        def handler(event):
            nonlocal call_count
            call_count += 1
        
        fresh_bus.once("test:event", handler)
        
        fresh_bus.emit("test:event", {})
        fresh_bus.emit("test:event", {})
        fresh_bus.emit("test:event", {})
        
        assert call_count == 1
    
    def test_once_returns_unsubscribe_function(self, fresh_bus):
        """Test that once() returns an unsubscribe function"""
        def handler(event):
            pass
        
        unsub = fresh_bus.once("test:event", handler)
        
        assert callable(unsub)
    
    def test_once_can_be_cancelled_early(self, fresh_bus):
        """Test that once() subscription can be cancelled before firing"""
        call_count = 0
        
        def handler(event):
            nonlocal call_count
            call_count += 1
        
        unsub = fresh_bus.once("test:event", handler)
        unsub()
        
        fresh_bus.emit("test:event", {})
        
        assert call_count == 0
    
    def test_multiple_subscriptions_to_same_event(self, fresh_bus):
        """Test multiple handlers for the same event type"""
        calls = []
        
        def handler1(event):
            calls.append("handler1")
        
        def handler2(event):
            calls.append("handler2")
        
        def handler3(event):
            calls.append("handler3")
        
        fresh_bus.on("test:event", handler1)
        fresh_bus.on("test:event", handler2)
        fresh_bus.on("test:event", handler3)
        
        fresh_bus.emit("test:event", {})
        
        assert len(calls) == 3
        assert "handler1" in calls
        assert "handler2" in calls
        assert "handler3" in calls


# ============================================================================
# Async Tests
# ============================================================================

@pytest.mark.unit
class TestTonikaBusAsync:
    """Test async functionality"""
    
    @pytest.mark.asyncio
    async def test_wait_for_resolves_on_event(self, fresh_bus):
        """Test that wait_for resolves when event is emitted"""
        async def emit_later():
            await asyncio.sleep(0.1)
            fresh_bus.emit("test:event", {"data": 42})
        
        # Start emitting in background
        asyncio.create_task(emit_later())
        
        # Wait for event
        event = await fresh_bus.wait_for("test:event", timeout_ms=1000)
        
        assert event.type == "test:event"
        assert event.detail == {"data": 42}
    
    @pytest.mark.asyncio
    async def test_wait_for_timeout(self, fresh_bus):
        """Test that wait_for times out if event not emitted"""
        with pytest.raises(asyncio.TimeoutError):
            await fresh_bus.wait_for("nonexistent:event", timeout_ms=100)
    
    @pytest.mark.asyncio
    async def test_wait_for_without_timeout(self, fresh_bus):
        """Test wait_for without timeout"""
        async def emit_soon():
            await asyncio.sleep(0.05)
            fresh_bus.emit("test:event", {"data": 123})
        
        asyncio.create_task(emit_soon())
        
        event = await fresh_bus.wait_for("test:event")
        
        assert event.detail == {"data": 123}
    
    @pytest.mark.asyncio
    async def test_multiple_wait_for_same_event(self, fresh_bus):
        """Test multiple coroutines waiting for the same event"""
        results = []
        
        async def waiter(name):
            event = await fresh_bus.wait_for("test:event", timeout_ms=1000)
            results.append((name, event.detail))
        
        # Start multiple waiters
        task1 = asyncio.create_task(waiter("waiter1"))
        task2 = asyncio.create_task(waiter("waiter2"))
        task3 = asyncio.create_task(waiter("waiter3"))
        
        # Give them time to start waiting
        await asyncio.sleep(0.05)
        
        # Emit event
        fresh_bus.emit("test:event", {"data": "shared"})
        
        # Wait for all to complete
        await asyncio.gather(task1, task2, task3)
        
        assert len(results) == 3
        assert all(detail == {"data": "shared"} for _, detail in results)


# ============================================================================
# Event Log Tests
# ============================================================================

@pytest.mark.unit
class TestTonikaBusEventLog:
    """Test event logging functionality"""
    
    def test_event_log_stores_events(self, fresh_bus):
        """Test that events are stored in log"""
        fresh_bus.emit("event:1", {"n": 1})
        fresh_bus.emit("event:2", {"n": 2})
        fresh_bus.emit("event:3", {"n": 3})
        
        log = fresh_bus.get_event_log()
        assert len(log) == 3
        assert log[0].type == "event:1"
        assert log[1].type == "event:2"
        assert log[2].type == "event:3"
    
    def test_event_log_preserves_order(self, fresh_bus):
        """Test that event log preserves emission order"""
        for i in range(10):
            fresh_bus.emit(f"event:{i}", {"index": i})
        
        log = fresh_bus.get_event_log()
        
        for i, event in enumerate(log):
            assert event.detail["index"] == i
    
    def test_event_log_limit(self, fresh_bus):
        """Test that get_event_log respects limit parameter"""
        for i in range(20):
            fresh_bus.emit(f"event:{i}", {})
        
        log = fresh_bus.get_event_log(limit=5)
        assert len(log) == 5
        
        # Should return the LAST 5 events
        assert log[0].type == "event:15"
        assert log[4].type == "event:19"
    
    def test_event_log_bounded_size(self, fresh_bus):
        """Test that event log doesn't grow unbounded"""
        max_len = fresh_bus._event_log_maxlen
        
        # Emit more events than the max
        for i in range(max_len + 100):
            fresh_bus.emit(f"event:{i}", {})
        
        log = fresh_bus.get_event_log()
        
        # Should be capped at max length
        assert len(log) == max_len
        
        # Should contain the MOST RECENT events
        assert log[-1].type == f"event:{max_len + 99}"
    
    def test_clear_event_log(self, fresh_bus):
        """Test that clear_event_log empties the log"""
        fresh_bus.emit("event:1", {})
        fresh_bus.emit("event:2", {})
        
        fresh_bus.clear_event_log()
        
        log = fresh_bus.get_event_log()
        assert len(log) == 0
    
    def test_get_event_log_returns_copy(self, fresh_bus):
        """Test that get_event_log returns a copy, not the internal deque"""
        fresh_bus.emit("event:1", {})
        
        log1 = fresh_bus.get_event_log()
        log2 = fresh_bus.get_event_log()
        
        # Should be different list objects
        assert log1 is not log2
        
        # But contain the same events
        assert log1[0] is log2[0]


# ============================================================================
# Module Registry Tests
# ============================================================================

@pytest.mark.unit
class TestTonikaBusModuleRegistry:
    """Test module registry functionality"""
    
    def test_register_module(self, fresh_bus):
        """Test registering a module"""
        class MockModule:
            name = "TestModule"
            version = "1.0.0"
        
        module = MockModule()
        fresh_bus.register_module(module)
        
        assert "TestModule" in fresh_bus.list_modules()
        assert fresh_bus.get_module("TestModule") is module
    
    def test_register_multiple_modules(self, fresh_bus):
        """Test registering multiple modules"""
        class MockModule:
            def __init__(self, name):
                self.name = name
                self.version = "1.0.0"
        
        mod1 = MockModule("Module1")
        mod2 = MockModule("Module2")
        mod3 = MockModule("Module3")
        
        fresh_bus.register_module(mod1)
        fresh_bus.register_module(mod2)
        fresh_bus.register_module(mod3)
        
        modules = fresh_bus.list_modules()
        assert len(modules) == 3
        assert "Module1" in modules
        assert "Module2" in modules
        assert "Module3" in modules
    
    def test_unregister_module(self, fresh_bus):
        """Test unregistering a module"""
        class MockModule:
            name = "TestModule"
            version = "1.0.0"
        
        module = MockModule()
        fresh_bus.register_module(module)
        fresh_bus.unregister_module("TestModule")
        
        assert "TestModule" not in fresh_bus.list_modules()
        assert fresh_bus.get_module("TestModule") is None
    
    def test_get_nonexistent_module(self, fresh_bus):
        """Test getting a module that doesn't exist"""
        result = fresh_bus.get_module("NonexistentModule")
        assert result is None
    
    def test_unregister_nonexistent_module(self, fresh_bus):
        """Test unregistering a module that doesn't exist (should not error)"""
        # Should not raise
        fresh_bus.unregister_module("NonexistentModule")
    
    def test_register_overwrites_existing(self, fresh_bus):
        """Test that registering with same name overwrites"""
        class MockModule:
            def __init__(self, name, data):
                self.name = name
                self.version = "1.0.0"
                self.data = data
        
        mod1 = MockModule("TestModule", "first")
        mod2 = MockModule("TestModule", "second")
        
        fresh_bus.register_module(mod1)
        fresh_bus.register_module(mod2)
        
        retrieved = fresh_bus.get_module("TestModule")
        assert retrieved.data == "second"


# ============================================================================
# Debug Mode Tests
# ============================================================================

@pytest.mark.unit
class TestTonikaBusDebug:
    """Test debug mode functionality"""
    
    def test_set_debug_enables_debug(self, fresh_bus):
        """Test that set_debug enables debug mode"""
        fresh_bus.set_debug(True)
        assert fresh_bus.debug is True
    
    def test_set_debug_disables_debug(self, fresh_bus):
        """Test that set_debug can disable debug mode"""
        fresh_bus.set_debug(True)
        fresh_bus.set_debug(False)
        assert fresh_bus.debug is False
    
    def test_debug_mode_affects_logging(self, fresh_bus):
        """Test that debug mode changes logger level"""
        import logging
        
        fresh_bus.set_debug(True)
        assert fresh_bus.logger.level == logging.DEBUG
        
        fresh_bus.set_debug(False)
        assert fresh_bus.logger.level == logging.INFO


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

@pytest.mark.unit
class TestTonikaBusEdgeCases:
    """Test edge cases and error handling"""
    
    def test_emit_during_handler_execution(self, fresh_bus):
        """Test emitting events from within a handler"""
        call_order = []
        
        def handler1(event):
            call_order.append("handler1")
            fresh_bus.emit("event:b", {})
        
        def handler2(event):
            call_order.append("handler2")
        
        fresh_bus.on("event:a", handler1)
        fresh_bus.on("event:b", handler2)
        
        fresh_bus.emit("event:a", {})
        
        assert "handler1" in call_order
        assert "handler2" in call_order
    
    def test_unsubscribe_during_handler_execution(self, fresh_bus):
        """Test unsubscribing from within a handler"""
        call_count = 0
        unsub_func = None
        
        def handler(event):
            nonlocal call_count
            call_count += 1
            if unsub_func:
                unsub_func()
        
        unsub_func = fresh_bus.on("test:event", handler)
        
        fresh_bus.emit("test:event", {})
        fresh_bus.emit("test:event", {})
        
        # Should only be called once
        assert call_count == 1
    
    def test_empty_event_type(self, fresh_bus):
        """Test emitting event with empty string type"""
        fresh_bus.emit("", {"data": 123})
        
        events = fresh_bus.get_event_log()
        assert len(events) == 1
        assert events[0].type == ""
    
    def test_special_characters_in_event_type(self, fresh_bus):
        """Test event types with special characters"""
        special_types = [
            "event:with:colons",
            "event-with-dashes",
            "event_with_underscores",
            "event.with.dots",
            "event/with/slashes",
            "event:123:numbers",
        ]
        
        for event_type in special_types:
            fresh_bus.emit(event_type, {})
        
        events = fresh_bus.get_event_log()
        assert len(events) == len(special_types)
    
    def test_large_event_detail(self, fresh_bus):
        """Test emitting event with large detail payload"""
        large_detail = {"data": "x" * 10000, "list": list(range(1000))}
        
        fresh_bus.emit("test:large", large_detail)
        
        event = fresh_bus.get_event_log()[0]
        assert len(event.detail["data"]) == 10000
        assert len(event.detail["list"]) == 1000


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestTonikaBusIntegration:
    """Integration tests for complex scenarios"""
    
    def test_full_event_flow(self, fresh_bus):
        """Test complete event flow from emission to handling"""
        results = []
        
        def processor(event):
            results.append(f"processed:{event.detail['value']}")
            fresh_bus.emit("processed", {"original": event.detail['value']})
        
        def logger(event):
            results.append(f"logged:{event.detail['original']}")
        
        fresh_bus.on("input", processor)
        fresh_bus.on("processed", logger)
        
        fresh_bus.emit("input", {"value": 42})
        
        assert "processed:42" in results
        assert "logged:42" in results
    
    @pytest.mark.asyncio
    async def test_async_event_chain(self, fresh_bus):
        """Test async event chains"""
        results = []
        
        async def step1():
            await fresh_bus.wait_for("start", timeout_ms=1000)
            results.append("step1")
            fresh_bus.emit("step1:done", {})
        
        async def step2():
            await fresh_bus.wait_for("step1:done", timeout_ms=1000)
            results.append("step2")
            fresh_bus.emit("step2:done", {})
        
        async def step3():
            await fresh_bus.wait_for("step2:done", timeout_ms=1000)
            results.append("step3")
        
        # Start all tasks
        task1 = asyncio.create_task(step1())
        task2 = asyncio.create_task(step2())
        task3 = asyncio.create_task(step3())
        
        # Give them time to start waiting
        await asyncio.sleep(0.05)
        
        # Trigger the chain
        fresh_bus.emit("start", {})
        
        # Wait for completion
        await asyncio.gather(task1, task2, task3)
        
        assert results == ["step1", "step2", "step3"]


