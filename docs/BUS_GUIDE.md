# Tonika Bus Architecture Guide

**Complete guide to the Tonika Bus event system**

The Tonika Bus is the communication backbone of Tonika—a centralized event broker implementing the publish-subscribe pattern. This guide covers everything you need to know to work with the Bus.

---

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [TonikaBus API](#tonikabus-api)
- [TonikaModule API](#tonikamodule-api)
- [Event Structures](#event-structures)
- [Async Support](#async-support)
- [Event Naming Conventions](#event-naming-conventions)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)

---

## Overview

### What is the Bus?

The Tonika Bus is a **singleton event broker** that enables complete decoupling between modules. No module ever calls another module's methods directly—all communication flows through events.

```python
# Traditional (tight coupling)
sequencer.synth.play(note)  # ❌ Direct call

# Bus (zero coupling)
bus.emit("midi:note-on", {"note": note})  # ✅ Event
```

### Why Pub/Sub?

**Publishers** emit events without knowing who's listening:
```python
class Piano(TonikaModule):
    def key_pressed(self, note):
        self.emit("midi:note-on", {"note": note})
        # Piano doesn't know who's listening!
```

**Subscribers** listen without knowing who's sending:
```python
class Synth(TonikaModule):
    async def _initialize(self):
        self.on("midi:note-on", self.play_sound)
        # Synth doesn't know who sent the note!
```

**Key Benefits:**
- ✅ Zero coupling between modules
- ✅ Easy to add new listeners
- ✅ Simple to swap implementations
- ✅ Trivial to test
- ✅ Observable system state (event log)

### Goblin Law Enforcement

The Bus enforces **Goblin Law #37: Never Meddle in Another Goblin's Guts**. Modules must communicate through events, never direct method calls.

See [Goblin Laws with Examples](goblin_laws_examples.md) for detailed design principles.

---

## Core Concepts

### The Singleton Pattern

**There is only ONE Bus.** No matter how many times you call `TonikaBus()`, you get the same instance.

```python
from tonika_bus import TonikaBus

bus1 = TonikaBus()
bus2 = TonikaBus()

assert bus1 is bus2  # ✅ True! Same Bus!
```

**Why singleton?**
- Single source of truth for all events
- No "which bus?" confusion
- Easier debugging and testing

### Events

Every message on the Bus is a `TonikaEvent` with three parts:

```python
event.type      # What happened? (e.g., "midi:note-on")
event.detail    # The data (e.g., {"note": 60, "velocity": 100})
event._meta     # Who sent it? When? (timestamp, source, version)
```

Events are created automatically when you emit:

```python
# You write:
bus.emit("midi:note-on", {"note": 60}, source="MidiInput", version="1.0.0")

# Bus creates:
TonikaEvent(
    type="midi:note-on",
    detail={"note": 60},
    _meta=EventMetadata(
        timestamp=1704067200000,  # Unix milliseconds
        source="MidiInput",
        version="1.0.0"
    )
)
```

### Module Lifecycle

Every `TonikaModule` follows the same lifecycle:

```
Constructor → UNINITIALIZED
    ↓
init() → INITIALIZING → "module:initializing" event
    ↓
_initialize() → custom setup
    ↓
READY → "module:ready" event
    ↓
Normal operation → emit/receive events
    ↓
destroy() → cleanup → "module:destroyed" → DESTROYED
```

See **Goblin Law #41: Only One Drumbeat of Readiness** in [Goblin Laws](goblin_laws_examples.md).

---

## TonikaBus API

### Getting the Bus

```python
from tonika_bus import TonikaBus

bus = TonikaBus()  # Always returns the same instance
```

### emit(event_type, detail, source="unknown", version="0.0.0")

Send an event to all subscribers.

```python
bus.emit("midi:note-on", {"note": 60, "velocity": 100})
```

**Parameters:**
- `event_type` (str): Event type (e.g., `"midi:note-on"`)
- `detail` (Any): Event payload (usually dict)
- `source` (str): Who sent it (auto-filled by modules)
- `version` (str): Sender version (auto-filled by modules)

**Returns:** None

**Note:** Handlers are called synchronously in registration order. Exceptions in handlers are logged but don't stop other handlers.

### on(event_type, handler) → unsubscribe_function

Subscribe to an event type.

```python
def my_handler(event):
    print(f"Got: {event.detail}")

# Subscribe
unsub = bus.on("midi:note-on", my_handler)

# Later, unsubscribe
unsub()
```

**Parameters:**
- `event_type` (str): Event type to listen for
- `handler` (Callable[[TonikaEvent], None]): Function to call (sync or async)

**Returns:** Callable[[], None] - Unsubscribe function

**Handler Signature:**
```python
def handler(event: TonikaEvent) -> None:
    # Sync handler
    pass

async def async_handler(event: TonikaEvent) -> None:
    # Async handler (scheduled with create_task if loop running)
    pass
```

### once(event_type, handler) → unsubscribe_function

Subscribe to an event, but only fire once.

```python
def one_time(event):
    print("This only prints once!")

bus.once("module:ready", one_time)

bus.emit("module:ready", {})  # Handler called
bus.emit("module:ready", {})  # Handler NOT called
```

**Parameters:** Same as `on()`

**Returns:** Unsubscribe function (to cancel before first fire)

### async wait_for(event_type, timeout_ms=None) → TonikaEvent

Wait for a specific event before continuing (async).

```python
# Wait for MIDI to be ready
event = await bus.wait_for("midi:ready", timeout_ms=5000)
print(f"MIDI ready at {event._meta.timestamp}")
```

**Parameters:**
- `event_type` (str): Event type to wait for
- `timeout_ms` (int | None): Timeout in milliseconds (None = wait forever)

**Returns:** TonikaEvent - The event that was received

**Raises:** `asyncio.TimeoutError` if timeout is reached

**⚠️ Warning:** If you call `wait_for()` without a timeout and the event never arrives, the future will remain in memory indefinitely. Always use a timeout in production code.

### get_event_log(limit=None) → List[TonikaEvent]

Get recent events from the log (for debugging).

```python
# Get last 10 events
recent = bus.get_event_log(limit=10)
for event in recent:
    print(f"{event.type} from {event._meta.source}")
```

**Parameters:**
- `limit` (int | None): Max events to return (None = all, up to 1000)

**Returns:** List[TonikaEvent] - Events in chronological order

**Note:** Event log is bounded at 1000 events to prevent unbounded memory growth.

### clear_event_log()

Clear the event log (useful for long-running apps).

```python
bus.clear_event_log()
```

### set_debug(enabled: bool)

Enable or disable debug logging.

```python
bus.set_debug(True)  # See all events in console
```

When enabled, you'll see:
```
📢 EMIT: TonikaEvent(type='midi:note-on', source='Piano', ...)
👂 SUBSCRIBE: midi:note-on (total handlers: 2)
🔇 UNSUBSCRIBE: midi:note-on
```

### Module Registry Methods

**register_module(module: TonikaModule)**

Register a module (called automatically by module constructor).

```python
# You don't call this directly
# It happens automatically when you create a module
```

**unregister_module(name: str)**

Unregister a module (called automatically by `module.destroy()`).

**get_module(name: str) → TonikaModule | None**

Get a module by name (for inspection, **not** for calling methods).

```python
# ✅ OK: Check status
synth = bus.get_module("Synth")
if synth:
    status = synth.get_status()
    print(status["status"])  # "ready", "error", etc.

# ❌ VIOLATION OF GOBLIN LAW #37
synth = bus.get_module("Synth")
synth.play_note(60)  # Never call methods directly!
```

**list_modules() → List[str]**

Get names of all registered modules.

```python
modules = bus.list_modules()
print(f"Active modules: {modules}")
# ["MidiInput", "Synth", "Recorder"]
```

---

## TonikaModule API

Base class for all Tonika modules (Goblins).

### Constructor

```python
class MyModule(TonikaModule):
    def __init__(self):
        super().__init__(
            name="MyModule",        # Unique name
            version="1.0.0",        # Version string
            description="What I do" # Optional description
        )
```

**Parameters:**
- `name` (str): Module name (should be unique)
- `version` (str): Version string (default: "0.0.0")
- `description` (str): Brief description (default: "")

### async init()

Initialize the module. **You must call this after construction!**

```python
module = MyModule()
await module.init()  # Emits "module:initializing" → "module:ready"
```

**Lifecycle:**
1. Sets status to `INITIALIZING`
2. Emits `"module:initializing"`
3. Calls your `_initialize()` method
4. Sets status to `READY`
5. Emits `"module:ready"`

**On error:**
- Sets status to `ERROR`
- Emits `"module:error"`
- Re-raises exception

### async _initialize()

**Override this in your subclass.** This is where you:
- Set up internal state
- Subscribe to events
- Initialize resources

```python
class MyModule(TonikaModule):
    async def _initialize(self):
        self.counter = 0
        self.on("increment", self.handle_increment)
        
        # Can be async!
        await self.load_config()
```

**⚠️ Important:** Override `_initialize()` (with underscore), **NOT** `init()`!

### destroy()

Clean up the module. **Always call this when done!**

```python
module.destroy()
```

**Automatically:**
- Unsubscribes from all events
- Removes from module registry
- Emits `"module:destroyed"`
- Sets status to `DESTROYED`

**Note:** This is synchronous (not async).

### emit(event_type, detail)

Emit an event via the Bus. Source and version are added automatically.

```python
class MyModule(TonikaModule):
    def do_something(self):
        self.emit("data:processed", {"result": 42})
        # Bus adds source="MyModule", version="1.0.0"
```

### on(event_type, handler)

Subscribe to an event. Automatically tracked for cleanup.

```python
class MyModule(TonikaModule):
    async def _initialize(self):
        self.on("midi:note-on", self.handle_note)
    
    def handle_note(self, event):
        note = event.detail["note"]
        print(f"Got note: {note}")
```

**Note:** Subscriptions are automatically cleaned up when you call `destroy()`!

### once(event_type, handler)

Subscribe to an event, but only fire once.

```python
self.once("database:ready", self.on_db_ready)
```

### async wait_for(event_type, timeout_ms=None)

Wait for a specific event before continuing.

```python
async def _initialize(self):
    # Wait for dependency
    await self.wait_for("database:ready", timeout_ms=5000)
    # Now safe to use database
```

### get_status() → Dict[str, Any]

Get current module status.

```python
status = module.get_status()
print(status)
# {
#     "name": "MyModule",
#     "version": "1.0.0",
#     "description": "What I do",
#     "status": "ready"  # or "uninitialized", "initializing", "error", "destroyed"
# }
```

---

## Event Structures

### TonikaEvent

Core event structure for all Bus communication.

```python
@dataclass
class TonikaEvent:
    type: str           # Event type (e.g., "midi:note-on")
    detail: Any         # Payload data
    _meta: EventMetadata  # Context: timestamp, source, version
```

**Example:**
```python
event = TonikaEvent(
    type="midi:note-on",
    detail={"note": 60, "velocity": 100},
    _meta=EventMetadata(
        timestamp=1704067200000,
        source="Piano",
        version="1.0.0"
    )
)

print(event.type)           # "midi:note-on"
print(event.detail["note"]) # 60
print(event._meta.source)   # "Piano"
```

### EventMetadata

Metadata for every event - who, when, what version.

```python
@dataclass
class EventMetadata:
    timestamp: int  # Unix epoch milliseconds
    source: str     # Which module emitted it
    version: str    # Module version for debugging
```

**Factory method:**
```python
meta = EventMetadata.create(source="MyModule", version="1.0.0")
# Automatically sets timestamp to current time
```

### ModuleStatus

Lifecycle states for modules.

```python
class ModuleStatus(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DESTROYED = "destroyed"
```

---

## Async Support

### Async Handlers

Event handlers can be either synchronous or asynchronous:

```python
from tonika_bus import TonikaBus

bus = TonikaBus()

# Synchronous handler
bus.on("beat:tick", lambda e: print("tick", e.detail))

# Asynchronous handler
async def on_tick_async(event):
    await asyncio.sleep(0.1)  # Simulate async work
    print("async tick", event.detail)

bus.on("beat:tick", on_tick_async)
```

**How it works:**
- If a running event loop exists, async handlers are scheduled with `asyncio.create_task()`
- If no event loop is running, async handlers are executed with `asyncio.run()` (**⚠️ blocks**)

**Best Practice:** Always run your application in an async context (`asyncio.run(main())`) to avoid blocking.

### Waiting for Events

Use `wait_for()` to wait for dependencies:

```python
class ApiModule(TonikaModule):
    async def _initialize(self):
        print("⏳ Waiting for database...")
        await self.wait_for("database:ready", timeout_ms=5000)
        print("✅ API ready - database is available")
```

**Always use timeouts** to prevent indefinite waiting:

```python
# ❌ BAD: Could wait forever
await self.wait_for("some:event")

# ✅ GOOD: Will timeout after 5 seconds
await self.wait_for("some:event", timeout_ms=5000)
```

---

## Event Naming Conventions

Events use `domain:action` or `domain:noun:action` pattern:

```
✅ Good:
midi:note-on
midi:note-off
sequencer:pattern:request
module:ready
transport:play
audio:buffer:ready

❌ Bad:
foo                    # No domain
do-something           # No colon
MidiNoteOn            # Use lowercase with colons
```

### Common Domains

- `midi:*` - MIDI events
- `module:*` - Module lifecycle
- `audio:*` - Audio processing
- `sequencer:*` - Sequencer events
- `transport:*` - Transport control
- `theory:*` - Music theory analysis
- `ui:*` - User interface events

### Lifecycle Events (Reserved)

These events are emitted automatically by `TonikaModule` and **should not be emitted by subclasses**:

- `module:initializing` - Module starting initialization
- `module:ready` - Module ready to use
- `module:error` - Module initialization failed
- `module:destroyed` - Module cleaned up

See **Goblin Law #41** in [Goblin Laws](goblin_laws_examples.md).

---

## Common Patterns

### Request-Response Pattern

```python
import uuid
from tonika_bus import TonikaModule

class DataProvider(TonikaModule):
    async def _initialize(self):
        self.data = {"users": 100, "songs": 500}
        self.on("data:request", self.handle_request)
    
    def handle_request(self, event):
        request_id = event.detail["request_id"]
        key = event.detail["key"]
        
        # Send response
        self.emit("data:response", {
            "request_id": request_id,
            "key": key,
            "value": self.data.get(key, "NOT_FOUND")
        })

class DataConsumer(TonikaModule):
    async def _initialize(self):
        self.on("data:response", self.handle_response)
        self.responses = {}
    
    def handle_response(self, event):
        request_id = event.detail["request_id"]
        self.responses[request_id] = event.detail["value"]
    
    def request_data(self, key):
        request_id = str(uuid.uuid4())
        self.emit("data:request", {
            "request_id": request_id,
            "key": key
        })
        return request_id
```

### Module Dependencies

Use `wait_for()` to handle initialization order:

```python
class DatabaseModule(TonikaModule):
    async def _initialize(self):
        await asyncio.sleep(1)  # Simulate connection time
        self.emit("database:ready", {})

class ApiModule(TonikaModule):
    async def _initialize(self):
        # Wait for database before starting
        await self.wait_for("database:ready", timeout_ms=5000)
        print("✅ API ready - database is available")
```

### Event Chains

Process data through multiple modules:

```python
class InputModule(TonikaModule):
    def process(self, value):
        self.emit("stage1", {"value": value})

class ProcessorModule(TonikaModule):
    async def _initialize(self):
        self.on("stage1", self._process)
    
    def _process(self, event):
        value = event.detail["value"] * 2
        self.emit("stage2", {"value": value})

class OutputModule(TonikaModule):
    async def _initialize(self):
        self.on("stage2", self._output)
    
    def _output(self, event):
        print(f"Final result: {event.detail['value']}")
```

### Broadcasting

One emitter, many listeners:

```python
class Piano(TonikaModule):
    def play_key(self, note):
        self.emit("midi:note-on", {"note": note})

class Synth(TonikaModule):
    async def _initialize(self):
        self.on("midi:note-on", self.play)

class Recorder(TonikaModule):
    async def _initialize(self):
        self.on("midi:note-on", self.record)

class Visualizer(TonikaModule):
    async def _initialize(self):
        self.on("midi:note-on", self.draw)
```

---

## Best Practices

### 1. Always Use Timeouts

```python
# ❌ BAD: Could wait forever
await self.wait_for("database:ready")

# ✅ GOOD: Timeout after reasonable time
await self.wait_for("database:ready", timeout_ms=5000)
```

### 2. Clean Up Modules

```python
# ❌ BAD: Module leaks event handlers
module = MyModule(name="Test", version="1.0.0")
await module.init()
# ... use module ...
# Forgot to call destroy()!

# ✅ GOOD: Always clean up
module = MyModule(name="Test", version="1.0.0")
try:
    await module.init()
    # ... use module ...
finally:
    module.destroy()
```

### 3. Keep Handlers Fast

Event handlers should execute quickly (< 1ms ideal). For long-running work, use async:

```python
# ❌ BAD: Blocks event loop
def handler(event):
    time.sleep(10)  # Blocks everything!

# ✅ GOOD: Async for slow work
async def handler(event):
    await asyncio.sleep(10)  # Doesn't block
```

### 4. Don't Modify Event Detail

Handlers should **not** modify event detail in place:

```python
# ❌ BAD: Mutates shared data
def handler(event):
    event.detail["count"] += 1  # Affects other handlers!

# ✅ GOOD: Read only
def handler(event):
    count = event.detail["count"]
    self.emit("counter:changed", {"count": count + 1})
```

### 5. Use Descriptive Event Names

```python
# ❌ BAD: Vague
self.emit("done", {})

# ✅ GOOD: Descriptive
self.emit("audio:render:complete", {"duration_ms": 1234})
```

### 6. Validate Event Detail

Don't assume event detail structure:

```python
# ❌ BAD: Assumes structure
def handler(event):
    note = event.detail["note"]  # KeyError if missing!

# ✅ GOOD: Safe access
def handler(event):
    note = event.detail.get("note")
    if note is None:
        self.logger.warning("Received event without note")
        return
```

### 7. Never Call Module Methods Directly

```python
# ❌ VIOLATION OF GOBLIN LAW #37
synth = bus.get_module("Synth")
synth.play_note(60)  # Direct call!

# ✅ COMPLIANCE
bus.emit("synth:note:play", {"note": 60})
```

See [Goblin Laws with Examples](goblin_laws_examples.md) for more design principles.

---

## Debugging

### Enable Debug Logging

```python
bus = TonikaBus()
bus.set_debug(True)

# Now see all events in console:
# 📢 EMIT: TonikaEvent(type='midi:note-on', source='Piano', ...)
# 👂 SUBSCRIBE: midi:note-on (total handlers: 2)
```

### Inspect Event History

```python
# See what happened recently
events = bus.get_event_log(limit=20)
for event in events:
    timestamp = event._meta.timestamp
    event_type = event.type
    source = event._meta.source
    print(f"{timestamp}: {event_type} from {source}")
```

### Check Module Status

```python
# List all modules
modules = bus.list_modules()
print(f"Active modules: {modules}")

# Get specific module status
module = bus.get_module("Synth")
if module:
    status = module.get_status()
    print(f"Status: {status['status']}")
    print(f"Version: {status['version']}")
```

---

## See Also

- **[Writing Your First Module](FIRST_MODULE.md)** - Step-by-step tutorial
- **[Goblin Laws with Examples](goblin_laws_examples.md)** - Design principles
- **[Testing Guide](TESTING.md)** - How to test your modules
- **[API Reference](https://tonika-bus.readthedocs.io/)** - Full API docs

---

**🧌 Remember: Never Meddle in Another Goblin's Guts!** — Goblin Law #37