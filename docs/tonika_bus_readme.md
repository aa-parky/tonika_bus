# Tonika Bus 🚌

**The Message Highway for Musical Goblins**

> *"Never Meddle in Another Goblin's Guts"* — Goblin Law #37

The Tonika Bus is a centralized event communication system that lets musical modules talk to each other without getting tangled up. Think of it as a magical messenger that carries notes between Goblins, so they never have to shout directly at each other.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-106%20passing-brightgreen.svg)](../tests/)
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen.svg)](htmlcov/)

---

## 📖 Table of Contents

- [For 5-Year-Old Orcs](#for-5-year-old-orcs)
- [For Developers](#for-developers)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Goblin Laws](#goblin-laws)
- [Testing](#testing)
- [Architecture](#architecture)
- [Contributing](#contributing)

---

## 🧌 For 5-Year-Old Orcs

### What is the Bus?

Imagine you have a bunch of Goblins in a cave. Each Goblin has a special job:

- 🎹 **Piano Goblin** - Plays piano keys
- 🔊 **Sound Goblin** - Makes the actual sounds
- 📼 **Recorder Goblin** - Remembers what happened
- 🎨 **Artist Goblin** - Draws pretty lights

**The Problem:** If Piano Goblin shouts directly at Sound Goblin, and Sound Goblin shouts at Artist Goblin, and everyone shouts at everyone... it gets VERY LOUD and CONFUSING! 😵

**The Solution:** The Bus! 🚌

The Bus is like a magical messenger bird that flies between Goblins. When Piano Goblin plays a note, they don't shout at Sound Goblin. Instead, they tell the Bus: *"Hey Bus, I just played middle C!"*

The Bus then flies to ALL the Goblins who care about piano notes and whispers: *"Psst! Piano Goblin just played middle C!"*

Now Sound Goblin makes the sound, Recorder Goblin writes it down, and Artist Goblin draws a pretty light. **Nobody shouted at anybody!** 🎉

### Why is this Good?

1. **Goblins don't need to know each other** - Piano Goblin doesn't even know Sound Goblin exists!
2. **Easy to add new Goblins** - Want a new Dance Goblin who dances to notes? Just tell them to listen to the Bus!
3. **Goblins can take breaks** - If Sound Goblin goes on vacation, nobody crashes. The Bus just keeps delivering messages.
4. **You can see all the messages** - The Bus remembers what it delivered, so you can check what happened!

### The Goblin Laws

Goblins follow ancient laws to keep the cave organized:

**Law #37: Never Meddle in Another Goblin's Guts** 🚫  
Don't poke other Goblins! Use the Bus!

**Law #41: Only One Drumbeat of Readiness** 🥁  
All Goblins wake up the same way: *stretch → yawn → ready!*

**Law #7: No Fat Orcs** 🏋️  
Each Goblin does ONE job really well. Don't make a Goblin do everything!

**Law #8: All Goblins Are Boundary Guards** 🛡️  
If a Goblin talks to the outside world (like a real piano), they MUST tell the Bus immediately!

---

## 👨‍💻 For Developers

### What is the Bus?

The Tonika Bus is a **centralized event broker** implementing the **publish-subscribe pattern** for modular music production. It provides:

- ✅ **Complete decoupling** - Modules never reference each other
- ✅ **Observable system state** - Event log for debugging
- ✅ **Async support** - Non-blocking event handling
- ✅ **Lifecycle management** - Standardized init/destroy pattern
- ✅ **Type safety** - Full type hints throughout
- ✅ **Well-tested** - 106 tests, 93% coverage

### Why Use It?

**Traditional approach (tight coupling):**
```python
class Sequencer:
    def __init__(self, synth, recorder, visualizer):
        self.synth = synth
        self.recorder = recorder
        self.visualizer = visualizer
    
    def play_note(self, note):
        self.synth.play(note)          # Direct call
        self.recorder.record(note)      # Direct call
        self.visualizer.show(note)      # Direct call
```

**Problems:**
- ❌ Sequencer tightly coupled to 3 modules
- ❌ Hard to add new listeners
- ❌ Can't swap implementations
- ❌ Difficult to test
- ❌ Changes ripple through codebase

**Bus approach (decoupled):**
```python
class Sequencer(TonikaModule):
    def play_note(self, note):
        self.emit("midi:note-on", {"note": note})  # Just emit!

class Synth(TonikaModule):
    async def _initialize(self):
        self.on("midi:note-on", self.play)

class Recorder(TonikaModule):
    async def _initialize(self):
        self.on("midi:note-on", self.record)
```

**Benefits:**
- ✅ Zero coupling between modules
- ✅ Easy to add new listeners
- ✅ Simple to swap implementations
- ✅ Trivial to test
- ✅ Changes stay local

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/aa-parky/tonika_bus.git
cd tonika_bus

# Install with all dependencies
pip install -e ".[all]"

# Or just core
pip install -e .
```

### Your First Module (2 minutes)

```python
import asyncio
from tonika_bus.core import TonikaBus, TonikaModule

# Create a module that says hello
class HelloGoblin(TonikaModule):
    async def _initialize(self):
        # Subscribe to greetings
        self.on("greeting:hello", self.respond)
    
    def respond(self, event):
        name = event.detail["name"]
        print(f"🧌 Hello {name}! I'm a friendly Goblin!")
        self.emit("greeting:response", {"message": f"Hi from {self.name}!"})

# Use it
async def main():
    # Get the Bus (there's only one!)
    bus = TonikaBus()
    
    # Create and wake up the Goblin
    goblin = HelloGoblin(name="FriendlyGoblin", version="1.0.0")
    await goblin.init()
    
    # Send a greeting
    bus.emit("greeting:hello", {"name": "Orc"})
    
    # Give it time to respond
    await asyncio.sleep(0.1)
    
    # Check what happened
    events = bus.get_event_log()
    print(f"\n📜 {len(events)} events happened!")
    
    # Clean up
    goblin.destroy()

# Run it!
asyncio.run(main())
```

**Output:**
```
🧌 Hello Orc! I'm a friendly Goblin!
📜 4 events happened!
```

---

## 🎓 Core Concepts

### 1. The Bus (Singleton)

**There is only ONE Bus.** No matter how many times you call `TonikaBus()`, you get the same instance.

```python
from tonika_bus.core import TonikaBus

bus1 = TonikaBus()
bus2 = TonikaBus()

assert bus1 is bus2  # True! Same Bus!
```

**Why singleton?**
- Single source of truth for all events
- No "which bus?" confusion
- Easier debugging and testing

### 2. Events (Messages)

Every message on the Bus is a `TonikaEvent` with three parts:

```python
event.type      # What happened? (e.g., "midi:note-on")
event.detail    # The data (e.g., {"note": 60, "velocity": 100})
event._meta     # Who sent it? When? (timestamp, source, version)
```

**Events are created automatically when you emit:**

```python
# You write:
bus.emit("midi:note-on", {"note": 60})

# Bus creates:
TonikaEvent(
    type="midi:note-on",
    detail={"note": 60},
    _meta=EventMetadata(
        timestamp=1730678400000,  # Unix milliseconds
        source="MidiInput",
        version="1.0.0"
    )
)
```

### 3. Modules (Goblins)

All Tonika components extend `TonikaModule`. This gives you:

- ✅ Consistent lifecycle (init → ready → destroy)
- ✅ Bus access without coupling
- ✅ Automatic cleanup
- ✅ Built-in event handling

```python
class MyGoblin(TonikaModule):
    async def _initialize(self):
        # Set up subscriptions here
        self.on("some:event", self.handle_it)
    
    def handle_it(self, event):
        # Process the event
        print(f"Got: {event.detail}")
```

### 4. Pub/Sub Pattern

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
    
    def play_sound(self, event):
        note = event.detail["note"]
        print(f"♪ Playing {note}")
```

**Key Point:** Piano and Synth have ZERO knowledge of each other! 🎯

---

## 📚 API Reference

### TonikaBus

The central message broker. Get it with `TonikaBus()` (singleton).

#### `emit(event_type, detail, source="unknown", version="0.0.0")`

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

---

#### `on(event_type, handler) → unsubscribe_function`

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
- `handler` (Callable[[TonikaEvent], None]): Function to call

**Returns:** Callable[[], None] - Unsubscribe function

---

#### `once(event_type, handler) → unsubscribe_function`

Subscribe to an event, but only fire once.

```python
def one_time(event):
    print("This only prints once!")

bus.once("module:ready", one_time)

# Emit twice
bus.emit("module:ready", {})
bus.emit("module:ready", {})
# Handler only called once!
```

---

#### `async wait_for(event_type, timeout_ms=None) → TonikaEvent`

Wait for a specific event before continuing.

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

**⚠️ CRITICAL SAFETY WARNING:**

**Always use timeouts in production code.** If you call `wait_for()` without a timeout and the event never arrives, the future will remain in memory indefinitely, causing a memory leak.

```python
# ❌ DANGEROUS: Memory leak if event never arrives
await self.wait_for("database:ready")

# ✅ SAFE: Will timeout and raise exception
await self.wait_for("database:ready", timeout_ms=5000)
```

**Why this matters:**
- Events can fail to arrive due to bugs, crashes, or network issues
- Unbounded waits accumulate in memory over time
- Memory leaks cause mysterious production failures
- Timeouts make failures explicit and debuggable

---

#### `get_event_log(limit=None) → List[TonikaEvent]`

Get recent events from the log (for debugging).

```python
# Get last 10 events
recent = bus.get_event_log(limit=10)
for event in recent:
    print(f"{event.type} from {event._meta.source}")
```

**Parameters:**
- `limit` (int | None): Max events to return (None = all)

**Returns:** List[TonikaEvent] - Events in chronological order

---

#### `clear_event_log()`

Clear the event log (useful for long-running apps).

```python
bus.clear_event_log()
```

---

#### `set_debug(enabled: bool)`

Enable or disable debug logging.

```python
bus.set_debug(True)  # See all events in console
```

---

#### `register_module(module: TonikaModule)`

Register a module (called automatically by module constructor).

```python
# You don't call this directly
# It happens automatically when you create a module
```

---

#### `unregister_module(name: str)`

Unregister a module (called automatically by `module.destroy()`).

---

#### `get_module(name: str) → TonikaModule | None`

Get a module by name (for inspection, not for calling!).

```python
synth = bus.get_module("Synth")
if synth:
    status = synth.get_status()
    print(status["status"])  # "ready", "error", etc.
```

---

#### `list_modules() → List[str]`

Get names of all registered modules.

```python
modules = bus.list_modules()
print(f"Active modules: {modules}")
# ["MidiInput", "Synth", "Recorder"]
```

---

### TonikaModule

Base class for all Tonika modules (Goblins).

#### Constructor

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

---

#### `async init()`

Initialize the module. **You must call this!**

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

---

#### `async _initialize()`

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

**Note:** This is `_initialize()` with underscore, not `init()`!

---

#### `destroy()`

Clean up the module. **Always call this when done!**

```python
module.destroy()
```

**Automatically:**
- Unsubscribes from all events
- Removes from module registry
- Emits `"module:destroyed"`
- Sets status to `DESTROYED`

**Note:** This is synchronous (not async)!

---

#### `emit(event_type, detail)`

Emit an event via the Bus. Source and version are added automatically.

```python
class MyModule(TonikaModule):
    def do_something(self):
        self.emit("data:processed", {"result": 42})
        # Bus adds source="MyModule", version="1.0.0"
```

---

#### `on(event_type, handler)`

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

---

#### `once(event_type, handler)`

Subscribe to an event, but only fire once.

```python
self.once("database:ready", self.on_db_ready)
```

---

#### `async wait_for(event_type, timeout_ms=None)`

Wait for a specific event before continuing.

```python
async def _initialize(self):
    # Wait for dependency
    await self.wait_for("database:ready", timeout_ms=5000)
    # Now safe to use database
```

**⚠️ Always use timeouts in production!** See the critical safety warning in the `TonikaBus.wait_for()` documentation above.

---

#### `get_status() → Dict[str, Any]`

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

### Event Naming Convention

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

**Common Domains:**
- `midi:*` - MIDI events
- `module:*` - Module lifecycle
- `audio:*` - Audio processing
- `sequencer:*` - Sequencer events
- `transport:*` - Transport control

---

## 🎯 Examples

### Example 1: Simple Counter

```python
import asyncio
from tonika_bus.core import TonikaBus, TonikaModule

class CounterGoblin(TonikaModule):
    async def _initialize(self):
        self.count = 0
        self.on("counter:increment", self.increment)
        self.on("counter:reset", self.reset)
    
    def increment(self, event):
        amount = event.detail.get("amount", 1)
        self.count += amount
        self.emit("counter:changed", {"count": self.count})
        print(f"🔢 Count: {self.count}")
    
    def reset(self, event):
        self.count = 0
        self.emit("counter:changed", {"count": self.count})
        print(f"🔄 Reset to 0")

async def main():
    bus = TonikaBus()
    counter = CounterGoblin(name="Counter", version="1.0.0")
    await counter.init()
    
    # Increment a few times
    bus.emit("counter:increment", {"amount": 5})
    bus.emit("counter:increment", {"amount": 3})
    bus.emit("counter:increment", {"amount": 2})
    
    # Reset
    bus.emit("counter:reset", {})
    
    # Cleanup
    counter.destroy()

asyncio.run(main())
```

**Output:**
```
🔢 Count: 5
🔢 Count: 8
🔢 Count: 10
🔄 Reset to 0
```

---

### Example 2: Musical Goblins

```python
import asyncio
from tonika_bus.core import TonikaBus, TonikaModule

class PianoGoblin(TonikaModule):
    """Plays piano keys"""
    def play_key(self, note):
        print(f"🎹 Piano: Playing note {note}")
        self.emit("midi:note-on", {"note": note, "velocity": 100})

class SynthGoblin(TonikaModule):
    """Makes sounds"""
    async def _initialize(self):
        self.on("midi:note-on", self.make_sound)
    
    def make_sound(self, event):
        note = event.detail["note"]
        print(f"🔊 Synth: BEEP! (note {note})")

class RecorderGoblin(TonikaModule):
    """Records everything"""
    async def _initialize(self):
        self.recorded = []
        self.on("midi:note-on", self.record)
    
    def record(self, event):
        self.recorded.append(event.detail)
        print(f"📼 Recorder: Saved note {event.detail['note']}")

class ArtistGoblin(TonikaModule):
    """Draws pretty lights"""
    async def _initialize(self):
        self.on("midi:note-on", self.draw)
    
    def draw(self, event):
        note = event.detail["note"]
        print(f"🎨 Artist: Drawing light for note {note}")

async def main():
    # Wake up all the Goblins
    piano = PianoGoblin(name="Piano", version="1.0.0")
    synth = SynthGoblin(name="Synth", version="1.0.0")
    recorder = RecorderGoblin(name="Recorder", version="1.0.0")
    artist = ArtistGoblin(name="Artist", version="1.0.0")
    
    await piano.init()
    await synth.init()
    await recorder.init()
    await artist.init()
    
    # Play a C major chord
    print("🎵 Playing C major chord...\n")
    piano.play_key(60)  # C
    piano.play_key(64)  # E
    piano.play_key(67)  # G
    
    await asyncio.sleep(0.1)
    
    print(f"\n📊 Recorder saved {len(recorder.recorded)} notes!")
    
    # All Goblins go to sleep
    piano.destroy()
    synth.destroy()
    recorder.destroy()
    artist.destroy()

asyncio.run(main())
```

**Output:**
```
🎵 Playing C major chord...

🎹 Piano: Playing note 60
🔊 Synth: BEEP! (note 60)
📼 Recorder: Saved note 60
🎨 Artist: Drawing light for note 60
🎹 Piano: Playing note 64
🔊 Synth: BEEP! (note 64)
📼 Recorder: Saved note 64
🎨 Artist: Drawing light for note 64
🎹 Piano: Playing note 67
🔊 Synth: BEEP! (note 67)
📼 Recorder: Saved note 67
🎨 Artist: Drawing light for note 67

📊 Recorder saved 3 notes!
```

**Notice:** Piano Goblin doesn't know about Synth, Recorder, or Artist! They all just listen to the Bus! 🎉

---

### Example 3: Request-Response Pattern

```python
import asyncio
import uuid
from tonika_bus.core import TonikaBus, TonikaModule

class DataProvider(TonikaModule):
    """Provides data when asked"""
    async def _initialize(self):
        self.data = {
            "users": 100,
            "songs": 500,
            "playlists": 50
        }
        self.on("data:request", self.handle_request)
    
    def handle_request(self, event):
        request_id = event.detail["request_id"]
        key = event.detail["key"]
        
        print(f"📦 Provider: Got request for '{key}'")
        
        # Send response
        self.emit("data:response", {
            "request_id": request_id,
            "key": key,
            "value": self.data.get(key, "NOT_FOUND")
        })

class DataConsumer(TonikaModule):
    """Requests data"""
    async def _initialize(self):
        self.on("data:response", self.handle_response)
        self.responses = {}
    
    def handle_response(self, event):
        request_id = event.detail["request_id"]
        key = event.detail["key"]
        value = event.detail["value"]
        
        self.responses[request_id] = value
        print(f"📥 Consumer: Got '{key}' = {value}")
    
    def request_data(self, key):
        request_id = str(uuid.uuid4())
        print(f"📤 Consumer: Requesting '{key}'...")
        self.emit("data:request", {
            "request_id": request_id,
            "key": key
        })
        return request_id

async def main():
    provider = DataProvider(name="Provider", version="1.0.0")
    consumer = DataConsumer(name="Consumer", version="1.0.0")
    
    await provider.init()
    await consumer.init()
    
    # Request some data
    req1 = consumer.request_data("users")
    req2 = consumer.request_data("songs")
    
    await asyncio.sleep(0.1)  # Wait for responses
    
    print(f"\n✅ Got {len(consumer.responses)} responses!")
    
    provider.destroy()
    consumer.destroy()

asyncio.run(main())
```

---

### Example 4: Waiting for Dependencies

```python
import asyncio
from tonika_bus.core import TonikaBus, TonikaModule

class DatabaseGoblin(TonikaModule):
    """Connects to database"""
    async def _initialize(self):
        print("💾 Database: Connecting...")
        await asyncio.sleep(1)  # Simulate connection time
        print("💾 Database: Connected!")
        self.emit("database:ready", {})

class ApiGoblin(TonikaModule):
    """Needs database to work"""
    async def _initialize(self):
        print("🌐 API: Waiting for database...")
        
        # ⚠️ ALWAYS use timeout in production!
        # This prevents memory leaks if database:ready never arrives
        await self.wait_for("database:ready", timeout_ms=5000)
        
        print("🌐 API: Database is ready! Starting API server...")
        await asyncio.sleep(0.5)
        print("🌐 API: Ready to serve requests!")

async def main():
    db = DatabaseGoblin(name="Database", version="1.0.0")
    api = ApiGoblin(name="API", version="1.0.0")
    
    # Start both (API will wait for DB)
    await asyncio.gather(
        db.init(),
        api.init()
    )
    
    print("\n✅ Both modules ready!")
    
    db.destroy()
    api.destroy()

asyncio.run(main())
```

**Output:**
```
💾 Database: Connecting...
🌐 API: Waiting for database...
💾 Database: Connected!
🌐 API: Database is ready! Starting API server...
🌐 API: Ready to serve requests!

✅ Both modules ready!
```

**⚠️ Important Note About Timeouts:**

This example uses `timeout_ms=5000` (5 seconds). In production code, **always include a timeout**. Without it, if the `"database:ready"` event never arrives (due to a bug, crash, or network issue), the future will remain in memory indefinitely, causing a memory leak. See the [Bus Architecture Guide](BUS_GUIDE.md) for more details on safe `wait_for()` usage.

---

## 🧌 Goblin Laws

The Bus enforces ancient Goblin Laws to keep your code clean and maintainable.

### Goblin Law #37: Never Meddle in Another Goblin's Guts

**Rule:** Modules must NEVER directly access or modify another module's internal state.

**Why:** If Goblins poke each other's guts, everything breaks! 🩸

**Enforcement:** The Bus is the ONLY communication channel between modules.

```python
# ❌ FORBIDDEN - Violation of Law #37
synth = bus.get_module("Synth")
synth.oscillator.frequency = 440  # Direct meddling! BAD!

# ✅ REQUIRED - Compliance with Law #37
bus.emit("synth:frequency:set", {"frequency": 440})
```

**Punishment for violation:** Your code becomes a tangled mess that nobody can understand! 😱

---

### Goblin Law #41: Only One Drumbeat of Readiness

**Rule:** Only the base `TonikaModule` class emits lifecycle events (`module:initializing`, `module:ready`, `module:error`, `module:destroyed`).

**Why:** If every Goblin drums their own beat, nobody knows when anyone is ready! 🥁🥁🥁

**Enforcement:** Subclasses override `_initialize()`, NOT `init()`.

```python
# ❌ FORBIDDEN - Violation of Law #41
class BadGoblin(TonikaModule):
    async def init(self):
        self.emit("module:ready", {})  # DON'T override init()!

# ✅ REQUIRED - Compliance with Law #41
class GoodGoblin(TonikaModule):
    async def _initialize(self):
        # Custom setup here
        self.emit("synth:voice-allocated", {})  # Domain events OK!
```

**Why this matters:** Consistent lifecycle means you can trust that ALL modules follow the same pattern:
1. `UNINITIALIZED` → `INITIALIZING` → `READY`
2. Always emits `"module:ready"` when ready
3. Always emits `"module:destroyed"` when destroyed

---

### Goblin Law #7: No Fat Orcs

**Rule:** Each module does ONE thing well.

**Why:** A Goblin who tries to do everything does nothing well! 🏋️

**Guidance:** If a module is doing too many things, split it into multiple modules that communicate via the Bus.

```python
# ❌ BAD - Fat Orc doing everything
class MegaModule(TonikaModule):
    async def _initialize(self):
        self.play_midi()
        self.record_audio()
        self.analyze_chords()
        self.draw_visualizations()
        self.send_network_packets()
        # TOO MUCH!

# ✅ GOOD - Lean Goblins, each with one job
class MidiPlayer(TonikaModule): ...
class AudioRecorder(TonikaModule): ...
class ChordAnalyzer(TonikaModule): ...
class Visualizer(TonikaModule): ...
class NetworkSender(TonikaModule): ...
```

---

### Goblin Law #8: All Goblins Are Boundary Guards

**Rule:** Every module that touches the "outside world" (hardware, files, network) must immediately report to the Bus.

**Why:** The Bus needs to know what's happening in the real world! 🛡️

**Examples:**

```python
# ✅ GOOD - Boundary guard reports immediately
class MidiInputModule(TonikaModule):
    def handle_hardware_midi(self, note):
        # Got note from real MIDI keyboard
        self.emit("midi:note-on", {"note": note})  # Tell the Bus!

# ✅ GOOD - File reader reports immediately
class ConfigLoader(TonikaModule):
    def load_file(self, path):
        data = json.load(open(path))
        self.emit("config:loaded", {"data": data})  # Tell the Bus!

# ❌ BAD - Boundary guard keeps secrets
class MidiInputModule(TonikaModule):
    def handle_hardware_midi(self, note):
        self.internal_buffer.append(note)  # Keeping it secret!
        # Bus doesn't know! BAD!
```

---

## 🧪 Testing

The Bus has **106 tests with 93% coverage**. All tests pass in < 1 second! ⚡

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov

# Verbose
pytest -v

# Only unit tests (fast)
pytest -m unit

# Only integration tests
pytest -m integration

# Stop on first failure
pytest -x
```

### Test Structure

```
tests/
├── test_bus.py        # 46 tests for TonikaBus (92% coverage)
├── test_events.py     # 35 tests for event structures (100% coverage)
├── test_module.py     # 25 tests for TonikaModule (93% coverage)
└── conftest.py        # Shared fixtures
```

### Testing Your Modules

```python
import pytest
from tonika_bus.core import TonikaBus, TonikaModule

@pytest.fixture
def fresh_bus():
    """Provide a fresh Bus for each test"""
    bus = TonikaBus()
    bus.handlers.clear()
    bus.module_registry.clear()
    bus.clear_event_log()
    yield bus

@pytest.mark.asyncio
async def test_my_module(fresh_bus):
    """Test module behavior"""
    module = MyModule(name="Test", version="1.0.0")
    await module.init()
    
    # Test event emission
    received = []
    fresh_bus.on("my:event", lambda e: received.append(e))
    
    module.emit("my:event", {"data": "test"})
    
    assert len(received) == 1
    assert received[0].detail["data"] == "test"
    
    module.destroy()
```

### Using Makefile

```bash
make test          # Run all tests
make test-cov      # Run with coverage report
make test-unit     # Run only unit tests
make lint          # Run linter (ruff)
make format        # Format code (black)
make typecheck     # Run type checker (mypy)
make check         # All quality checks
```

---

## 🏗️ Architecture

### Design Principles

#### 1. No Direct Coupling (Goblin Law #37)

Modules never call each other's methods. All communication goes through the Bus.

```python
# ❌ FORBIDDEN
sequencer.get_pattern()  # Direct method call

# ✅ REQUIRED
bus.emit("sequencer:pattern:request", {"request_id": "abc123"})
```

#### 2. Observable System State

At any time, you can inspect:
- What modules exist
- What events occurred
- Module status

```python
# See all modules
print(bus.list_modules())

# See recent events
print(bus.get_event_log(limit=10))

# Check module status
status = module.get_status()
print(status["status"])  # "ready", "error", etc.
```

#### 3. Single Lifecycle Drumbeat (Goblin Law #41)

Every module follows the same lifecycle:

```
Constructor → UNINITIALIZED
    ↓
init() → INITIALIZING → "module:initializing"
    ↓
_initialize() → custom setup
    ↓
READY → "module:ready"
    ↓
Normal operation → emit/receive events
    ↓
destroy() → cleanup → "module:destroyed" → DESTROYED
```

### Event Flow Diagram

```
┌─────────────┐
│  Piano      │
│  Goblin     │
└──────┬──────┘
       │ emit("midi:note-on", {note: 60})
       ↓
┌─────────────────────────────────────────┐
│         🚌 Tonika Bus                   │
│  ┌──────────────────────────────────┐   │
│  │  Event Log (for debugging)       │   │
│  │  [event1, event2, event3, ...]   │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Handler Registry                │   │
│  │  "midi:note-on" → [h1, h2, h3]  │   │
│  └──────────────────────────────────┘   │
└───────┬──────────┬──────────┬───────────┘
        │          │          │
        ↓          ↓          ↓
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │  Synth   │ │ Recorder │ │  Artist  │
  │  Goblin  │ │  Goblin  │ │  Goblin  │
  └──────────┘ └──────────┘ └──────────┘
```

### Module Registry

The Bus maintains a registry of all active modules:

```python
bus = TonikaBus()

# Modules auto-register on creation
piano = PianoGoblin(name="Piano", version="1.0.0")
synth = SynthGoblin(name="Synth", version="1.0.0")

# Check what's registered
print(bus.list_modules())  # ["Piano", "Synth"]

# Get a specific module (for inspection only!)
module = bus.get_module("Piano")
print(module.get_status())
```

**Important:** Use `get_module()` for inspection/debugging only, NOT for calling methods! That would violate Goblin Law #37! 🚫

---

## 🐛 Debugging

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

### Common Issues

#### Q: My handler isn't being called

**Check:**
1. ✅ Module is initialized: `await module.init()`
2. ✅ Subscription in `_initialize()`, not `__init__()`
3. ✅ Event type matches exactly (case-sensitive!)
4. ✅ Bus is the same instance (singleton)

```python
# Debug: See all handlers
print(bus.handlers)
```

#### Q: Events arriving in wrong order

Events are processed synchronously in the order they're emitted. If using async operations, use `await`:

```python
await module1.init()  # Wait for this
await module2.init()  # Then this
```

#### Q: Memory leak / handlers not cleaning up

**Make sure you call `destroy()`:**

```python
module = MyModule(name="Test", version="1.0.0")
await module.init()
# ... use module ...
module.destroy()  # ← Don't forget this!
```

#### Q: "Set changed size during iteration" error

This was a bug in older versions. **Update to latest version!** The Bus now makes a copy of handlers before iterating.

---

## 🤝 Contributing

We welcome contributions from Orcs, Goblins, and other creatures! 🧌

### Code Style

- Follow PEP 8
- Use type hints everywhere
- Write docstrings for all public methods
- Keep handlers fast (< 1ms ideal)
- Test your changes

### Running Quality Checks

```bash
# Run all tests
make test

# Check coverage
make test-cov

# Lint code
make lint

# Format code
make format

# Type check
make typecheck

# All checks
make check
```

### Submitting Changes

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `make check`
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

---

## 📜 License

**GPL-3.0** - See [LICENSE](LICENSE)

Part of the **Tonika project** - Music as Resistance ✊

---

## 🔗 Links

- **GitHub:** [https://github.com/aa-parky/tonika_bus](https://github.com/aa-parky/tonika_bus)
- **Main Tonika Repo:** [https://github.com/aa-parky/tonika](https://github.com/aa-parky/tonika)
- **Goblin Laws:** [docs/goblin-laws.md](docs/goblin-laws.md)
- **Issues:** [https://github.com/aa-parky/tonika_bus/issues](https://github.com/aa-parky/tonika_bus/issues)

---

## 🎵 What's Next?

Now that you have the Bus, you can build:

- 🎹 **MIDI adapters** using `mido` and `python-rtmidi`
- 🎼 **Music theory modules** using `music21`
- 🎛️ **Audio processing** modules
- 🎨 **Visualizers** that react to music
- 🎮 **Controllers** for live performance
- 📼 **Recorders** and **sequencers**
- 🤖 **AI music generators**

**The Bus connects them all!** 🚌✨

---

**🧌 Now go make some noise with your Goblins! 🎵**

*Remember: Never Meddle in Another Goblin's Guts!* — Goblin Law #37