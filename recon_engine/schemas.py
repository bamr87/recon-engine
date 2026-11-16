"""The neutral schemas for the two streams the engine reconciles (SPEC.md § 5.1).

`OperationalEvent` is one physical fact from the floor; `GLPosting` is one line of
the general ledger. Both are immutable and validate on construction: a malformed
record raises `ValueError` naming the offending field, so nothing malformed reaches
the residual. Money and quantities are `Decimal`, never float, and every timestamp
is timezone-aware.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

__all__ = ["EventType", "GLPosting", "JournalType", "OperationalEvent"]

# An accounting period is a calendar month, written YYYY-MM ([0-9], not \d: \d also matches non-ASCII digits).
_PERIOD = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])")


class EventType(StrEnum):
    """What happened on the floor (SPEC.md § 5.1)."""

    ISSUE = "issue"
    PRODUCE = "produce"
    SCRAP = "scrap"
    SHIP = "ship"
    COUNT = "count"
    HOUR = "hour"


class JournalType(StrEnum):
    """How a GL line was posted (SPEC.md § 5.1); manual and reversing journals feed the close-period signal (§ 4.3)."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    REVERSING = "reversing"


def _is_period(value: object) -> bool:
    """True when `value` is an accounting period string, `YYYY-MM`."""
    return isinstance(value, str) and _PERIOD.fullmatch(value) is not None


def _invalid(record: object, name: str, problem: str) -> ValueError:
    return ValueError(f"{type(record).__name__}.{name}: {problem}")


def _check_timestamp(record: object, name: str, value: object) -> None:
    if not isinstance(value, datetime):
        raise _invalid(record, name, f"must be a datetime, got {type(value).__name__}")
    if value.tzinfo is None or value.utcoffset() is None:
        raise _invalid(record, name, "must be timezone-aware; a naive datetime has no defined period")


def _check_amount(record: object, name: str, value: object) -> None:
    if not isinstance(value, Decimal):
        raise _invalid(record, name, f"must be a Decimal, got {type(value).__name__} (float cannot hold cents exactly)")
    if not value.is_finite():
        raise _invalid(record, name, f"must be a finite Decimal, got {value}")
    if value < 0:
        raise _invalid(record, name, f"must be non-negative, got {value}")


def _check_text(record: object, name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise _invalid(record, name, f"must be a non-empty string, got {value!r}")


def _check_source_document(record: object, name: str, value: object) -> None:
    # None is allowed: SPEC.md § 5.1 lets the key be absent (the engine then matches probabilistically).
    # A key that is present must name a document, so '' and whitespace are rejected.
    if value is not None:
        _check_text(record, name, value)


def _coerce_enum(record: object, name: str, value: object, enum: type[StrEnum]) -> None:
    if isinstance(value, enum):
        return
    try:
        member = enum(value)
    except ValueError:
        allowed = ", ".join(option.value for option in enum)
        raise _invalid(record, name, f"{value!r} is not one of: {allowed}") from None
    object.__setattr__(record, name, member)


@dataclass(frozen=True, kw_only=True, slots=True)
class OperationalEvent:
    """One physical fact: material issued, units produced, scrap, a shipment, a count or hours run.

    `quantity` is in `uom` and is priced at the standard cost that `standard_cost_ref` names.
    `event_type` accepts an `EventType` or its string value. `source_document` may be None
    when the source carries no key, but never empty.
    """

    timestamp: datetime
    event_type: EventType
    item: str
    quantity: Decimal
    uom: str
    standard_cost_ref: str
    source_document: str | None

    def __post_init__(self) -> None:
        _check_timestamp(self, "timestamp", self.timestamp)
        _coerce_enum(self, "event_type", self.event_type, EventType)
        _check_text(self, "item", self.item)
        _check_amount(self, "quantity", self.quantity)
        _check_text(self, "uom", self.uom)
        _check_text(self, "standard_cost_ref", self.standard_cost_ref)
        _check_source_document(self, "source_document", self.source_document)


@dataclass(frozen=True, kw_only=True, slots=True)
class GLPosting:
    """One general-ledger line: a debit or a credit to one account, in one accounting period.

    `period` (YYYY-MM) is the ledger's own period assignment, which may differ from the month
    of `timestamp` for close adjustments. `journal_type` accepts a `JournalType` or its string
    value. `source_document` may be None when the source carries no key, but never empty.
    """

    timestamp: datetime
    account: str
    debit: Decimal
    credit: Decimal
    journal_type: JournalType
    preparer: str
    source_document: str | None
    period: str

    def __post_init__(self) -> None:
        _check_timestamp(self, "timestamp", self.timestamp)
        _check_text(self, "account", self.account)
        _check_amount(self, "debit", self.debit)
        _check_amount(self, "credit", self.credit)
        _coerce_enum(self, "journal_type", self.journal_type, JournalType)
        _check_text(self, "preparer", self.preparer)
        _check_source_document(self, "source_document", self.source_document)
        if not _is_period(self.period):
            raise _invalid(self, "period", f"must be a YYYY-MM string, got {self.period!r}")
