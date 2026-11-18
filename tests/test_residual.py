"""monthly_residual: one period's GL-implied value minus its operations-implied value (SPEC.md § 2)."""

import dataclasses
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from recon_engine import (
    EventType,
    GLPosting,
    JournalType,
    MissingDirectionError,
    MissingStandardCostError,
    OperationalEvent,
    Residual,
    monthly_residual,
)

PERIOD = "2026-10"
MID_OCTOBER = datetime(2026, 10, 14, 9, 30, tzinfo=UTC)
COSTS = {"WIDGET-100": Decimal("12.50")}
# The test scope: finished goods. Production adds value, shipments relieve it.
DIRECTIONS = {EventType.PRODUCE: 1, EventType.SHIP: -1}


def event(event_type, quantity, *, ref="WIDGET-100", at=MID_OCTOBER):
    return OperationalEvent(
        timestamp=at,
        event_type=event_type,
        item=ref,
        quantity=Decimal(quantity),
        uom="ea",
        standard_cost_ref=ref,
        source_document="WO-1001",
    )


def posting(*, debit="0", credit="0", period=PERIOD, at=MID_OCTOBER):
    return GLPosting(
        timestamp=at,
        account="1400-finished-goods",
        debit=Decimal(debit),
        credit=Decimal(credit),
        journal_type=JournalType.AUTOMATIC,
        preparer="erp-batch",
        source_document="WO-1001",
        period=period,
    )


def produce_40_ship_20():
    # 40 produced and 20 shipped at 12.50: operations-implied value 500.00 - 250.00.
    return [event(EventType.PRODUCE, "40"), event(EventType.SHIP, "20")]


def test_balanced_month_gives_zero():
    # Arrange
    postings = [posting(debit="500.00"), posting(credit="250.00")]

    # Act
    result = monthly_residual(postings, produce_40_ship_20(), COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert isinstance(result.residual, Decimal)
    assert result.residual == Decimal("0")


def test_gross_totals_are_reported_beside_the_residual():
    # Arrange
    postings = [posting(debit="500.00"), posting(credit="250.00")]

    # Act
    result = monthly_residual(postings, produce_40_ship_20(), COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert (result.gl_debits, result.gl_credits, result.gl_value) == (
        Decimal("500.00"),
        Decimal("250.00"),
        Decimal("250.00"),
    )
    assert dict(result.ops_by_event_type) == {EventType.PRODUCE: Decimal("500.00"), EventType.SHIP: Decimal("-250.00")}
    assert result.ops_value == Decimal("250.00")
    assert (result.period, result.gl_posting_count, result.ops_event_count) == (PERIOD, 2, 2)


def test_books_above_operations_give_a_positive_residual():
    # Arrange
    postings = [posting(debit="510.00"), posting(credit="250.00")]

    # Act
    result = monthly_residual(postings, produce_40_ship_20(), COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert result.residual == Decimal("10.00")


def test_books_below_operations_give_a_negative_residual():
    # Arrange
    postings = [posting(debit="480.00"), posting(credit="250.00")]

    # Act
    result = monthly_residual(postings, produce_40_ship_20(), COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert result.residual == Decimal("-20.00")


def test_missing_standard_cost_raises_a_named_error_listing_every_ref():
    # Arrange
    events = [
        event(EventType.PRODUCE, "1", ref="GADGET-7"),
        event(EventType.SHIP, "1", ref="BOLT-3"),
        *produce_40_ship_20(),
    ]

    # Act
    with pytest.raises(MissingStandardCostError) as raised:
        monthly_residual([], events, COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert isinstance(raised.value, LookupError)
    assert raised.value.refs == ("BOLT-3", "GADGET-7")
    assert str(raised.value) == "no standard cost for: BOLT-3, GADGET-7"


def test_missing_direction_raises_a_named_error():
    # Arrange
    events = [event(EventType.SCRAP, "2"), *produce_40_ship_20()]

    # Act
    with pytest.raises(MissingDirectionError) as raised:
        monthly_residual([], events, COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert isinstance(raised.value, LookupError)
    assert raised.value.event_types == (EventType.SCRAP,)
    assert str(raised.value) == "no direction for event type: scrap"


def test_decimal_sums_are_exact():
    # Arrange: ten 0.10 postings sum to 1.00 exactly, where float gives 0.9999999999999999.
    postings = [posting(debit="0.10") for _ in range(10)]

    # Act
    result = monthly_residual(postings, [], COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert str(result.gl_value) == "1.00"
    assert result.residual == Decimal("1.00")


def test_decimal_products_keep_every_digit():
    # Arrange: the product has 38 significant digits; the default decimal context would round it to 28.
    events = [event(EventType.PRODUCE, "1234567890.123456789", ref="FINE")]
    costs = {"FINE": Decimal("9876543210.987654321")}

    # Act
    result = monthly_residual([], events, costs, PERIOD, directions=DIRECTIONS)

    # Assert
    assert result.ops_value == Decimal("12193263113702179522.374638011112635269")
    assert result.residual == Decimal("-12193263113702179522.374638011112635269")


def test_records_outside_the_period_are_not_counted():
    # Arrange
    september = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)
    postings = [posting(debit="500.00"), posting(debit="999.00", period="2026-09")]
    events = [event(EventType.PRODUCE, "40"), event(EventType.PRODUCE, "7", at=september)]

    # Act
    result = monthly_residual(postings, events, COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert (result.gl_posting_count, result.ops_event_count) == (1, 1)
    assert result.residual == Decimal("0")


def test_a_posting_counts_in_its_ledger_period_not_its_timestamp_month():
    # Arrange: an October close adjustment posted on 2 November.
    late = posting(debit="500.00", period=PERIOD, at=datetime(2026, 11, 2, 10, 0, tzinfo=UTC))

    # Act
    result = monthly_residual([late], [event(EventType.PRODUCE, "40")], COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert result.gl_posting_count == 1
    assert result.residual == Decimal("0")


def test_an_event_counts_in_the_month_of_its_timestamp_read_in_tz():
    # Arrange: 03:00 UTC on 1 November is still 31 October at UTC-8.
    night_shift = [event(EventType.PRODUCE, "40", at=datetime(2026, 11, 1, 3, 0, tzinfo=UTC))]
    pacific = timezone(timedelta(hours=-8))

    # Act
    in_utc = monthly_residual([], night_shift, COSTS, PERIOD, directions=DIRECTIONS)
    in_pacific = monthly_residual([], night_shift, COSTS, PERIOD, directions=DIRECTIONS, tz=pacific)

    # Assert
    assert in_utc.ops_event_count == 0
    assert in_pacific.ops_event_count == 1
    assert in_pacific.ops_value == Decimal("500.00")


def test_an_empty_month_gives_zero_with_zero_counts():
    # Arrange
    postings, events = [], []

    # Act
    result = monthly_residual(postings, events, COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert result.residual == Decimal("0")
    assert (result.gl_posting_count, result.ops_event_count) == (0, 0)
    assert dict(result.ops_by_event_type) == {}


def test_streams_may_be_any_iterable():
    # Arrange
    postings = (posting(debit=amount) for amount in ("500.00", "0"))
    events = iter(produce_40_ship_20())

    # Act
    result = monthly_residual(postings, events, COSTS, PERIOD, directions=DIRECTIONS)

    # Assert
    assert (result.gl_posting_count, result.ops_event_count) == (2, 2)
    assert result.residual == Decimal("250.00")


def test_directions_accept_event_type_strings():
    # Arrange
    postings = [posting(debit="500.00"), posting(credit="250.00")]

    # Act
    result = monthly_residual(postings, produce_40_ship_20(), COSTS, PERIOD, directions={"produce": 1, "ship": -1})

    # Assert
    assert result.residual == Decimal("0")


@pytest.mark.parametrize(
    "directions",
    [
        pytest.param({EventType.PRODUCE: 0, EventType.SHIP: -1}, id="zero"),
        pytest.param({EventType.PRODUCE: 2, EventType.SHIP: -1}, id="two"),
        pytest.param({EventType.PRODUCE: True, EventType.SHIP: -1}, id="bool"),
        pytest.param({EventType.PRODUCE: Decimal(1), EventType.SHIP: -1}, id="Decimal"),
        pytest.param({"transfer": 1}, id="unknown event type"),
    ],
)
def test_malformed_directions_raise_value_error(directions):
    # Arrange
    events = produce_40_ship_20()

    # Act / Assert
    with pytest.raises(ValueError, match=r"^directions"):
        monthly_residual([], events, COSTS, PERIOD, directions=directions)


@pytest.mark.parametrize(
    "cost",
    [
        pytest.param(12.5, id="float"),
        pytest.param(Decimal("-12.50"), id="negative"),
        pytest.param(Decimal("NaN"), id="NaN"),
    ],
)
def test_a_malformed_standard_cost_raises_value_error(cost):
    # Arrange
    costs = {"WIDGET-100": cost}

    # Act / Assert
    with pytest.raises(ValueError, match=r"^standard_costs\['WIDGET-100'\]: "):
        monthly_residual([], produce_40_ship_20(), costs, PERIOD, directions=DIRECTIONS)


@pytest.mark.parametrize("period", ["2026-10-01", "Oct 2026", "2026-00"])
def test_a_malformed_period_raises_value_error(period):
    # Arrange
    events = produce_40_ship_20()

    # Act / Assert
    with pytest.raises(ValueError, match=r"^period: "):
        monthly_residual([], events, COSTS, period, directions=DIRECTIONS)


def test_records_must_be_schema_instances():
    # Arrange
    raw_posting = {"account": "1400-finished-goods", "debit": Decimal("500.00")}
    raw_event = {"event_type": "produce", "quantity": Decimal("40")}

    # Act / Assert
    with pytest.raises(TypeError, match=r"^postings: "):
        monthly_residual([raw_posting], [], COSTS, PERIOD, directions=DIRECTIONS)
    with pytest.raises(TypeError, match=r"^events: "):
        monthly_residual([], [raw_event], COSTS, PERIOD, directions=DIRECTIONS)


def test_tz_none_is_refused_rather_than_read_as_local_time():
    # Arrange
    events = produce_40_ship_20()

    # Act / Assert
    with pytest.raises(TypeError, match=r"^tz: "):
        monthly_residual([], events, COSTS, PERIOD, directions=DIRECTIONS, tz=None)


def test_residual_is_immutable():
    # Arrange
    result = monthly_residual([posting(debit="500.00")], produce_40_ship_20(), COSTS, PERIOD, directions=DIRECTIONS)

    # Act / Assert
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.residual = Decimal("0")
    with pytest.raises(TypeError):
        result.ops_by_event_type[EventType.SCRAP] = Decimal("0")


def test_residual_derives_its_totals_from_the_gross_parts():
    # Arrange
    parts = {
        "period": PERIOD,
        "gl_debits": Decimal("7.00"),
        "gl_credits": Decimal("2.00"),
        "ops_by_event_type": {EventType.PRODUCE: Decimal("4.00"), EventType.SHIP: Decimal("-1.50")},
        "gl_posting_count": 2,
        "ops_event_count": 2,
    }

    # Act
    result = Residual(**parts)

    # Assert
    assert (result.gl_value, result.ops_value, result.residual) == (Decimal("5.00"), Decimal("2.50"), Decimal("2.50"))
