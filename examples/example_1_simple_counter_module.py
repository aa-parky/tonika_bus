# Example 1: Simple Counter Module
# Source: tonika_bus_readme.md → Examples → Example 1
# Requires: `tonika_bus` package available on PYTHONPATH

import asyncio

from tonika_bus import TonikaBus, TonikaModule


class CounterModule(TonikaModule):
    async def _initialize(self):
        self.count = 0
        self.on("counter:increment", self.increment)
        self.on("counter:reset", self.reset)

    def increment(self, event):
        self.count += event.detail.get("amount", 1)
        self.emit("counter:changed", {"count": self.count})
        print(f"Count: {self.count}")

    def reset(self, event):
        self.count = 0
        self.emit("counter:changed", {"count": self.count})


async def main():
    bus = TonikaBus()
    counter = CounterModule("Counter", "1.0.0")
    await counter.init()

    bus.emit("counter:increment", {"amount": 5})
    bus.emit("counter:increment", {"amount": 3})
    bus.emit("counter:reset", {})

    await asyncio.sleep(0.1)  # Let handlers run
    counter.destroy()


if __name__ == "__main__":
    asyncio.run(main())
