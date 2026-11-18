"""OperationalEvent and GLPosting: valid records construct; malformed ones raise ValueError naming the field."""

import dataclasses
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from recon_engine import EventType, GLPosting, JournalType, OperationalEvent

AT = datetime(2026, 10, 14, 9, 30, tzinfo=UTC)


def make_event(**overrides):
    fields = {
        "timestamp": AT,
        "event_type": EventType.PRODUCE,
        "item": "WIDGET-100",
        "quantity": Decimal("40"),
        "uom": "ea",
        "standard_cost_ref": "WIDGET-100",
        "source_document": "WO-1001",
    }
    return OperationalEvent(**(fields | overrides))


def make_posting(**overrides):
    fields = {
        "timestamp": AT,
        "account": "1400-finished-goods",
        "debit": Decimal("500.00"),
        "credit": Decimal("0"),
        "journal_type": JournalType.AUTOMATIC,
        "preparer": "erp-batch",
        "source_document": "WO-1001",
        "period": "2026-10",
    }
    return GLPosting(**(fields | overrides))


def test_valid_records_keep_their_values():
    # Arrange
    pacific = timezone(timedelta(hours=-8))

    # Act
    event = make_event(timestamp=datetime(2026, 10, 14, 1, 30, tzinfo=pacific), quantity=Decimal("0.125"))
    posting = make_posting(debit=Decimal("0"), credit=Decimal("12.34"))

    # Assert
    assert event.timestamp.utcoffset() == timedelta(hours=-8)
    assert event.quantity == Decimal("0.125")
    assert (posting.debit, posting.credit) == (Decimal("0"), Decimal("12.34"))
    assert posting.period == "2026-10"


def test_enum_fields_accept_their_string_values():
    # Arrange
    event_type, journal_type = "scrap", "manual"

    # Act
    event = make_event(event_type=event_type)
    posting = make_posting(journal_type=journal_type)

    # Assert
    assert event.event_type is EventType.SCRAP
    assert posting.journal_type is JournalType.MANUAL


def test_source_document_may_be_absent():
    # Arrange: SPEC.md § 5.1 lets the linkage key be absent (the engine then matches probabilistically).
    absent = None

    # Act
    event = make_event(source_document=absent)
    posting = make_posting(source_document=absent)

    # Assert
    assert event.source_document is None
    assert posting.source_document is None


@pytest.mark.parametrize(
    ("name", "value"),
    [
        pytest.param("quantity", Decimal("-1"), id="negative quantity"),
        pytest.param("quantity", 40.0, id="float quantity"),
        pytest.param("quantity", 40, id="int quantity"),
        pytest.param("quantity", Decimal("NaN"), id="NaN quantity"),
        pytest.param("quantity", Decimal("Infinity"), id="infinite quantity"),
        pytest.param("timestamp", datetime(2026, 10, 14, 9, 30), id="naive timestamp"),
        pytest.param("timestamp", "2026-10-14T09:30:00+00:00", id="string timestamp"),
        pytest.param("source_document", "", id="empty source_document"),
        pytest.param("source_document", "   ", id="blank source_document"),
        pytest.param("item", "", id="empty item"),
        pytest.param("uom", "", id="empty uom"),
        pytest.param("standard_cost_ref", " ", id="blank standard_cost_ref"),
        pytest.param("event_type", "transfer", id="unknown event_type"),
        pytest.param("event_type", None, id="missing event_type"),
    ],
)
def test_operational_event_rejects_a_malformed_field(name, value):
    # Arrange
    pattern = rf"^OperationalEvent\.{name}: "

    # Act / Assert
    with pytest.raises(ValueError, match=pattern):
        make_event(**{name: value})


@pytest.mark.parametrize(
    ("name", "value"),
    [
        pytest.param("debit", Decimal("-0.01"), id="negative debit"),
        pytest.param("credit", Decimal("-5"), id="negative credit"),
        pytest.param("debit", 500.0, id="float debit"),
        pytest.param("credit", "12.34", id="string credit"),
        pytest.param("timestamp", datetime(2026, 10, 14, 9, 30), id="naive timestamp"),
        pytest.param("account", "", id="empty account"),
        pytest.param("preparer", "", id="empty preparer"),
        pytest.param("source_document", "", id="empty source_document"),
        pytest.param("journal_type", "adjusting", id="unknown journal_type"),
        pytest.param("period", "2026-13", id="month 13"),
        pytest.param("period", "2026-1", id="one-digit month"),
        pytest.param("period", "2026-10-01", id="a date, not a period"),
        pytest.param("period", "２０２６-10", id="non-ASCII digits"),
        pytest.param("period", 202610, id="int period"),
    ],
)
def test_gl_posting_rejects_a_malformed_field(name, value):
    # Arrange
    pattern = rf"^GLPosting\.{name}: "

    # Act / Assert
    with pytest.raises(ValueError, match=pattern):
        make_posting(**{name: value})


def test_records_are_immutable():
    # Arrange
    event = make_event()
    posting = make_posting()

    # Act / Assert
    with pytest.raises(dataclasses.FrozenInstanceError):
        event.quantity = Decimal("41")
    with pytest.raises(dataclasses.FrozenInstanceError):
        posting.debit = Decimal("0")


def test_records_take_keyword_arguments_only():
    # Arrange: positional construction would let a debit and a credit swap places unnoticed.
    positional = (AT, "1400-finished-goods", Decimal("500.00"), Decimal("0"), "automatic", "erp-batch", None, "2026-10")

    # Act / Assert
    with pytest.raises(TypeError):
        GLPosting(*positional)
