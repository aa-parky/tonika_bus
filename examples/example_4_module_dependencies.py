# Example 4: Module Dependencies
# Source: tonika_bus_readme.md → Examples → Example 4
# Requires: `tonika_bus` package available on PYTHONPATH

import asyncio
from tonika_bus import TonikaModule

class DatabaseModule(TonikaModule):
    async def _initialize(self):
        await asyncio.sleep(0.5)  # Simulate DB connection
        self.emit("database:ready", {})
        print("✅ Database ready")

class ApiModule(TonikaModule):
    async def _initialize(self):
        # Wait for database before starting
        print("⏳ Waiting for database...")
        await self.wait_for("database:ready", timeout_ms=5000)
        print("✅ API ready - database is available")

async def main():
    db = DatabaseModule("Database", "1.0.0")
    api = ApiModule("API", "1.0.0")

    # Start both (API will wait for DB)
    await asyncio.gather(
        db.init(),
        api.init()
    )

    db.destroy()
    api.destroy()

if __name__ == "__main__":
    asyncio.run(main())
