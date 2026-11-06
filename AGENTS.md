# recon-engine

Guidance for AI coding agents (Claude Code, Copilot, Cursor) working in recon-engine.

The Recon Engine reconciles an operational event stream against a general ledger and decomposes the residual. [SPEC.md](SPEC.md) is the design of record: read it before changing anything, and change it (not just the code) when a design decision moves. Work follows the build order in SPEC.md section 6; done means the step's behaviour is implemented, tested, and described in README.md.

## Stack & commands

Python 3.12, standard library only for the core package (`recon_engine/`). Adapters may declare their own dependencies, never the core.

```bash
python3 -m pip install -e .
python3 -m pytest
```

## Conventions

- Conventional Commits: `type(scope): description` (`feat`/`fix`/`docs`/`refactor`/`test`/`chore`/`ci`).
- Default branch is `main` — branch from it and open a PR; never push to it directly.
- README-First, README-Last: read the nearest `README.md` before changing a directory, and update it after.
- Files are placed per `SCHEMA.md`; a new directory gets its own `SCHEMA.md` and a row in its parent.
- Markdown is one paragraph per line.
- Don't suppress type errors or leave empty exception handlers.
- Two rules from the spec bind the code: residual buckets are gross, never net, and every inter-bucket transfer without an operational event flows into Unexplained.

## Fleet context

This repo is one of ~40 managed by the [bamr87/bamr87 dash](https://github.com/bamr87/bamr87) (registry: `_data/projects.yml`; tiered baseline: `docs/STANDARDS.md`). It is vendored there as a git submodule: commit and push changes **here** first — the hub only bumps its pointer afterwards. Shared CI, release, schema, and agent kits are seeded from the hub's `templates/`; prefer adopting those over hand-rolling equivalents.
