# Testing Guide

**Comprehensive guide to testing Tonika modules**

This guide covers testing strategies, best practices, and common patterns for ensuring your Tonika modules work correctly.

---

## Table of Contents

- [Overview](#overview)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Testing Your Modules](#testing-your-modules)
- [Test Fixtures](#test-fixtures)
- [Common Test Patterns](#common-test-patterns)
- [Async Testing](#async-testing)
- [Best Practices](#best-practices)
- [CI/CD Integration](#cicd-integration)

---

## Overview

### Test Framework

Tonika Bus uses **pytest** for testing with these key plugins:

- **pytest** - Core testing framework
- **pytest-asyncio** - Async test support
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Mocking utilities

### Test Organization

Tests are organized by concern:

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_bus.py          # TonikaBus tests
├── test_events.py       # Event structure tests
└── test_module.py       # TonikaModule tests
```

### Test Markers

Tests are marked for selective execution:

- `@pytest.mark.unit` - Fast unit tests (no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require hardware)
- `@pytest.mark.slow` - Slow tests (skip with `-m 'not slow'`)
- `@pytest.mark.midi` - Tests requiring MIDI hardware

---

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov

# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m 'not slow'
```

### Coverage Reports

```bash
# Terminal coverage report
pytest --cov=tonika_bus --cov-report=term-missing

# HTML coverage report
pytest --cov=tonika_bus --cov-report=html
open htmlcov/index.html

# XML coverage report (for CI)
pytest --cov=tonika_bus --cov-report=xml
```

### Stop on First Failure

```bash
# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3
```

### Run Specific Tests

```bash
# Run a specific file
pytest tests/test_bus.py

# Run a specific test class
pytest tests/test_bus.py::TestTonikaBusEmit

# Run a specific test function
pytest tests/test_bus.py::TestTonikaBusEmit::test_emit_creates_event
```

---

## Test Structure

### Anatomy of a Test

```python
import pytest
from tonika_bus import TonikaBus, TonikaModule

@pytest.mark.unit
class TestMyFeature:
    """Test my feature"""
    
    def test_basic_functionality(self, fresh_bus):
        """Test that basic functionality works"""
        # Arrange: Set up test conditions
        bus = fresh_bus
        
        # Act: Perform the action
        bus.emit("test:event", {"data": 123})
        
        # Assert: Verify the result
        events = bus.get_event_log()
        assert len(events) == 1
        assert events[0].type == "test:event"
```

### Test Class Organization

Group related tests in classes:

```python
@pytest.mark.unit
class TestTonikaBusEmit:
    """Test event emission functionality"""
    
    def test_emit_creates_event(self, fresh_bus):
        """Test that emit creates a proper TonikaEvent"""
        # ... test code ...
    
    def test_emit_notifies_handlers(self, fresh_bus):
        """Test that emit notifies all subscribed handlers"""
        # ... test code ...
    
    def test_emit_handles_exceptions(self, fresh_bus):
        """Test that exceptions in handlers don't break the Bus"""
        # ... test code ...
```

---

## Testing Your Modules

### Basic Module Test

```python
import pytest
from tonika_bus import TonikaBus, TonikaModule

class CounterModule(TonikaModule):
    async def _initialize(self):
        self.count = 0
        self.on("counter:increment", self.increment)
    
    def increment(self, event):
        self.count += 1
        self.emit("counter:changed", {"count": self.count})

@pytest.mark.asyncio
async def test_counter_module(fresh_bus):
    """Test counter module increments correctly"""
    # Create module
    counter = CounterModule(name="Counter", version="1.0.0")
    await counter.init()
    
    # Test increment
    fresh_bus.emit("counter:increment", {})
    assert counter.count == 1
    
    # Test event emission
    events = fresh_bus.get_event_log()
    changed_events = [e for e in events if e.type == "counter:changed"]
    assert len(changed_events) == 1
    assert changed_events[0].detail["count"] == 1
    
    # Cleanup
    counter.destroy()
```

### Testing Event Handlers

```python
@pytest.mark.asyncio
async def test_module_receives_events(fresh_bus):
    """Test that module receives subscribed events"""
    received_events = []
    
    class ListenerModule(TonikaModule):
        async def _initialize(self):
            self.on("test:event", self.handle)
        
        def handle(self, event):
            received_events.append(event)
    
    module = ListenerModule(name="Listener", version="1.0.0")
    await module.init()
    
    # Emit event
    fresh_bus.emit("test:event", {"data": 123})
    
    # Verify received
    assert len(received_events) == 1
    assert received_events[0].detail["data"] == 123
    
    module.destroy()
```

### Testing Module Lifecycle

```python
@pytest.mark.asyncio
async def test_module_lifecycle(fresh_bus):
    """Test module lifecycle transitions"""
    from tonika_bus.core.events import ModuleStatus
    
    class SimpleModule(TonikaModule):
        async def _initialize(self):
            pass
    
    module = SimpleModule(name="Test", version="1.0.0")
    
    # Initial state
    assert module.status == ModuleStatus.UNINITIALIZED
    
    # After init
    await module.init()
    assert module.status == ModuleStatus.READY
    
    # After destroy
    module.destroy()
    assert module.status == ModuleStatus.DESTROYED
```

### Testing Module Dependencies

```python
@pytest.mark.asyncio
async def test_module_waits_for_dependency(fresh_bus):
    """Test module can wait for dependencies"""
    
    class DatabaseModule(TonikaModule):
        async def _initialize(self):
            await asyncio.sleep(0.1)
            self.emit("database:ready", {})
    
    class ApiModule(TonikaModule):
        async def _initialize(self):
            await self.wait_for("database:ready", timeout_ms=1000)
            self.ready = True
    
    db = DatabaseModule(name="Database", version="1.0.0")
    api = ApiModule(name="API", version="1.0.0")
    
    # Start both (API will wait for DB)
    await asyncio.gather(
        db.init(),
        api.init()
    )
    
    # Verify both ready
    assert db.status == ModuleStatus.READY
    assert api.status == ModuleStatus.READY
    assert api.ready is True
    
    db.destroy()
    api.destroy()
```

---

## Test Fixtures

### Fresh Bus Fixture

The `fresh_bus` fixture provides a clean Bus for each test:

```python
# In conftest.py
@pytest.fixture
def fresh_bus():
    """Provide a fresh Bus instance for each test"""
    TonikaBus._instance = None
    TonikaBus._initialized = False
    bus = TonikaBus()
    yield bus
    bus.clear_event_log()
```

Usage:
```python
def test_something(fresh_bus):
    """Test that uses a fresh bus"""
    fresh_bus.emit("test:event", {})
    assert len(fresh_bus.get_event_log()) == 1
```

### Debug Bus Fixture

The `bus_with_debug` fixture provides a Bus with debug enabled:

```python
# In conftest.py
@pytest.fixture
def bus_with_debug(fresh_bus):
    """Provide a Bus with debug mode enabled"""
    fresh_bus.set_debug(True)
    return fresh_bus
```

Usage:
```python
def test_debug_logging(bus_with_debug, caplog):
    """Test debug logging"""
    bus_with_debug.emit("test:event", {})
    assert "EMIT" in caplog.text
```

### Custom Fixtures

Create fixtures for common test setups:

```python
@pytest.fixture
async def counter_module(fresh_bus):
    """Provide an initialized counter module"""
    module = CounterModule(name="Counter", version="1.0.0")
    await module.init()
    yield module
    module.destroy()

def test_with_counter(counter_module):
    """Test using counter fixture"""
    assert counter_module.count == 0
```

---

## Common Test Patterns

### Testing Event Emission

```python
def test_module_emits_event(fresh_bus):
    """Test that module emits expected event"""
    
    class EmitterModule(TonikaModule):
        async def _initialize(self):
            pass
        
        def do_something(self):
            self.emit("action:done", {"result": 42})
    
    module = EmitterModule(name="Emitter", version="1.0.0")
    await module.init()
    
    # Trigger action
    module.do_something()
    
    # Check event log
    events = fresh_bus.get_event_log()
    action_events = [e for e in events if e.type == "action:done"]
    
    assert len(action_events) == 1
    assert action_events[0].detail["result"] == 42
    assert action_events[0]._meta.source == "Emitter"
    
    module.destroy()
```

### Testing Multiple Subscribers

```python
def test_multiple_subscribers(fresh_bus):
    """Test that event reaches multiple subscribers"""
    
    received1 = []
    received2 = []
    
    class Subscriber1(TonikaModule):
        async def _initialize(self):
            self.on("broadcast", lambda e: received1.append(e))
    
    class Subscriber2(TonikaModule):
        async def _initialize(self):
            self.on("broadcast", lambda e: received2.append(e))
    
    sub1 = Subscriber1(name="Sub1", version="1.0.0")
    sub2 = Subscriber2(name="Sub2", version="1.0.0")
    
    await sub1.init()
    await sub2.init()
    
    # Emit broadcast
    fresh_bus.emit("broadcast", {"msg": "hello"})
    
    # Both should receive
    assert len(received1) == 1
    assert len(received2) == 1
    
    sub1.destroy()
    sub2.destroy()
```

### Testing Request-Response

```python
def test_request_response_pattern(fresh_bus):
    """Test request-response pattern"""
    
    class Provider(TonikaModule):
        async def _initialize(self):
            self.on("data:request", self.handle_request)
        
        def handle_request(self, event):
            request_id = event.detail["request_id"]
            self.emit("data:response", {
                "request_id": request_id,
                "value": 42
            })
    
    class Consumer(TonikaModule):
        async def _initialize(self):
            self.on("data:response", self.handle_response)
            self.responses = {}
        
        def handle_response(self, event):
            request_id = event.detail["request_id"]
            self.responses[request_id] = event.detail["value"]
    
    provider = Provider(name="Provider", version="1.0.0")
    consumer = Consumer(name="Consumer", version="1.0.0")
    
    await provider.init()
    await consumer.init()
    
    # Request data
    fresh_bus.emit("data:request", {"request_id": "req123"})
    
    # Check response
    assert "req123" in consumer.responses
    assert consumer.responses["req123"] == 42
    
    provider.destroy()
    consumer.destroy()
```

### Testing Error Handling

```python
def test_handler_exception_doesnt_break_bus(fresh_bus):
    """Test that exceptions in handlers don't break the Bus"""
    
    successful_called = False
    
    def failing_handler(event):
        raise ValueError("Intentional error")
    
    def successful_handler(event):
        nonlocal successful_called
        successful_called = True
    
    fresh_bus.on("test:event", failing_handler)
    fresh_bus.on("test:event", successful_handler)
    
    # Should not raise
    fresh_bus.emit("test:event", {})
    
    # Other handlers should still be called
    assert successful_called
```

---

## Async Testing

### Basic Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation(fresh_bus):
    """Test async operations"""
    
    class AsyncModule(TonikaModule):
        async def _initialize(self):
            await asyncio.sleep(0.01)
            self.ready = True
    
    module = AsyncModule(name="Async", version="1.0.0")
    await module.init()
    
    assert module.ready is True
    
    module.destroy()
```

### Testing wait_for()

```python
@pytest.mark.asyncio
async def test_wait_for_event(fresh_bus):
    """Test waiting for events"""
    
    async def emit_later():
        await asyncio.sleep(0.1)
        fresh_bus.emit("delayed:event", {"data": 123})
    
    # Start emitting in background
    asyncio.create_task(emit_later())
    
    # Wait for event
    event = await fresh_bus.wait_for("delayed:event", timeout_ms=1000)
    
    assert event.type == "delayed:event"
    assert event.detail["data"] == 123
```

### Testing Timeouts

```python
@pytest.mark.asyncio
async def test_wait_for_timeout(fresh_bus):
    """Test that wait_for times out correctly"""
    
    with pytest.raises(asyncio.TimeoutError):
        await fresh_bus.wait_for("nonexistent:event", timeout_ms=100)
```

### Testing Async Handlers

```python
@pytest.mark.asyncio
async def test_async_handler(fresh_bus):
    """Test async event handlers"""
    
    results = []
    
    async def async_handler(event):
        await asyncio.sleep(0.01)
        results.append(event.detail)
    
    fresh_bus.on("test:event", async_handler)
    fresh_bus.emit("test:event", {"data": 123})
    
    # Wait for async handler to complete
    await asyncio.sleep(0.05)
    
    assert len(results) == 1
    assert results[0]["data"] == 123
```

---

## Best Practices

### 1. Use Fresh Bus Fixture

Always use `fresh_bus` fixture to ensure test isolation:

```python
# ✅ GOOD: Isolated test
def test_something(fresh_bus):
    fresh_bus.emit("test:event", {})
    # Clean slate every time

# ❌ BAD: Shared state
def test_something():
    bus = TonikaBus()
    # Might have state from previous tests!
```

### 2. Always Clean Up Modules

```python
# ✅ GOOD: Cleanup in finally or fixture
@pytest.fixture
async def my_module(fresh_bus):
    module = MyModule(name="Test", version="1.0.0")
    await module.init()
    yield module
    module.destroy()  # Always cleaned up

# ❌ BAD: No cleanup
async def test_module(fresh_bus):
    module = MyModule(name="Test", version="1.0.0")
    await module.init()
    # Module leaked!
```

### 3. Test One Thing Per Test

```python
# ✅ GOOD: Focused test
def test_increment_increases_count(counter_module):
    """Test that increment increases count"""
    counter_module.increment()
    assert counter_module.count == 1

# ❌ BAD: Testing multiple things
def test_counter_everything(counter_module):
    """Test counter"""
    counter_module.increment()
    assert counter_module.count == 1
    counter_module.reset()
    assert counter_module.count == 0
    counter_module.set(50)
    assert counter_module.count == 50
    # Too much in one test!
```

### 4. Use Descriptive Test Names

```python
# ✅ GOOD: Clear intent
def test_emit_creates_event_with_correct_metadata(fresh_bus):
    """Test that emit creates event with source and version"""
    # ...

# ❌ BAD: Vague
def test_emit(fresh_bus):
    """Test emit"""
    # ...
```

### 5. Use Markers Appropriately

```python
# ✅ GOOD: Marked appropriately
@pytest.mark.unit
def test_event_creation():
    """Fast unit test"""
    # ...

@pytest.mark.integration
@pytest.mark.midi
def test_midi_input():
    """Integration test requiring MIDI hardware"""
    # ...

# ❌ BAD: No markers
def test_something():
    # Hard to run selectively
    # ...
```

### 6. Test Edge Cases

```python
def test_counter_handles_negative_increment(counter_module):
    """Test that counter handles negative increments"""
    counter_module.increment(amount=-5)
    assert counter_module.count == -5

def test_counter_handles_zero_increment(counter_module):
    """Test that counter handles zero increment"""
    counter_module.increment(amount=0)
    assert counter_module.count == 0

def test_counter_handles_large_increment(counter_module):
    """Test that counter handles large increments"""
    counter_module.increment(amount=1000000)
    assert counter_module.count == 1000000
```

---

## CI/CD Integration

### GitHub Actions Configuration

The project uses GitHub Actions for CI. See `.github/workflows/ci.yml`:

```yaml
- name: Run tests with pytest
  run: |
    pytest --cov=tonika_bus --cov-report=xml --cov-report=term-missing -v
```

### Running Tests Locally Like CI

```bash
# Run exactly what CI runs
pytest --cov=tonika_bus --cov-report=xml --cov-report=term-missing -v

# Check linting (ruff)
ruff check src/ tests/

# Check type hints (mypy)
mypy src/tonika_bus/core/
```

### Coverage Requirements

The project aims for high coverage. Check coverage with:

```bash
pytest --cov=tonika_bus --cov-report=term-missing
```

Coverage reports are automatically uploaded to Coveralls on CI.

---

## See Also

- **[Bus Architecture Guide](BUS_GUIDE.md)** - Understanding the Bus
- **[Writing Your First Module](FIRST_MODULE.md)** - Module basics
- **[Goblin Laws with Examples](goblin_laws_examples.md)** - Design principles
- **[pytest documentation](https://docs.pytest.org/)** - Official pytest docs
- **[pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)** - Async testing

---

**🧌 Test your Goblins thoroughly!** 🎵

*Remember: Untested code is broken code!*