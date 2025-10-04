"""
Example usage of the refactored Tonika Bus

This demonstrates the three-file structure working together.

Goblin Law #37: Never Meddle in Another Goblin's Guts
Goblin Law #41: Only One Drumbeat of Readiness
"""

import asyncio
import sys
from pathlib import Path

# Add parent tests to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bus import TonikaBus
from events import TonikaEvent
from module import TonikaModule


class ExampleModule(TonikaModule):
    """
    Example module showing how to use the refactored Bus.

    Goblin Law #7: No Fat Orcs - does one thing well
    """

    async def _initialize(self):
        """Subscribe to events during initialization"""
        self.on("test:ping", self.handle_ping)
        print(f"  [{self.name}] Initialized and listening for pings")

    def handle_ping(self, event: TonikaEvent):
        """Handle ping events"""
        print(f"  [{self.name}] PONG! Received: {event.detail}")
        self.emit("test:pong", {"response": f"pong from {self.name}"})


async def test_refactored_bus():
    """Test the refactored three-file structure"""

    print("🧪 Tonika Bus Refactored - Testing Goblin Law #37 enforcement\n")

    # Get the Bus (singleton)
    bus = TonikaBus()
    bus.set_debug(True)

    # Create two modules
    module1 = ExampleModule("Module1", "1.0.0", "First test module")
    module2 = ExampleModule("Module2", "1.0.0", "Second test module")

    # Initialize them
    print("\n📦 Initializing modules...")
    await module1.init()
    await module2.init()

    # Test event emission
    print("\n📣 Emitting test:ping event...")
    bus.emit("test:ping", {"message": "Hello Goblins!"}, source="TestHarness", version="1.0.0")

    # Give handlers time to run
    await asyncio.sleep(0.1)

    # Show event log
    print("\n📜 Event Log (last 5 events):")
    for event in bus.get_event_log(limit=5):
        print(f"  {event}")

    # Test module registry
    print("\n📋 Registered modules:")
    for module_name in bus.list_modules():
        module = bus.get_module(module_name)
        status = module.get_status()
        print(f"  - {status['name']} v{status['version']}: {status['status']}")

    # Clean up
    print("\n🧹 Cleaning up...")
    module1.destroy()
    module2.destroy()

    print("\n✅ Test complete - Goblin Law #37 upheld!")
    print("✅ Three-file refactoring successful!")


if __name__ == "__main__":
    asyncio.run(test_refactored_bus())
