# Example 3: Request-Response Pattern
# Source: tonika_bus_readme.md → Examples → Example 3
# Requires: `tonika_bus` package available on PYTHONPATH

import asyncio

from tonika_bus import TonikaModule


class DataProvider(TonikaModule):
    async def _initialize(self):
        self.data = {"users": 100, "songs": 500}
        self.on("data:request", self.handle_request)

    def handle_request(self, event):
        request_id = event.detail["request_id"]
        key = event.detail["key"]

        # Send response
        self.emit("data:response", {"request_id": request_id, "value": self.data.get(key)})


class DataConsumer(TonikaModule):
    async def _initialize(self):
        self.on("data:response", self.handle_response)
        self.responses = {}

    def handle_response(self, event):
        request_id = event.detail["request_id"]
        self.responses[request_id] = event.detail["value"]

    def request_data(self, key):
        request_id = f"req_{id(self)}_{key}"
        self.emit("data:request", {"request_id": request_id, "key": key})
        return request_id


async def main():
    provider = DataProvider("Provider", "1.0.0")
    consumer = DataConsumer("Consumer", "1.0.0")

    await provider.init()
    await consumer.init()

    # Request data
    req_id = consumer.request_data("users")

    # Wait briefly to let the response propagate
    await asyncio.sleep(0.1)

    print(f"Users: {consumer.responses.get(req_id)}")

    provider.destroy()
    consumer.destroy()


if __name__ == "__main__":
    asyncio.run(main())
