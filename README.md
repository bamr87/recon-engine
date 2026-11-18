# recon-engine

> The Recon Engine's direction is to become the ultimate open home for all things operational-to-ledger reconciliation: data, tools, resources and transparency, with one honest monthly residual, gross-not-net buckets, and an inspectable core, for everyone ([constitution](docs/constitution.md) §1).

**Status:** build step 1 implemented (the neutral schemas and the single monthly number, see [Quick start](#quick-start)); step 2, the six-bucket decomposition, is next. The design is in [SPEC.md](SPEC.md) and the build order is its section 6.

## What it is

Every GL entry must trace to an operational event, and every operational event must have a GL footprint. Whatever violates that is the residual (`Residual = Finance − Operations`), and the engine's job is to assemble it honestly, decompose it (material, labor and machine, overhead absorption, timing, ghost, unexplained) and flag the signals of manipulation: Benford deviations, smoothed residuals, threshold clustering, close-period spikes, bucket migration, persistent timing items.

Three pieces are planned:

- A dependency-free **core library** (`recon_engine/`) that takes two event streams in a neutral schema and returns the decomposed residual and anomaly scores.
- **Adapters**: Django ERP first ([bamr87/djangoerp](https://github.com/bamr87/djangoerp)), then CSV/Parquet files, then scheduled API pulls.
- A **Django ERP module** that mounts the core inside the ERP: monthly recon run, period view, drill-down, anomaly queue.

## Quick start

```bash
python3 -m pip install -e .
```

The core imports only the standard library, so that is the whole install. Build step 1 takes the two streams in the neutral schemas and returns one period's single number, GL-implied value minus operations-implied value ([SPEC.md § 2](SPEC.md#2-the-single-monthly-number)):

```python
from datetime import UTC, datetime
from decimal import Decimal

from recon_engine import EventType, GLPosting, JournalType, OperationalEvent, monthly_residual

events = [
    OperationalEvent(
        timestamp=datetime(2026, 10, 14, 9, 30, tzinfo=UTC),
        event_type=EventType.PRODUCE,
        item="WIDGET-100",
        quantity=Decimal("40"),
        uom="ea",
        standard_cost_ref="WIDGET-100",
        source_document="WO-1001",
    ),
]
postings = [
    GLPosting(
        timestamp=datetime(2026, 10, 14, 17, 0, tzinfo=UTC),
        account="1400-finished-goods",
        debit=Decimal("510.00"),
        credit=Decimal("0"),
        journal_type=JournalType.AUTOMATIC,
        preparer="erp-batch",
        source_document="WO-1001",
        period="2026-10",
    ),
]

result = monthly_residual(
    postings,
    events,
    standard_costs={"WIDGET-100": Decimal("12.50")},
    period="2026-10",
    directions={EventType.PRODUCE: 1},
)
print(result.gl_value, result.ops_value, result.residual)
```

It prints the GL-implied value, the operations-implied value (40 units at a standard 12.50) and the residual:

```text
510.00 500.00 10.00
```

The conventions SPEC.md leaves to the business are arguments, never defaults: the postings you pass are the GL scope (the accounts that carry production value), `directions` gives each event type in the period its sign (+1 or -1), and an event belongs to the month of its timestamp in `tz` (UTC unless you pass the ledger's zone; a posting belongs to its own `period`). Money is `Decimal` throughout and the arithmetic never rounds. An event with no standard cost or no direction raises `MissingStandardCostError` or `MissingDirectionError` instead of being priced at zero, and the `Residual` keeps the gross parts beside the single number: GL debits and credits, and the operations value of each event type.

The rest of the core's output in [SPEC.md § 5.1](SPEC.md#51-core-library-standalone), the six-bucket decomposition and the anomaly scores, is planned as build steps 2, 4 and 5 ([SPEC.md § 6](SPEC.md#6-build-order)).

## Layout

See [SCHEMA.md](SCHEMA.md). In brief: `SPEC.md` is the design of record, `recon_engine/` is the core package (build step 1: `schemas.py` and `residual.py`), and `tests/` is its pytest suite. `docs/` holds the constitution, the amendment log and the ADRs, and `features/features.yml` lists each step of the build order with its status.

## Documentation

Every document is indexed in [docs/README.md](docs/README.md). The rules every change must satisfy are in [docs/constitution.md](docs/constitution.md); to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Development

Python 3.12, standard library only for the core (adapters may add their own dependencies). The `dev` extra adds the tools: pytest, pytest-cov and ruff.

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest                          # coverage: python3 -m pytest --cov=recon_engine
ruff check . && ruff format --check .
```

## Contributing

Read [SPEC.md](SPEC.md) before changing anything: it is the design of record, and a change to a design decision changes SPEC.md in the same pull request. Build steps land in the order of its section 6, each with its tests and this README brought up to date; [AGENTS.md](AGENTS.md) lists the commands and conventions. Two rules of [SPEC.md § 3](SPEC.md#3-decomposition-for-a-manufacturing-environment) bind every change to the code:

- **Gross, never net.** Offsetting items never cancel each other, inside a bucket or across buckets: both sides are kept and reported.
- **Transfers are events.** A reclassification between buckets with no matching operational event is recorded as a flow into the Unexplained bucket, never dropped.

## Fleet context

One of the projects managed by the [bamr87/bamr87](https://github.com/bamr87/bamr87) hub, where it is vendored as a submodule under `projects/recon-engine`. Commit and push here first; the hub only bumps its pointer.

## License

[MIT](LICENSE)
