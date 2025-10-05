# Examples

See the [examples directory](../examples/) for complete working examples:

- `example_1_simple_counter_module.py` - Basic module creation
- `example_2_midi_like_system.py` - MIDI-style event handling
- `example_3_request_response.py` - Request/response patterns
- `example_4_module_dependencies.py` - Module communication

## Async handlers

Event handlers can be either synchronous or asynchronous. If you register an async (coroutine) handler, the Bus will schedule it as a background task using `asyncio.create_task()` when an event loop is running. This prevents slow handlers from blocking the system. If no event loop is running, the Bus will execute the async handler with `asyncio.run()`.

Example:

```python
import asyncio
from tonika_bus.core.bus import TonikaBus

bus = TonikaBus()

# synchronous handler
bus.on("beat:tick", lambda e: print("tick", e.detail))

# asynchronous handler
async def on_tick_async(event):
    await asyncio.sleep(0.1)  # simulate async work
    print("async tick", event.detail)

bus.on("beat:tick", on_tick_async)

# somewhere in your code
bus.emit("beat:tick", {"n": 1}, source="metronome")
```
