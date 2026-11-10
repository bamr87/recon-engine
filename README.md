# recon-engine

> Reconciles a business's operational event stream against its general ledger the way debits reconcile against credits: one monthly residual, decomposed gross-not-net into six buckets, with a statistical layer that scores where interpretation has drifted from fact.

**Status:** specification stage. Nothing runs yet; the design is in [SPEC.md](SPEC.md) and the build order is its section 6.

## What it is

Every GL entry must trace to an operational event, and every operational event must have a GL footprint. Whatever violates that is the residual (`Residual = Finance − Operations`), and the engine's job is to assemble it honestly, decompose it (material, labor and machine, overhead absorption, timing, ghost, unexplained) and flag the signals of manipulation: Benford deviations, smoothed residuals, threshold clustering, close-period spikes, bucket migration, persistent timing items.

Three pieces are planned:

- A dependency-free **core library** (`recon_engine/`) that takes two event streams in a neutral schema and returns the decomposed residual and anomaly scores.
- **Adapters**: Django ERP first ([bamr87/djangoerp](https://github.com/bamr87/djangoerp)), then CSV/Parquet files, then scheduled API pulls.
- A **Django ERP module** that mounts the core inside the ERP: monthly recon run, period view, drill-down, anomaly queue.

## Layout

See [SCHEMA.md](SCHEMA.md). In brief: `SPEC.md` is the design of record, `recon_engine/` is the core package (stub until build step 1 lands), `tests/` arrives with it. `docs/` holds the constitution, the amendment log and the ADRs, and `features/features.yml` lists each step of the build order with its status.

## Documentation

Every document is indexed in [docs/README.md](docs/README.md). The rules every change must satisfy are in [docs/constitution.md](docs/constitution.md); to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Development

Python 3.12, standard library only for the core (adapters may add their own dependencies).

```bash
python3 -m pip install -e .
python3 -m pytest        # once tests exist
```

## Fleet context

One of the projects managed by the [bamr87/bamr87](https://github.com/bamr87/bamr87) hub, where it is vendored as a submodule under `projects/recon-engine`. Commit and push here first; the hub only bumps its pointer.

## License

[MIT](LICENSE)
