# The Recon Engine — Specification

> Two histories of one business, reconciled like debits and credits: the operational event stream against the general ledger, with the residual decomposed, scored and kept visible.

## 1. Premise

A manufacturing or technology business has two histories of itself. The operational history is a stream of physical facts: material issued, hours run, units produced, scrap recorded, goods shipped. The financial history is the general ledger: a stream of interpretations of those facts in money.

The Recon Engine treats these as mirror ledgers that must reconcile the way debits and credits do. The guiding analogy is the accounting equation:

```text
Equity = Assets + Liabilities   →   Residual = Finance − Operations
```

- Operations plays the role of the factual side (assets and liabilities as they physically exist).
- Finance plays the role of the interpreted side (what the books claim).
- Equity, the residual, is what falls out when the two are fully reconciled. It can be positive (operational value the books have not recognized — unbilled output, process gains, know-how) or negative (financial claims operations cannot back — unfulfillable orders, phantom capacity, hidden losses).

The strong form of the principle: every GL entry must trace to an operational event, and every operational event must have a GL footprint. Anything that violates this is, by definition, the residual.

## 2. The single monthly number

Start with one figure per period.

1. **GL-implied production value** — the net of all postings for the month touching inventory, WIP, COGS, absorbed overhead, and revenue.
2. **Operations-implied production value** — what the floor actually consumed, produced, and shipped, priced at standard cost.
3. **Monthly residual** = (1) − (2).

Much of this already exists in fragments as variance accounts. The Recon Engine's first job is simply to assemble those fragments into one honest number before anyone nets them away.

## 3. Decomposition for a manufacturing environment

The residual is decomposed into six buckets. Two rules apply to all of them:

- **Gross, never net.** Offsetting items may not cancel each other inside or across buckets.
- **Transfers are events.** Any reclassification between buckets that has no matching operational event is recorded as a flow into the Unexplained bucket.

### 3.1 Material

- Purchase price variance (paid vs. standard)
- Usage variance (consumed vs. bill-of-materials)

### 3.2 Labor and machine

- Rate variance (paid vs. standard rate)
- Efficiency variance (hours booked vs. hours absorbed)

### 3.3 Overhead absorption

- Assumed capacity vs. actual capacity run
- Flagged as the most common dumping ground: a favorable absorption variance can quietly swallow an unfavorable yield loss.

### 3.4 Timing and cut-off

- Goods received not invoiced
- Shipped not billed
- WIP straddling period end
- Expected to self-correct in the following period; persistence is itself a signal.

### 3.5 Ghost bucket

- Scrap, rework, yield loss, cycle-count adjustments
- Physical reality changed and nothing — or the wrong thing — was posted.
- This is the candidate "equity" of the system, but a small ghost bucket is not proof of honesty; it may mean someone found another bucket to hide things in.

### 3.6 Unexplained

- Receives every inter-bucket transfer lacking an operational event.
- Receives anything the statistical layer cannot attribute.
- This turns manipulation into a visible flow rather than a disappearance.

## 4. The statistical layer

The engine is a model wedged between operational transactional facts and financial, subjective results. It has three layers.

### 4.1 Learned expectation

Given the month's operational events, predict what each GL account should look like. Start simple: one regression per account on operational drivers (units, hours, material quantities, shipments), trained on prior periods. Graduate to a small factor model once enough history exists.

### 4.2 Standardized residuals

For each account: actual posting minus expected, divided by the account's historical dispersion. A $10,000 miss in overhead and a $10,000 miss in freight must not look alike.

### 4.3 Anomaly detection on residuals

Signals that indicate interpretation drifting from fact:

- **Benford's law** on posted amounts, by account and by preparer.
- **Autocorrelation** of residuals suggesting smoothing across periods.
- **Threshold clustering** — amounts bunching just under approval limits.
- **Close-period behavior** — spikes in manual, late, or reversing journals near period end.
- **Bucket migration** — recurring reclassifications out of Ghost into Overhead or Timing.
- **Persistence** — timing items that fail to self-correct.

### 4.4 Output

The monthly residual, decomposed into:

1. **Explained** — attributable to standard-costing variances with operational backing.
2. **Normal noise** — within the learned dispersion.
3. **Anomaly score** — the manipulation signal, with the contributing accounts, periods, and preparers.

## 5. Architecture

### 5.1 Core library (standalone)

A dependency-free core that accepts two event streams in a neutral schema and returns the decomposed residual and anomaly scores.

- **Operational event schema:** timestamp, event type (issue, produce, scrap, ship, count, hour), item or resource, quantity, unit of measure, standard cost reference, source document.
- **GL posting schema:** timestamp, account, debit, credit, journal type (automatic, manual, reversing), preparer, source document, period.
- **Linkage:** a source-document key that both sides can carry; where absent, the engine attempts probabilistic matching and records the match confidence.

### 5.2 Adapters

- **Django ERP adapter (first)** — reads directly from the ERP's inventory, production, and journal models and feeds the core ([bamr87/djangoerp](https://github.com/bamr87/djangoerp)).
- **File adapter** — CSV or Parquet exports from any ERP.
- **API adapter** — pulls from external ERPs on a schedule.

### 5.3 Django ERP module

The same core mounted inside the ERP as an app: a monthly recon run, a decomposition view per period, drill-down from bucket to postings to operational events, and an anomaly queue for review.

## 6. Build order

1. Neutral schemas and the single monthly number.
2. Deterministic decomposition into the six buckets, gross-not-net, with transfer logging.
3. Django ERP adapter and a minimal period view.
4. Learned-expectation layer with per-account regressions.
5. Anomaly detection on standardized residuals.
6. File and API adapters for standalone use.

## Feature catalog

<!-- features:start v1 · generated by bamr87/bamr87 tools/governance_lint.py prd-sync from features/features.yml — edit the catalog, then re-run; do not edit this table by hand -->
Every user-facing capability has a stable id in the feature catalog [`features/features.yml`](features/features.yml). Each entry names the PRD requirements it serves (`prd:`); the trace below is the reverse view.

| ID | Feature | Status | Where | Requirements |
| --- | --- | --- | --- | --- |
| [RECON-001](features/features.yml) | Neutral schemas and the single monthly number | planned | [`SPEC.md`](SPEC.md) | §2, §5.1 |
| [RECON-002](features/features.yml) | Six-bucket decomposition, gross not net, with transfer logging | planned | [`SPEC.md`](SPEC.md) | §3 |
| [RECON-003](features/features.yml) | Django ERP adapter and a minimal period view | planned | [`SPEC.md`](SPEC.md) | §5.2, §5.3 |
| [RECON-004](features/features.yml) | Learned expectation: one regression per GL account | planned | [`SPEC.md`](SPEC.md) | §4.1 |
| [RECON-005](features/features.yml) | Anomaly detection on standardized residuals | planned | [`SPEC.md`](SPEC.md) | §4.2, §4.3, §4.4 |
| [RECON-006](features/features.yml) | File and API adapters for standalone use | planned | [`SPEC.md`](SPEC.md) | §5.2 |

**Requirement → feature trace**

| Requirement | Features |
| --- | --- |
| §2 | RECON-001 |
| §5.1 | RECON-001 |
| §3 | RECON-002 |
| §5.2 | RECON-003, RECON-006 |
| §5.3 | RECON-003 |
| §4.1 | RECON-004 |
| §4.2 | RECON-005 |
| §4.3 | RECON-005 |
| §4.4 | RECON-005 |
<!-- features:end -->

## 7. Open questions

- How to price operational events when standards are stale or missing.
- How much history is needed before the learned-expectation layer is trustworthy.
- Whether the anomaly score should be a single scalar or a vector per detection method.
- Governance: who may reclassify between buckets, and whether the engine should be able to block a close.
