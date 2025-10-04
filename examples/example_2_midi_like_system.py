# Example 2: MIDI-like System
# Source: tonika_bus_readme.md → Examples → Example 2
# Requires: `tonika_bus` package available on PYTHONPATH

import asyncio
from tonika_bus import TonikaModule

class MidiInputModule(TonikaModule):
    """Simulates MIDI input"""
    def simulate_key_press(self, note, velocity):
        self.emit("midi:note-on", {
            "note": note,
            "velocity": velocity,
            "channel": 1
        })

class SynthModule(TonikaModule):
    """Plays notes"""
    async def _initialize(self):
        self.on("midi:note-on", self.play_note)

    def play_note(self, event):
        note = event.detail["note"]
        velocity = event.detail["velocity"]
        print(f"♪ Playing note {note} at velocity {velocity}")

class RecorderModule(TonikaModule):
    """Records all MIDI events"""
    async def _initialize(self):
        self.recorded = []
        self.on("midi:note-on", self.record_event)

    def record_event(self, event):
        self.recorded.append(event)
        print(f"📼 Recorded: {event.detail}")

async def main():
    midi = MidiInputModule("MidiInput", "1.0.0")
    synth = SynthModule("Synth", "1.0.0")
    recorder = RecorderModule("Recorder", "1.0.0")

    await midi.init()
    await synth.init()
    await recorder.init()

    # Simulate playing
    midi.simulate_key_press(60, 100)  # Middle C
    midi.simulate_key_press(64, 80)   # E
    midi.simulate_key_press(67, 90)   # G

    await asyncio.sleep(0.1)

    print(f"\nTotal recorded: {len(recorder.recorded)} events")

    # Cleanup
    midi.destroy()
    synth.destroy()
    recorder.destroy()

if __name__ == "__main__":
    asyncio.run(main())
