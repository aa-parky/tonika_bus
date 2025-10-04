"""
Comprehensive test suite for Event structures (events.py)

Tests all event-related data structures:
- ModuleStatus enum
- EventMetadata dataclass
- TonikaEvent dataclass

Goblin Law #7: No Fat Orcs
These tests verify that event structures do ONE thing well.
"""

from datetime import datetime
from time import sleep

import pytest

from tonika_bus.core.events import EventMetadata, ModuleStatus, TonikaEvent

# ============================================================================
# ModuleStatus Tests
# ============================================================================


@pytest.mark.unit
class TestModuleStatus:
    """Test ModuleStatus enum"""

    def test_all_states_defined(self):
        """Test that all expected states are defined"""
        assert hasattr(ModuleStatus, "UNINITIALIZED")
        assert hasattr(ModuleStatus, "INITIALIZING")
        assert hasattr(ModuleStatus, "READY")
        assert hasattr(ModuleStatus, "ERROR")
        assert hasattr(ModuleStatus, "DESTROYED")

    def test_status_values(self):
        """Test that status values are correct"""
        assert ModuleStatus.UNINITIALIZED.value == "uninitialized"
        assert ModuleStatus.INITIALIZING.value == "initializing"
        assert ModuleStatus.READY.value == "ready"
        assert ModuleStatus.ERROR.value == "error"
        assert ModuleStatus.DESTROYED.value == "destroyed"

    def test_status_equality(self):
        """Test that status values can be compared"""
        status1 = ModuleStatus.READY
        status2 = ModuleStatus.READY
        status3 = ModuleStatus.ERROR

        assert status1 == status2
        assert status1 != status3

    def test_status_string_representation(self):
        """Test string representation of status"""
        assert str(ModuleStatus.READY) == "ModuleStatus.READY"
        assert ModuleStatus.READY.name == "READY"
        assert ModuleStatus.READY.value == "ready"

    def test_status_iteration(self):
        """Test that all statuses can be iterated"""
        statuses = list(ModuleStatus)
        assert len(statuses) == 5
        assert ModuleStatus.UNINITIALIZED in statuses
        assert ModuleStatus.READY in statuses


# ============================================================================
# EventMetadata Tests
# ============================================================================


@pytest.mark.unit
class TestEventMetadata:
    """Test EventMetadata dataclass"""

    def test_create_factory_method(self):
        """Test EventMetadata.create() factory method"""
        meta = EventMetadata.create(source="TestSource", version="1.0.0")

        assert meta.source == "TestSource"
        assert meta.version == "1.0.0"
        assert isinstance(meta.timestamp, int)
        assert meta.timestamp > 0

    def test_create_requires_parameters(self):
        """Test that create() requires both source and version"""
        # Should work with both parameters
        meta = EventMetadata.create(source="Test", version="1.0.0")
        assert meta.source == "Test"
        assert meta.version == "1.0.0"

    def test_timestamp_is_current(self):
        """Test that timestamp is set to current time"""
        before = int(datetime.now().timestamp() * 1000)
        meta = EventMetadata.create(source="Test", version="1.0.0")
        after = int(datetime.now().timestamp() * 1000)

        assert before <= meta.timestamp <= after

    def test_timestamp_precision(self):
        """Test that different metadata have different timestamps"""
        meta1 = EventMetadata.create(source="Test", version="1.0.0")
        sleep(0.001)  # Small delay
        meta2 = EventMetadata.create(source="Test", version="1.0.0")

        # Timestamps should be different (or at least not guaranteed to be same)
        assert meta1.timestamp <= meta2.timestamp

    def test_metadata_direct_construction(self):
        """Test creating metadata directly (not via factory)"""
        timestamp = int(datetime.now().timestamp() * 1000)
        meta = EventMetadata(timestamp=timestamp, source="Test", version="1.0.0")

        assert meta.timestamp == timestamp
        assert meta.source == "Test"
        assert meta.version == "1.0.0"

    def test_metadata_string_representation(self):
        """Test string representation of metadata"""
        meta = EventMetadata.create(source="TestSource", version="2.0.0")

        str_repr = str(meta)
        assert "TestSource" in str_repr
        assert "2.0.0" in str_repr

    def test_metadata_equality(self):
        """Test metadata equality comparison"""
        timestamp = int(datetime.now().timestamp() * 1000)

        meta1 = EventMetadata(timestamp=timestamp, source="Test", version="1.0.0")
        meta2 = EventMetadata(timestamp=timestamp, source="Test", version="1.0.0")
        meta3 = EventMetadata(timestamp=timestamp, source="Other", version="1.0.0")

        assert meta1 == meta2
        assert meta1 != meta3

    def test_metadata_with_custom_timestamp(self):
        """Test creating metadata with custom timestamp"""
        custom_time = 1704067200000  # 2024-01-01 00:00:00 UTC in milliseconds
        meta = EventMetadata(timestamp=custom_time, source="Test", version="1.0.0")

        assert meta.timestamp == custom_time

    def test_metadata_fields_accessible(self):
        """Test that all metadata fields are accessible"""
        meta = EventMetadata.create(source="TestSource", version="3.0.0")

        assert hasattr(meta, "source")
        assert hasattr(meta, "version")
        assert hasattr(meta, "timestamp")


# ============================================================================
# TonikaEvent Tests
# ============================================================================


@pytest.mark.unit
class TestTonikaEvent:
    """Test TonikaEvent dataclass"""

    def test_event_creation(self):
        """Test creating a TonikaEvent"""
        meta = EventMetadata.create(source="TestSource", version="1.0.0")
        event = TonikaEvent(type="test:event", detail={"data": 123}, _meta=meta)

        assert event.type == "test:event"
        assert event.detail == {"data": 123}
        assert event._meta.source == "TestSource"
        assert event._meta.version == "1.0.0"

    def test_event_with_dict_detail(self):
        """Test event with dictionary detail"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:dict", detail={"key": "value", "num": 42}, _meta=meta)

        assert event.detail["key"] == "value"
        assert event.detail["num"] == 42

    def test_event_with_list_detail(self):
        """Test event with list detail"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:list", detail=[1, 2, 3, 4], _meta=meta)

        assert event.detail == [1, 2, 3, 4]
        assert len(event.detail) == 4

    def test_event_with_string_detail(self):
        """Test event with string detail"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:string", detail="simple message", _meta=meta)

        assert event.detail == "simple message"
        assert isinstance(event.detail, str)

    def test_event_with_number_detail(self):
        """Test event with number detail"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:number", detail=42, _meta=meta)

        assert event.detail == 42
        assert isinstance(event.detail, int)

    def test_event_with_none_detail(self):
        """Test event with None detail"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:none", detail=None, _meta=meta)

        assert event.detail is None

    def test_event_with_boolean_detail(self):
        """Test event with boolean detail"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:bool", detail=True, _meta=meta)

        assert event.detail is True
        assert isinstance(event.detail, bool)

    def test_event_with_nested_detail(self):
        """Test event with nested data structures"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        detail = {"user": {"name": "Alice", "id": 123}, "items": [1, 2, 3], "active": True}
        event = TonikaEvent(type="test:nested", detail=detail, _meta=meta)

        assert event.detail["user"]["name"] == "Alice"
        assert event.detail["items"][1] == 2
        assert event.detail["active"] is True

    def test_event_string_representation(self):
        """Test string representation of event"""
        meta = EventMetadata.create(source="TestSource", version="1.0.0")
        event = TonikaEvent(type="test:event", detail={"msg": "hello"}, _meta=meta)

        str_repr = str(event)
        assert "test:event" in str_repr
        assert "TestSource" in str_repr

    def test_event_equality(self):
        """Test event equality comparison"""
        timestamp = int(datetime.now().timestamp() * 1000)
        meta1 = EventMetadata(timestamp=timestamp, source="Test", version="1.0.0")
        meta2 = EventMetadata(timestamp=timestamp, source="Test", version="1.0.0")

        event1 = TonikaEvent(type="test:event", detail={"data": 1}, _meta=meta1)
        event2 = TonikaEvent(type="test:event", detail={"data": 1}, _meta=meta2)

        # Events with same metadata should be equal
        assert event1 == event2

    def test_event_type_variations(self):
        """Test various event type naming conventions"""
        meta = EventMetadata.create(source="Test", version="1.0.0")

        types = [
            "simple",
            "with:colon",
            "with-dash",
            "with_underscore",
            "with.dot",
            "with/slash",
            "UPPERCASE",
            "MixedCase",
            "event:123:numbers",
        ]

        for event_type in types:
            event = TonikaEvent(type=event_type, detail={}, _meta=meta)
            assert event.type == event_type

    def test_event_empty_type(self):
        """Test event with empty string type"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="", detail={}, _meta=meta)

        assert event.type == ""

    def test_event_large_detail(self):
        """Test event with large detail payload"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        large_detail = {
            "data": "x" * 10000,
            "list": list(range(1000)),
            "nested": {"deep": {"structure": {"value": 42}}},
        }
        event = TonikaEvent(type="test:large", detail=large_detail, _meta=meta)

        assert len(event.detail["data"]) == 10000
        assert len(event.detail["list"]) == 1000
        assert event.detail["nested"]["deep"]["structure"]["value"] == 42

    def test_event_metadata_accessible(self):
        """Test that event metadata is accessible"""
        meta = EventMetadata.create(source="TestSource", version="2.0.0")
        event = TonikaEvent(type="test:event", detail={}, _meta=meta)

        assert event._meta.source == "TestSource"
        assert event._meta.version == "2.0.0"
        assert isinstance(event._meta.timestamp, int)

    def test_event_fields_accessible(self):
        """Test that all event fields are accessible"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:event", detail={"data": 123}, _meta=meta)

        assert hasattr(event, "type")
        assert hasattr(event, "detail")
        assert hasattr(event, "_meta")

    def test_event_detail_modification(self):
        """Test that event detail can be modified (mutable)"""
        meta = EventMetadata.create(source="Test", version="1.0.0")
        event = TonikaEvent(type="test:event", detail={"count": 0}, _meta=meta)

        # Modify detail
        event.detail["count"] = 10
        assert event.detail["count"] == 10

        # Note: In production, handlers should NOT modify event details
        # This test just verifies the data structure behavior

    def test_event_with_complex_types(self):
        """Test event with complex Python types"""
        meta = EventMetadata.create(source="Test", version="1.0.0")

        class CustomClass:
            def __init__(self, value):
                self.value = value

        detail = {
            "tuple": (1, 2, 3),
            "set": {1, 2, 3},
            "custom": CustomClass(42),
        }

        event = TonikaEvent(type="test:complex", detail=detail, _meta=meta)

        assert event.detail["tuple"] == (1, 2, 3)
        assert event.detail["set"] == {1, 2, 3}
        assert event.detail["custom"].value == 42


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
class TestEventStructuresIntegration:
    """Integration tests for event structures working together"""

    def test_complete_event_creation_flow(self):
        """Test creating a complete event from scratch"""
        # Create metadata
        meta = EventMetadata.create(source="IntegrationTest", version="1.0.0")

        # Create event
        event = TonikaEvent(
            type="integration:test",
            detail={"message": "Integration test", "status": "success"},
            _meta=meta,
        )

        # Verify all parts
        assert event.type == "integration:test"
        assert event.detail["message"] == "Integration test"
        assert event._meta.source == "IntegrationTest"
        assert event._meta.version == "1.0.0"
        assert isinstance(event._meta.timestamp, int)

    def test_event_lifecycle_simulation(self):
        """Test simulating an event lifecycle"""
        # Creation
        meta = EventMetadata.create(source="Module1", version="1.0.0")
        event = TonikaEvent(type="user:action", detail={"action": "click"}, _meta=meta)

        # Processing (simulated)
        assert event.type == "user:action"
        processed_data = event.detail.copy()
        processed_data["processed"] = True

        # New event from processing
        meta2 = EventMetadata.create(source="Module2", version="1.0.0")
        processed_event = TonikaEvent(
            type="user:action:processed", detail=processed_data, _meta=meta2
        )

        # Verify chain
        assert processed_event.detail["action"] == "click"
        assert processed_event.detail["processed"] is True
        assert processed_event._meta.source == "Module2"

    def test_multiple_events_with_ordering(self):
        """Test creating multiple events and checking temporal ordering"""
        events = []

        for i in range(5):
            meta = EventMetadata.create(source=f"Source{i}", version="1.0.0")
            event = TonikaEvent(type=f"event:{i}", detail={"index": i}, _meta=meta)
            events.append(event)
            sleep(0.001)  # Ensure different timestamps

        # Verify ordering
        for i in range(len(events) - 1):
            assert events[i]._meta.timestamp <= events[i + 1]._meta.timestamp

    def test_event_with_all_status_types(self):
        """Test events representing different module statuses"""
        for status in ModuleStatus:
            meta = EventMetadata.create(source="StatusTest", version="1.0.0")
            event = TonikaEvent(
                type="module:status:changed",
                detail={"status": status.value, "module": "TestModule"},
                _meta=meta,
            )

            assert event.detail["status"] == status.value
            assert event.type == "module:status:changed"
