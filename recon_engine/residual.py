"""The single monthly number (SPEC.md § 2, build step 1).

    residual = GL-implied value - operations-implied value

for one accounting period. Both sides stay gross: the result carries the GL debits and
credits and the operations value of each event type, so nothing is netted away before the
decomposition of SPEC.md § 3 (build step 2).

SPEC.md § 2 leaves three conventions to the business, so the caller states them and none
is assumed here:

- GL scope: which accounts carry production value (inventory, WIP, COGS, absorbed overhead,
  revenue) is a chart-of-accounts decision. Pass only those postings.
- Directions: each event type that occurs in the period enters the operations side with the
  sign the caller gives it in `directions` (+1 or -1). A type without one stops the run.
- Period boundary: a posting belongs to the period the ledger assigned it (`GLPosting.period`);
  an event belongs to the calendar month of its timestamp read in `tz` (UTC by default).

Arithmetic is exact: Decimal only, in a context that raises instead of rounding.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, tzinfo
from decimal import (
    MAX_EMAX,
    MAX_PREC,
    MIN_EMIN,
    Context,
    Decimal,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    localcontext,
)
from types import MappingProxyType

from .schemas import EventType, GLPosting, OperationalEvent, _is_period

__all__ = ["MissingDirectionError", "MissingStandardCostError", "Residual", "monthly_residual"]

# Unlimited precision with every rounding signal trapped (the decimal docs' recipe for exact
# arithmetic): a sum or product that could not be held exactly raises instead of being rounded.
_EXACT = Context(
    prec=MAX_PREC,
    Emax=MAX_EMAX,
    Emin=MIN_EMIN,
    traps=[InvalidOperation, DivisionByZero, Overflow, Inexact, Rounded],
)
_ZERO = Decimal(0)


class MissingStandardCostError(LookupError):
    """Events in the period name standard costs the caller did not supply; `refs` lists every one.

    Pricing them at zero would bury SPEC.md § 7's first open question (how to price events
    when standards are stale or missing), so the run stops instead.
    """

    def __init__(self, refs: Iterable[str]) -> None:
        self.refs = tuple(sorted(set(refs)))
        super().__init__(self.refs)

    def __str__(self) -> str:
        return "no standard cost for: " + ", ".join(self.refs)


class MissingDirectionError(LookupError):
    """Events in the period have a type with no sign in `directions`; `event_types` lists every one."""

    def __init__(self, event_types: Iterable[EventType]) -> None:
        found = set(event_types)
        self.event_types = tuple(event_type for event_type in EventType if event_type in found)
        super().__init__(self.event_types)

    def __str__(self) -> str:
        return "no direction for event type: " + ", ".join(self.event_types)


@dataclass(frozen=True, kw_only=True, slots=True)
class Residual:
    """One period's single number and the gross totals it came from.

    `gl_value` is `gl_debits` - `gl_credits`; `ops_value` is the sum of `ops_by_event_type`
    (each type's quantity x standard cost, signed by its direction); `residual` is
    `gl_value` - `ops_value`. Those three are derived on construction, never passed in.
    """

    period: str
    gl_debits: Decimal
    gl_credits: Decimal
    ops_by_event_type: Mapping[EventType, Decimal] = field(hash=False)
    gl_posting_count: int
    ops_event_count: int
    gl_value: Decimal = field(init=False)
    ops_value: Decimal = field(init=False)
    residual: Decimal = field(init=False)

    def __post_init__(self) -> None:
        by_type = MappingProxyType(dict(self.ops_by_event_type))
        with localcontext(_EXACT):
            gl_value = self.gl_debits - self.gl_credits
            ops_value = sum(by_type.values(), _ZERO)
            residual = gl_value - ops_value
        object.__setattr__(self, "ops_by_event_type", by_type)
        object.__setattr__(self, "gl_value", gl_value)
        object.__setattr__(self, "ops_value", ops_value)
        object.__setattr__(self, "residual", residual)


def monthly_residual(
    postings: Iterable[GLPosting],
    events: Iterable[OperationalEvent],
    standard_costs: Mapping[str, Decimal],
    period: str,
    *,
    directions: Mapping[EventType | str, int],
    tz: tzinfo = UTC,
) -> Residual:
    """Assemble `period`'s residual: GL-implied value minus operations-implied value (SPEC.md § 2).

    postings: the GL lines in scope (see the module docstring); lines of other periods are not counted.
    events: the operational events; those whose timestamp, read in `tz`, falls in another month are not counted.
    standard_costs: the standard cost per unit for each `standard_cost_ref`, a non-negative Decimal in the
        event's unit of measure (units are not converted).
    period: the accounting period, YYYY-MM.
    directions: +1 or -1 for each event type, the sign its value carries on the operations side.
    tz: the zone whose calendar months are the periods of event timestamps.

    Raises MissingDirectionError or MissingStandardCostError, naming every gap, rather than pricing an
    event at zero; ValueError for a malformed period, direction or standard cost; TypeError for a record
    that is not a GLPosting or an OperationalEvent, or a `tz` that is not a tzinfo.
    """
    if not _is_period(period):
        raise ValueError(f"period: must be a YYYY-MM string, got {period!r}")
    if not isinstance(tz, tzinfo):
        raise TypeError(f"tz: must be a tzinfo, got {type(tz).__name__}")
    signs = _signs(directions)

    in_period_postings: list[GLPosting] = []
    for posting in postings:
        if not isinstance(posting, GLPosting):
            raise TypeError(f"postings: expected GLPosting, got {type(posting).__name__}")
        if posting.period == period:
            in_period_postings.append(posting)

    in_period_events: list[OperationalEvent] = []
    for event in events:
        if not isinstance(event, OperationalEvent):
            raise TypeError(f"events: expected OperationalEvent, got {type(event).__name__}")
        if _period_of(event.timestamp, tz) == period:
            in_period_events.append(event)

    unsigned = {event.event_type for event in in_period_events} - signs.keys()
    if unsigned:
        raise MissingDirectionError(unsigned)
    refs = {event.standard_cost_ref for event in in_period_events}
    unpriced = refs - standard_costs.keys()
    if unpriced:
        raise MissingStandardCostError(unpriced)
    costs = {ref: _cost(standard_costs, ref) for ref in refs}

    with localcontext(_EXACT):
        gl_debits = sum((posting.debit for posting in in_period_postings), _ZERO)
        gl_credits = sum((posting.credit for posting in in_period_postings), _ZERO)
        by_type: dict[EventType, Decimal] = {}
        for event in in_period_events:
            value = signs[event.event_type] * event.quantity * costs[event.standard_cost_ref]
            by_type[event.event_type] = by_type.get(event.event_type, _ZERO) + value

    return Residual(
        period=period,
        gl_debits=gl_debits,
        gl_credits=gl_credits,
        ops_by_event_type={event_type: by_type[event_type] for event_type in EventType if event_type in by_type},
        gl_posting_count=len(in_period_postings),
        ops_event_count=len(in_period_events),
    )


def _period_of(timestamp: datetime, tz: tzinfo) -> str:
    local = timestamp.astimezone(tz)
    return f"{local.year:04d}-{local.month:02d}"


def _signs(directions: Mapping[EventType | str, int]) -> dict[EventType, Decimal]:
    signs: dict[EventType, Decimal] = {}
    for key, sign in directions.items():
        try:
            event_type = EventType(key)
        except ValueError:
            raise ValueError(f"directions: {key!r} is not an event type") from None
        if type(sign) is not int or sign not in (1, -1):
            raise ValueError(f"directions[{event_type.value!r}]: must be the int +1 or -1, got {sign!r}")
        signs[event_type] = Decimal(sign)
    return signs


def _cost(standard_costs: Mapping[str, Decimal], ref: str) -> Decimal:
    cost = standard_costs[ref]
    if not isinstance(cost, Decimal):
        raise ValueError(f"standard_costs[{ref!r}]: must be a Decimal, got {type(cost).__name__}")
    if not cost.is_finite() or cost < 0:
        raise ValueError(f"standard_costs[{ref!r}]: must be a finite, non-negative Decimal, got {cost}")
    return cost
