# Writing Your First Module

**Step-by-step tutorial for creating a Tonika module**

This guide will walk you through creating your first Tonika module from scratch. You'll learn the basics of the Bus, module lifecycle, and event handling.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Understanding Modules](#understanding-modules)
- [Your First Module: CounterGoblin](#your-first-module-countergoblin)
- [Running Your Module](#running-your-module)
- [Understanding What Happened](#understanding-what-happened)
- [Adding More Features](#adding-more-features)
- [Next Steps](#next-steps)

---

## Prerequisites

### Installation

Make sure you have Tonika Bus installed:

```bash
git clone https://github.com/aa-parky/tonika_bus.git
cd tonika_bus
pip install -e .
```

Verify installation:
```bash
python -c "from tonika_bus import TonikaBus; print('✅ Ready!')"
```

### Python Knowledge

You should be comfortable with:
- Basic Python (classes, functions, dictionaries)
- Async/await (we'll explain as we go)
- Running Python scripts

---

## Understanding Modules

### What is a Module?

In Tonika, a **module** (or "Goblin") is a self-contained unit that:
1. Does **one thing well** (Goblin Law #7: No Fat Orcs)
2. Communicates only through the **Bus** (Goblin Law #37: Never Meddle in Another Goblin's Guts)
3. Follows a **standardized lifecycle** (Goblin Law #41: Only One Drumbeat of Readiness)

### Module Lifecycle

Every module goes through the same lifecycle:

```
1. Create → module = MyModule(name="Test", version="1.0.0")
2. Initialize → await module.init()
   - Status: UNINITIALIZED → INITIALIZING → READY
   - Emits: "module:initializing" → "module:ready"
3. Use → module.emit() / module.on()
   - Normal operation
4. Destroy → module.destroy()
   - Status: DESTROYED
   - Emits: "module:destroyed"
   - Cleans up subscriptions
```

### The Base Class

All modules extend `TonikaModule`:

```python
from tonika_bus import TonikaModule

class MyModule(TonikaModule):
    def __init__(self):
        super().__init__(
            name="MyModule",
            version="1.0.0",
            description="What this module does"
        )
    
    async def _initialize(self):
        # Your setup code goes here
        pass
```

**Key Points:**
- Override `_initialize()` (with underscore), **NOT** `init()`
- `_initialize()` can be async
- Setup subscriptions in `_initialize()`

---

## Your First Module: CounterGoblin

Let's create a simple counter that increments and resets via events.

### Step 1: Create the File

Create a file called `counter_goblin.py`:

```python
import asyncio
from tonika_bus import TonikaBus, TonikaModule

class CounterGoblin(TonikaModule):
    """A simple counter that responds to events"""
    
    def __init__(self):
        super().__init__(
            name="CounterGoblin",
            version="1.0.0",
            description="Counts things"
        )
    
    async def _initialize(self):
        """Set up the counter and subscribe to events"""
        # Internal state
        self.count = 0
        
        # Subscribe to events
        self.on("counter:increment", self.handle_increment)
        self.on("counter:reset", self.handle_reset)
        
        print("🔢 CounterGoblin ready to count!")
    
    def handle_increment(self, event):
        """Increment the counter"""
        amount = event.detail.get("amount", 1)
        self.count += amount
        
        # Emit an event to announce the new count
        self.emit("counter:changed", {"count": self.count})
        
        print(f"   Count: {self.count}")
    
    def handle_reset(self, event):
        """Reset the counter to zero"""
        self.count = 0
        
        # Emit an event to announce the reset
        self.emit("counter:changed", {"count": self.count})
        
        print(f"   🔄 Reset to 0")

# Main function to run the module
async def main():
    # Get the Bus (there's only one!)
    bus = TonikaBus()
    
    # Create the module
    counter = CounterGoblin()
    
    # Initialize it
    await counter.init()
    
    # Send some events
    print("\n📤 Sending increment events...")
    bus.emit("counter:increment", {"amount": 5})
    bus.emit("counter:increment", {"amount": 3})
    bus.emit("counter:increment", {"amount": 2})
    
    print("\n📤 Sending reset event...")
    bus.emit("counter:reset", {})
    
    # Give it time to process
    await asyncio.sleep(0.1)
    
    # Clean up
    counter.destroy()
    print("\n✅ Done!")

# Run it!
if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Run It

```bash
python counter_goblin.py
```

### Step 3: Expected Output

```
🔢 CounterGoblin ready to count!

📤 Sending increment events...
   Count: 5
   Count: 8
   Count: 10

📤 Sending reset event...
   🔄 Reset to 0

✅ Done!
```

---

## Understanding What Happened

Let's break down what happened step by step:

### 1. Module Creation

```python
counter = CounterGoblin()
```

- Creates the module instance
- Calls `__init__()` which registers with the Bus
- Status: `UNINITIALIZED`

### 2. Initialization

```python
await counter.init()
```

- Changes status to `INITIALIZING`
- Emits `"module:initializing"` event
- Calls your `_initialize()` method:
  - Sets `self.count = 0`
  - Subscribes to `"counter:increment"` and `"counter:reset"`
- Changes status to `READY`
- Emits `"module:ready"` event

### 3. Event Emission

```python
bus.emit("counter:increment", {"amount": 5})
```

- Bus creates a `TonikaEvent`:
  ```python
  TonikaEvent(
      type="counter:increment",
      detail={"amount": 5},
      _meta=EventMetadata(
          timestamp=1704067200000,
          source="unknown",  # Not sent by a module
          version="0.0.0"
      )
  )
  ```
- Bus looks up handlers for `"counter:increment"`
- Finds `counter.handle_increment`
- Calls it with the event

### 4. Event Handling

```python
def handle_increment(self, event):
    amount = event.detail.get("amount", 1)  # Get amount, default to 1
    self.count += amount                     # Update internal state
    self.emit("counter:changed", {...})      # Announce change
```

- Extracts data from `event.detail`
- Updates internal state
- Emits a new event to announce the change

### 5. Cleanup

```python
counter.destroy()
```

- Unsubscribes from all events
- Removes from module registry
- Emits `"module:destroyed"` event
- Changes status to `DESTROYED`

---

## Adding More Features

### Feature 1: Get Current Count

Add a handler to query the current count:

```python
async def _initialize(self):
    self.count = 0
    self.on("counter:increment", self.handle_increment)
    self.on("counter:reset", self.handle_reset)
    self.on("counter:get", self.handle_get)  # NEW
    print("🔢 CounterGoblin ready to count!")

def handle_get(self, event):
    """Return the current count"""
    request_id = event.detail.get("request_id")
    self.emit("counter:value", {
        "request_id": request_id,
        "count": self.count
    })
```

Usage:
```python
bus.emit("counter:get", {"request_id": "abc123"})
```

### Feature 2: Set Count to Specific Value

```python
async def _initialize(self):
    # ... existing code ...
    self.on("counter:set", self.handle_set)  # NEW

def handle_set(self, event):
    """Set the counter to a specific value"""
    new_value = event.detail.get("value", 0)
    self.count = new_value
    self.emit("counter:changed", {"count": self.count})
    print(f"   Set to {self.count}")
```

Usage:
```python
bus.emit("counter:set", {"value": 100})
```

### Feature 3: Log All Changes

Let's create a **second module** that listens to counter changes:

```python
class CounterLogger(TonikaModule):
    """Logs all counter changes"""
    
    def __init__(self):
        super().__init__(
            name="CounterLogger",
            version="1.0.0",
            description="Logs counter changes"
        )
    
    async def _initialize(self):
        self.history = []
        self.on("counter:changed", self.log_change)
        print("📝 CounterLogger ready!")
    
    def log_change(self, event):
        """Log each counter change"""
        count = event.detail["count"]
        self.history.append(count)
        print(f"   📝 Logged: {count} (history: {self.history})")
```

Add to main:
```python
async def main():
    bus = TonikaBus()
    
    counter = CounterGoblin()
    logger = CounterLogger()  # NEW
    
    await counter.init()
    await logger.init()       # NEW
    
    # ... send events ...
    
    counter.destroy()
    logger.destroy()          # NEW
```

**Output:**
```
🔢 CounterGoblin ready to count!
📝 CounterLogger ready!

📤 Sending increment events...
   Count: 5
   📝 Logged: 5 (history: [5])
   Count: 8
   📝 Logged: 8 (history: [5, 8])
   Count: 10
   📝 Logged: 10 (history: [5, 8, 10])
```

**Notice:** The two modules don't know about each other! They only communicate through events! 🎯

---

## Next Steps

### Learn More

- **[Bus Architecture Guide](BUS_GUIDE.md)** - Deep dive into the Bus
- **[Goblin Laws with Examples](goblin_laws_examples.md)** - Design principles
- **[Testing Guide](TESTING.md)** - How to test your modules

### Try These Exercises

1. **Add decrement**: Create a `handle_decrement` that subtracts from the counter

2. **Add validation**: Reject negative counts, emit `"counter:error"` instead

3. **Add persistence**: Save count to a file when it changes, load on init

4. **Multiple counters**: Create a module that manages multiple named counters

5. **Musical Goblins**: Adapt the example to create:
   - `PianoGoblin` - Emits `"midi:note-on"` events
   - `SynthGoblin` - Listens and "plays" notes
   - `RecorderGoblin` - Records all notes

### Explore Examples

Check out the working examples in [examples](../examples):
- `example_1_simple_counter_module.py` - Similar to what we just built
- `example_2_midi_like_system.py` - MIDI-style event handling
- `example_3_request_response.py` - Request/response patterns
- `example_4_module_dependencies.py` - Module dependencies with `wait_for()`

### Common Pitfalls

**❌ Forgetting to call `init()`:**
```python
counter = CounterGoblin()
# Forgot: await counter.init()
bus.emit("counter:increment", {})  # Handler not registered!
```

**❌ Forgetting to call `destroy()`:**
```python
counter = CounterGoblin()
await counter.init()
# Use module...
# Forgot: counter.destroy()  # Memory leak!
```

**❌ Overriding `init()` instead of `_initialize()`:**
```python
class BadGoblin(TonikaModule):
    async def init(self):  # ❌ WRONG
        self.on("event", self.handle)

class GoodGoblin(TonikaModule):
    async def _initialize(self):  # ✅ CORRECT
        self.on("event", self.handle)
```

**❌ Calling module methods directly:**
```python
counter = CounterGoblin()
await counter.init()

counter.handle_increment(...)  # ❌ VIOLATION OF GOBLIN LAW #37!

bus.emit("counter:increment", {...})  # ✅ CORRECT
```

---

**🧌 Now go create your own Goblins!** 🎵

*Remember: Never Meddle in Another Goblin's Guts!* — Goblin Law #37