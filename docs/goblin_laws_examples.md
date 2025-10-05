# Goblin Laws with Examples

**Design principles that guide Tonika development**

These are the ancient laws followed by Tonika Goblins—hard-earned wisdom carved into code. Each law comes with real examples showing what to do (and what not to do).

![tonika_goblin_law_small.png](../assets/images/tonika_goblin_law_small.png)

---

## Table of Contents

- [Core Programming Laws](#core-programming-laws)
  - [Law #37: Never Meddle in Another Goblin's Guts](#law-37-never-meddle-in-another-goblins-guts)
  - [Law #41: Only One Drumbeat of Readiness](#law-41-only-one-drumbeat-of-readiness)
  - [Law #7: No Fat Orcs](#law-7-no-fat-orcs)
  - [Law #8: All Goblins Are Boundary Guards](#law-8-all-goblins-are-boundary-guards)
  - [Law #32: Never Patch a Monkey](#law-32-never-patch-a-monkey)
  - [Law #13: Keep the Guest List Clean](#law-13-keep-the-guest-list-clean)
- [How Laws Work Together](#how-laws-work-together)
- [Common Violations and Fixes](#common-violations-and-fixes)

---

## Core Programming Laws

### Law #37: Never Meddle in Another Goblin's Guts

**Rule:** Modules must NEVER directly access or modify another module's internal state.

**Why:** Direct coupling makes code fragile, untestable, and impossible to change. When Goblins poke each other's guts, everything breaks.

**Enforcement:** The Bus is the ONLY communication channel between modules.

#### ❌ VIOLATION

```python
# Direct meddling - BAD!
class Sequencer:
    def __init__(self, synth, recorder):
        self.synth = synth          # Direct reference
        self.recorder = recorder    # Direct reference
    
    def play_pattern(self):
        # Directly accessing internal state
        self.synth.oscillator.frequency = 440
        self.synth.oscillator.waveform = "sine"
        
        # Directly calling methods
        self.synth.play_note(60)
        self.recorder.start_recording()
```

**Problems:**
- Sequencer tightly coupled to Synth and Recorder
- Can't swap Synth implementation
- Can't add new listeners (e.g., Visualizer)
- Hard to test Sequencer in isolation
- Changes to Synth break Sequencer

#### ✅ COMPLIANCE

```python
# Bus communication - GOOD!
class Sequencer(TonikaModule):
    def play_pattern(self):
        # Just emit events
        self.emit("synth:configure", {
            "frequency": 440,
            "waveform": "sine"
        })
        self.emit("midi:note-on", {"note": 60})
        self.emit("recorder:start", {})

class Synth(TonikaModule):
    async def _initialize(self):
        self.on("synth:configure", self.configure)
        self.on("midi:note-on", self.play_note)
    
    def configure(self, event):
        self.oscillator.frequency = event.detail["frequency"]
        self.oscillator.waveform = event.detail["waveform"]
    
    def play_note(self, event):
        # Play the note
        pass

class Recorder(TonikaModule):
    async def _initialize(self):
        self.on("recorder:start", self.start_recording)
    
    def start_recording(self, event):
        # Start recording
        pass
```

**Benefits:**
- Zero coupling between modules
- Can swap Synth implementation without touching Sequencer
- Easy to add Visualizer module (just subscribe to events)
- Each module testable in isolation
- Changes to Synth don't affect Sequencer

#### The Bus Inspection Exception

You **can** use `bus.get_module()` for inspection, but **never** for calling methods:

```python
# ✅ OK: Inspection only
synth = bus.get_module("Synth")
if synth:
    status = synth.get_status()
    print(f"Synth status: {status['status']}")

# ❌ VIOLATION: Calling methods
synth = bus.get_module("Synth")
synth.play_note(60)  # FORBIDDEN!
```

---

### Law #41: Only One Drumbeat of Readiness

**Rule:** Only the base `TonikaModule` class emits lifecycle events (`module:initializing`, `module:ready`, `module:error`, `module:destroyed`).

**Why:** If every Goblin drums their own beat, nobody knows when anyone is ready. Standardized lifecycle makes the system predictable.

**Enforcement:** Subclasses override `_initialize()`, **NOT** `init()`.

#### ❌ VIOLATION

```python
# Override init() - BAD!
class BadGoblin(TonikaModule):
    async def init(self):
        # Custom initialization
        self.data = []
        self.on("event", self.handle)
        
        # Manually emit ready
        self.emit("module:ready", {})
        self.status = ModuleStatus.READY
```

**Problems:**
- Breaks standardized lifecycle
- Might not emit events in correct order
- Other modules can't rely on lifecycle events
- Inconsistent with other modules

#### ✅ COMPLIANCE

```python
# Override _initialize() - GOOD!
class GoodGoblin(TonikaModule):
    async def _initialize(self):
        # Custom initialization
        self.data = []
        self.on("event", self.handle)
        
        # No need to emit lifecycle events!
        # TonikaModule.init() handles that
```

**Benefits:**
- Consistent lifecycle across all modules
- Reliable lifecycle events
- Other modules can depend on `"module:ready"`
- Less code to write

#### Domain Events Are Fine

You **can** emit your own domain-specific events:

```python
class Synth(TonikaModule):
    async def _initialize(self):
        self.voices = []
        
        # ✅ Domain event - GOOD!
        self.emit("synth:voices:allocated", {
            "count": len(self.voices)
        })
```

**Lifecycle events (reserved):**
- `module:initializing` ← TonikaModule only
- `module:ready` ← TonikaModule only
- `module:error` ← TonikaModule only
- `module:destroyed` ← TonikaModule only

**Domain events (yours to use):**
- `synth:*` ← Your domain
- `midi:*` ← Your domain
- `recorder:*` ← Your domain

---

### Law #7: No Fat Orcs

**Rule:** Each module does ONE thing well.

**Why:** A Goblin who tries to do everything does nothing well. Complexity is debt. Simplicity is freedom.

**Guidance:** If a module is doing too many things, split it into multiple modules that communicate via the Bus.

#### ❌ VIOLATION

```python
# Fat Orc - BAD!
class MegaModule(TonikaModule):
    async def _initialize(self):
        # MIDI input
        self.midi_port = mido.open_input()
        self.on_midi_message = self.handle_midi
        
        # Audio recording
        self.audio_buffer = []
        self.recording = False
        
        # Chord analysis
        self.chord_detector = ChordDetector()
        self.current_chord = None
        
        # Visualization
        self.visualizer = Visualizer()
        self.colors = {}
        
        # File export
        self.export_path = "/tmp"
        
        # Network sync
        self.sync_server = SyncServer()
    
    def handle_midi(self, msg):
        # Too much responsibility!
        self.record_audio(msg)
        self.analyze_chord(msg)
        self.update_visualization(msg)
        self.sync_to_network(msg)
        self.export_to_file(msg)
```

**Problems:**
- Doing 6 different jobs
- Hard to test
- Hard to maintain
- Can't reuse components
- Changes ripple everywhere

#### ✅ COMPLIANCE

```python
# Lean Goblins - GOOD!
class MidiInputModule(TonikaModule):
    """One job: Read MIDI and emit events"""
    async def _initialize(self):
        self.midi_port = mido.open_input()
        asyncio.create_task(self._poll_midi())
    
    async def _poll_midi(self):
        for msg in self.midi_port:
            self.emit("midi:message", {
                "type": msg.type,
                "note": msg.note,
                "velocity": msg.velocity
            })

class AudioRecorderModule(TonikaModule):
    """One job: Record audio"""
    async def _initialize(self):
        self.buffer = []
        self.on("midi:message", self.record)
    
    def record(self, event):
        self.buffer.append(event.detail)

class ChordAnalyzerModule(TonikaModule):
    """One job: Analyze chords"""
    async def _initialize(self):
        self.detector = ChordDetector()
        self.on("midi:message", self.analyze)
    
    def analyze(self, event):
        chord = self.detector.detect(event.detail)
        self.emit("theory:chord", {"chord": chord})

class VisualizerModule(TonikaModule):
    """One job: Visualize notes"""
    async def _initialize(self):
        self.on("midi:message", self.visualize)
    
    def visualize(self, event):
        # Draw visualization
        pass

class FileExporterModule(TonikaModule):
    """One job: Export to files"""
    async def _initialize(self):
        self.on("recorder:save", self.export)
    
    def export(self, event):
        # Export data
        pass

class NetworkSyncModule(TonikaModule):
    """One job: Sync over network"""
    async def _initialize(self):
        self.on("sync:data", self.sync)
    
    def sync(self, event):
        # Sync to network
        pass
```

**Benefits:**
- Each module does one thing well
- Easy to test individually
- Easy to reuse components
- Changes stay local
- Can disable features by not loading modules

#### The "One Thing" Test

Ask yourself: **"Can I describe this module in one sentence without using 'and'?"**

```
✅ "Reads MIDI input and emits events" → OK
✅ "Analyzes chords from MIDI notes" → OK
❌ "Reads MIDI input and records audio and analyzes chords and draws visualizations" → TOO MUCH!
```

---

### Law #8: All Goblins Are Boundary Guards

**Rule:** Every module that touches the "outside world" (hardware, files, network) must immediately report to the Bus.

**Why:** The Bus needs to know what's happening in the real world. Keeping secrets creates blind spots in the system.

**Enforcement:** Boundary modules emit events immediately upon receiving external input.

#### ❌ VIOLATION

```python
# Keeping secrets - BAD!
class MidiInputModule(TonikaModule):
    async def _initialize(self):
        self.buffer = []  # Internal buffer
        asyncio.create_task(self._poll_midi())
    
    async def _poll_midi(self):
        for msg in self.midi_port:
            # Store internally - Bus doesn't know!
            self.buffer.append(msg)
    
    def get_buffer(self):
        # Other modules have to ask
        return self.buffer
```

**Problems:**
- Bus doesn't know about MIDI input
- Other modules can't react in real-time
- Have to poll for updates
- Violates Law #37 (direct access to buffer)

#### ✅ COMPLIANCE

```python
# Immediate reporting - GOOD!
class MidiInputModule(TonikaModule):
    async def _initialize(self):
        asyncio.create_task(self._poll_midi())
    
    async def _poll_midi(self):
        for msg in self.midi_port:
            # Tell the Bus immediately!
            self.emit("midi:message", {
                "type": msg.type,
                "note": msg.note,
                "velocity": msg.velocity,
                "timestamp": time.time()
            })
```

**Benefits:**
- Real-time event propagation
- Other modules can react immediately
- Observable system state
- Event log for debugging

#### Boundary Examples

**File I/O:**
```python
class ConfigLoader(TonikaModule):
    def load_file(self, path):
        data = json.load(open(path))
        # Tell the Bus immediately!
        self.emit("config:loaded", {"data": data})
```

**Network:**
```python
class NetworkModule(TonikaModule):
    async def _initialize(self):
        self.on("network:connect", self._connect)
    
    async def _connect(self, event):
        result = await self.network.connect()
        # Tell the Bus immediately!
        self.emit("network:connected", {"result": result})
```

**Hardware:**
```python
class AudioInputModule(TonikaModule):
    def on_audio_buffer(self, buffer):
        # Got audio from hardware
        # Tell the Bus immediately!
        self.emit("audio:input", {
            "samples": buffer,
            "sample_rate": 44100
        })
```

---

### Law #32: Never Patch a Monkey

**Rule:** Don't modify functions or classes from other modules or libraries at runtime.

**Why:** Monkey patching makes code unpredictable and breaks assumptions. It's a shortcut that creates long-term problems.

**Enforcement:** Use composition, inheritance, or adapters instead of patching.

#### ❌ VIOLATION

```python
# Monkey patching - BAD!
import mido

# Modify library function
original_open = mido.open_input
def patched_open(*args, **kwargs):
    print("Opening MIDI port")
    return original_open(*args, **kwargs)

mido.open_input = patched_open  # Monkey patch!
```

**Problems:**
- Breaks assumptions
- Hard to debug
- Affects entire program
- Fragile across library versions

#### ✅ COMPLIANCE

```python
# Composition - GOOD!
class MidiPortWrapper:
    """Wrapper around mido.open_input"""
    
    def __init__(self):
        self.port = None
    
    def open(self, *args, **kwargs):
        print("Opening MIDI port")
        self.port = mido.open_input(*args, **kwargs)
        return self.port
```

Or use an adapter module:

```python
class MidiInputAdapter(TonikaModule):
    """Adapter for mido library"""
    
    async def _initialize(self):
        self.port = mido.open_input()
        asyncio.create_task(self._poll())
    
    async def _poll(self):
        for msg in self.port:
            # Emit standardized events
            self.emit("midi:message", self._convert(msg))
    
    def _convert(self, msg):
        """Convert mido message to our format"""
        return {
            "type": msg.type,
            "note": msg.note,
            "velocity": msg.velocity
        }
```

---

### Law #13: Keep the Guest List Clean

**Rule:** The Bus maintains a single, authoritative registry of all active modules.

**Why:** Having one clean list prevents confusion about who's in the room. Multiple registries create inconsistency.

**Enforcement:** Modules auto-register on creation and auto-unregister on destruction.

#### ❌ VIOLATION

```python
# Multiple registries - BAD!
class MySystem:
    def __init__(self):
        self.modules = {}  # My own registry
        self.active = []   # Another list
        self.names = set() # Yet another
    
    def add_module(self, module):
        self.modules[module.name] = module
        self.active.append(module)
        self.names.add(module.name)
        # Now we have THREE lists to maintain!
```

**Problems:**
- Multiple sources of truth
- Lists can get out of sync
- Hard to know what's actually active

#### ✅ COMPLIANCE

```python
# Single registry (the Bus) - GOOD!
class TonikaModule:
    def __init__(self, name, version):
        # ...
        self._bus = TonikaBus()
        self._bus.register_module(self)  # Single registration
    
    def destroy(self):
        # ...
        self._bus.unregister_module(self.name)  # Single cleanup

# Query the single registry
modules = bus.list_modules()  # One source of truth
module = bus.get_module("Synth")  # Always accurate
```

---

## How Laws Work Together

The laws are not isolated—they form a cohesive system:

### Example: MIDI Input System

```python
# Law #8: Boundary Guard
class MidiInputAdapter(TonikaModule):
    """Touches hardware, reports immediately"""
    async def _initialize(self):
        asyncio.create_task(self._poll())
    
    async def _poll(self):
        for msg in self.midi_port:
            # Law #8: Report immediately
            self.emit("midi:message", {
                "note": msg.note,
                "velocity": msg.velocity
            })

# Law #7: No Fat Orcs (focused on one job)
class ChordAnalyzer(TonikaModule):
    """Only analyzes chords"""
    async def _initialize(self):
        # Law #37: Use Bus, not direct reference
        self.on("midi:message", self.analyze)
    
    def analyze(self, event):
        chord = detect_chord(event.detail["note"])
        # Law #37: Emit, don't call directly
        self.emit("theory:chord", {"chord": chord})

# Law #7: No Fat Orcs (focused on one job)
class MidiRecorder(TonikaModule):
    """Only records MIDI"""
    async def _initialize(self):
        # Law #37: Use Bus, not direct reference
        self.on("midi:message", self.record)
    
    def record(self, event):
        self.buffer.append(event.detail)

# Law #13: Single registry
async def main():
    bus = TonikaBus()
    
    # All auto-register
    midi = MidiInputAdapter(name="MIDI", version="1.0.0")
    analyzer = ChordAnalyzer(name="Chords", version="1.0.0")
    recorder = MidiRecorder(name="Recorder", version="1.0.0")
    
    # Law #41: Standardized init
    await midi.init()      # "module:initializing" → "module:ready"
    await analyzer.init()  # "module:initializing" → "module:ready"
    await recorder.init()  # "module:initializing" → "module:ready"
    
    # Law #13: Query single registry
    print(bus.list_modules())  # ["MIDI", "Chords", "Recorder"]
```

---

## Common Violations and Fixes

### Violation: Direct Method Calls

```python
# ❌ VIOLATION: Direct call
synth = bus.get_module("Synth")
synth.play_note(60)

# ✅ FIX: Use events
bus.emit("synth:note:play", {"note": 60})
```

### Violation: Overriding init()

```python
# ❌ VIOLATION: Override init
class BadModule(TonikaModule):
    async def init(self):
        self.setup()

# ✅ FIX: Override _initialize
class GoodModule(TonikaModule):
    async def _initialize(self):
        self.setup()
```

### Violation: Module Doing Too Much

```python
# ❌ VIOLATION: Fat Orc
class MegaModule(TonikaModule):
    def handle_midi_and_record_and_visualize(self):
        # Too much!
        pass

# ✅ FIX: Split into focused modules
class MidiHandler(TonikaModule): pass
class Recorder(TonikaModule): pass
class Visualizer(TonikaModule): pass
```

### Violation: Keeping Secrets

```python
# ❌ VIOLATION: Not reporting to Bus
class Sensor(TonikaModule):
    def on_sensor_data(self, data):
        self.internal_cache.append(data)  # Secret!

# ✅ FIX: Report immediately
class Sensor(TonikaModule):
    def on_sensor_data(self, data):
        self.emit("sensor:data", {"value": data})
```

---

## See Also

- **[Bus Architecture Guide](BUS_GUIDE.md)** - Understanding the Bus
- **[Writing Your First Module](FIRST_MODULE.md)** - Module basics
- **[Testing Guide](TESTING.md)** - How to test your modules

---

**🧌 Follow the Laws, and your code will be clean!** 🎵

*Remember: Never Meddle in Another Goblin's Guts!* — Goblin Law #37