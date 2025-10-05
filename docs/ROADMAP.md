# Tonika Bus Roadmap

**Planned features and development timeline**

This roadmap outlines the planned development of Tonika Bus and its ecosystem. All dates are estimates and subject to change based on community needs and project priorities.

---

## Table of Contents

- [Project Status](#project-status)
- [Completed Phases](#completed-phases)
- [Phase 2: Integration Layer (Current)](#phase-2-integration-layer-current)
- [Phase 3: Presentation Layer](#phase-3-presentation-layer)
- [Phase 4: Community Platform](#phase-4-community-platform)
- [Future Considerations](#future-considerations)
- [Contributing](#contributing)

---

## Project Status

**Current Version:** 0.2.0  
**Current Phase:** Phase 2 - Integration Layer  
**Status:** Foundation building - Core Bus is stable, adapters in development

---

## Completed Phases

### ✅ Phase 1: Core Foundation (Complete)

**Status:** Released as v0.2.0

**Achievements:**
- ✅ TonikaBus singleton event broker
- ✅ TonikaModule base class with lifecycle management
- ✅ Event structures (TonikaEvent, EventMetadata, ModuleStatus)
- ✅ Full async/await support
- ✅ Event logging and debugging
- ✅ Module registry
- ✅ Comprehensive test suite (100+ tests)
- ✅ High test coverage (93%+)
- ✅ Type hints throughout
- ✅ Documentation (Bus Guide, First Module tutorial, Goblin Laws)
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Coverage reporting (Coveralls)
- ✅ Read the Docs integration

**Key Decisions:**
- Zero runtime dependencies for core
- GPL-3.0 license
- Singleton Bus pattern
- Standardized module lifecycle

---

## Phase 2: Integration Layer (Current)

**Timeline:** Q1-Q2 2025  
**Status:** In Progress  
**Goal:** Create adapters for mature libraries (MIDI, music theory)

### 2.1 MIDI Adapters

**Priority:** High  
**Timeline:** Q1 2025  
**Status:** Planned

#### MIDI Input Adapter

**Description:** Real-time MIDI input from hardware devices

**Dependencies:**
- `mido` (MIT License, GPL-3 compatible)
- `python-rtmidi` (MIT License, GPL-3 compatible)

**Features:**
- Auto-detect available MIDI ports
- Subscribe to specific ports
- Emit standardized `midi:message` events
- Handle device connect/disconnect
- Buffer overflow protection
- Low latency (< 5ms typical)

**Events Emitted:**
```python
"midi:ports:available"  # List of detected ports
"midi:port:opened"      # Port opened successfully
"midi:port:closed"      # Port closed
"midi:message"          # MIDI message received
"midi:error"            # Error occurred
```

**Example Usage:**
```python
from tonika_bus.adapters.midi import MidiInputAdapter

midi = MidiInputAdapter(name="MidiIn", version="1.0.0")
await midi.init()

# Automatically emits events for all MIDI input
```

**GitHub Issue:** [#TBD - MIDI Input Adapter](https://github.com/aa-parky/tonika_bus/issues)

---

#### MIDI Output Adapter

**Description:** Send MIDI to hardware devices

**Features:**
- Auto-detect available output ports
- Send MIDI messages via events
- Handle timing and buffering
- Support for MIDI clock sync

**Events Subscribed:**
```python
"midi:send"             # Send MIDI message
"midi:port:select"      # Select output port
```

**Events Emitted:**
```python
"midi:sent"             # Message sent successfully
"midi:output:error"     # Error sending
```

**GitHub Issue:** [#TBD - MIDI Output Adapter](https://github.com/aa-parky/tonika_bus/issues)

---

#### MIDI File Adapter

**Description:** Read and write MIDI files

**Features:**
- Load MIDI files
- Parse into events
- Write event streams to MIDI files
- Tempo and time signature handling

**Events:**
```python
"midi:file:load"        # Load MIDI file
"midi:file:loaded"      # File loaded successfully
"midi:file:save"        # Save to MIDI file
"midi:file:saved"       # File saved successfully
```

**GitHub Issue:** [#TBD - MIDI File Adapter](https://github.com/aa-parky/tonika_bus/issues)

---

### 2.2 Music Theory Adapters

**Priority:** Medium  
**Timeline:** Q2 2025  
**Status:** Planned

#### Chord Analyzer Adapter

**Description:** Real-time chord detection from MIDI notes

**Dependencies:**
- `music21` (BSD License, GPL-3 compatible)

**Features:**
- Detect chord from set of notes
- Identify chord inversions
- Suggest chord symbols
- Voice leading analysis

**Events:**
```python
"theory:notes"          # Subscribe to note sets
"theory:chord"          # Emit detected chord
"theory:chord:change"   # Chord changed
```

**Example:**
```python
from tonika_bus.adapters.theory import ChordAnalyzer

analyzer = ChordAnalyzer(name="Chords", version="1.0.0")
await analyzer.init()

# Listens to "theory:notes" events
# Emits "theory:chord" events
```

**GitHub Issue:** [#TBD - Chord Analyzer](https://github.com/aa-parky/tonika_bus/issues)

---

#### Scale Analyzer Adapter

**Description:** Detect scales and modes from note sets

**Features:**
- Identify scale/mode from notes
- Suggest scale degrees
- Analyze key centers
- Modal interchange detection

**Events:**
```python
"theory:notes"          # Subscribe to note sets
"theory:scale"          # Emit detected scale
"theory:key"            # Emit detected key center
```

**GitHub Issue:** [#TBD - Scale Analyzer](https://github.com/aa-parky/tonika_bus/issues)

---

### 2.3 Additional Adapters (Exploratory)

**Priority:** Low  
**Timeline:** Q2-Q3 2025  
**Status:** Research phase

#### Audio Processing Adapter

**Description:** Real-time audio processing

**Candidates:**
- `sounddevice` (MIT) - Audio I/O
- `numpy` (BSD) - DSP operations
- `scipy` (BSD) - Signal processing

**Features:**
- Audio input/output
- FFT analysis
- Filtering
- Effects processing

**Status:** Evaluating libraries and approach

**GitHub Issue:** [#TBD - Audio Processing](https://github.com/aa-parky/tonika_bus/issues)

---

#### OSC Adapter

**Description:** Open Sound Control protocol support

**Candidates:**
- `python-osc` (Public Domain)

**Features:**
- OSC message send/receive
- Integration with DAWs and controllers
- Network sync

**Status:** Community interest needed

**GitHub Issue:** [#TBD - OSC Support](https://github.com/aa-parky/tonika_bus/issues)

---

### 2.4 Documentation & Examples

**Priority:** High  
**Timeline:** Ongoing through Q1-Q2 2025

**Planned:**
- [ ] Comprehensive adapter documentation
- [ ] Real-world example projects
- [ ] Video tutorials
- [ ] Integration cookbook
- [ ] Performance optimization guide

---

## Phase 3: Presentation Layer

**Timeline:** Q3-Q4 2025  
**Status:** Planning phase  
**Goal:** Create visual components and UI framework

### 3.1 Web-Based UI Framework

**Description:** Browser-based rack interface for Tonika modules

**Tech Stack (Proposed):**
- HTML/CSS/JavaScript (no framework initially)
- WebSockets for Bus communication
- Canvas or SVG for visualizations

**Features:**
- Module rack visualization
- Drag-and-drop module loading
- Real-time event visualization
- Parameter controls
- Preset management

**Status:** Early design phase

**GitHub Issue:** [#TBD - Web UI Framework](https://github.com/aa-parky/tonika_bus/issues)

---

### 3.2 Visualization Modules

**Planned Modules:**
- Keyboard visualizer (piano roll)
- Waveform display
- Spectrum analyzer
- Chord diagram
- Scale diagram
- Event log viewer

**Status:** Concept phase

---

### 3.3 Theme System

**Description:** Pluggable theme system for UI components

**Architecture:**
```
Theme Layer      ← Actual colors, fonts, spacing
    ↓
Semantic Layer   ← Meanings: primary, accent, muted
    ↓
Component Layer  ← How components use semantics
```

**Status:** Design document in progress

**See:** [docs/UI_ARCHITECTURE.md](UI_ARCHITECTURE.md) (coming soon)

---

## Phase 4: Community Platform

**Timeline:** 2026  
**Status:** Roadmap planning  
**Goal:** Open for community contributions and plugin ecosystem

### 4.1 Plugin System

**Features:**
- Module discovery
- Hot-reloading
- Version management
- Dependency resolution

**Status:** Requirements gathering

---

### 4.2 Module Repository

**Description:** Community repository for sharing modules

**Features:**
- Module search and discovery
- Ratings and reviews
- Documentation requirements
- Quality guidelines

**Status:** Concept phase

---

### 4.3 Developer Tools

**Planned:**
- Module scaffolding CLI
- Testing utilities
- Performance profiling
- Debug visualizations
- Module validation tools

**Status:** Gathering requirements

---

## Future Considerations

### Beyond 2026

These are ideas under consideration but not yet committed:

#### Advanced Features
- [ ] Distributed Bus (network-connected instances)
- [ ] Persistent event log (time-travel debugging)
- [ ] Visual programming interface (node-based)
- [ ] Machine learning adapters
- [ ] Cloud synchronization
- [ ] Mobile app

#### Ecosystem Growth
- [ ] Plugin marketplace
- [ ] Commercial support options
- [ ] Training and certification
- [ ] Conference/community events

#### Platform Support
- [ ] Standalone executables (PyInstaller)
- [ ] Docker containers
- [ ] Raspberry Pi optimization
- [ ] iOS/Android apps

**Note:** These are aspirational and dependent on community interest and resources.

---

## Contributing

### How to Contribute to the Roadmap

**Current Phase (Phase 2):**
- Test MIDI adapters when available
- Report bugs and edge cases
- Suggest music theory features
- Contribute documentation improvements

**Future Phases:**
- Vote on features via GitHub issues
- Propose new adapters
- Share use cases
- Contribute example projects

### Priority Criteria

Features are prioritized based on:

1. **Foundation First** - Core stability before extensions
2. **Community Need** - Most requested features
3. **Maintainability** - Sustainable to support long-term
4. **GPL-3 Compatibility** - License compliance
5. **Goblin Law Compliance** - Architectural fit

### Suggesting New Features

Open a GitHub issue with:
- **Use Case** - What problem does it solve?
- **Proposed Solution** - How should it work?
- **Alternatives Considered** - What else did you think about?
- **Implementation Notes** - Any technical considerations?

**Issue Template:** [New Feature Request](https://github.com/aa-parky/tonika_bus/issues/new?template=feature_request.md)

---

## Release Schedule

### Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **Major (X.0.0)** - Breaking changes
- **Minor (0.X.0)** - New features, backward compatible
- **Patch (0.0.X)** - Bug fixes

### Planned Releases

**v0.2.x (Q1 2025)** - Bug fixes and polish  
**v0.3.0 (Q1 2025)** - MIDI Input Adapter  
**v0.4.0 (Q2 2025)** - MIDI Output & File Adapters  
**v0.5.0 (Q2 2025)** - Music Theory Adapters  
**v0.6.0 (Q3 2025)** - Audio Processing (if ready)  
**v0.7.0 (Q3 2025)** - Web UI Framework (alpha)  
**v0.8.0 (Q4 2025)** - Visualization Modules  
**v0.9.0 (Q4 2025)** - Beta release with full documentation  
**v1.0.0 (2026)** - Stable release, community platform opens

**Note:** Dates are estimates and may shift based on progress and feedback.

---

## Tracking Progress

### GitHub Project Board

Track development progress on the [Tonika Bus Project Board](https://github.com/aa-parky/tonika_bus/projects).

### Milestones

View detailed milestone progress: [GitHub Milestones](https://github.com/aa-parky/tonika_bus/milestones)

### Discussion Forum

Join the conversation: [GitHub Discussions](https://github.com/aa-parky/tonika_bus/discussions)

---

## See Also

- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and past changes
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - How to contribute
- **[GitHub Issues](https://github.com/aa-parky/tonika_bus/issues)** - Bug reports and feature requests
- **[GitHub Projects](https://github.com/aa-parky/tonika_bus/projects)** - Development board

---

**🧌 Help shape the future of Tonika!** 🎵

*This roadmap is a living document. Join the discussion on GitHub to influence priorities and direction.*