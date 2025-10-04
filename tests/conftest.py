"""
Pytest configuration and shared fixtures for tonika_bus tests

This file is automatically loaded by pytest and provides
shared fixtures and configuration for all tests.
"""

import sys
from pathlib import Path

# Add src to path so tests can import tonika_bus
# This allows: from tonika_bus.core.bus import TonikaBus
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from tonika_bus.core.bus import TonikaBus


@pytest.fixture
def fresh_bus():
    """
    Provide a fresh Bus instance for each test.

    Resets the singleton to ensure test isolation.
    Each test gets a clean Bus with no handlers or events.

    Usage:
        def test_something(fresh_bus):
            fresh_bus.emit("test:event", {})
            assert len(fresh_bus.get_event_log()) == 1
    """
    # Reset singleton
    TonikaBus._instance = None
    TonikaBus._initialized = False
    bus = TonikaBus()
    yield bus
    # Cleanup after test
    bus.clear_event_log()


@pytest.fixture
def bus_with_debug(fresh_bus):
    """
    Provide a Bus with debug mode enabled.

    Useful for tests that need to verify debug behavior.

    Usage:
        def test_debug_feature(bus_with_debug):
            assert bus_with_debug.debug is True
    """
    fresh_bus.set_debug(True)
    return fresh_bus
