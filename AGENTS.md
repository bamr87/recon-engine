<!-- kit: sdlc v0.2.0 · AGENTS.md is the CANONICAL agent instructions file (decision D4, UPS-AGENT-07/08).
     Keep these six `##` headings (UPS-AGENT-07 checks they exist, in any order; add your own headings as needed). CLAUDE.md is a pointer to this file and carries no rules of its own. -->

# recon-engine

Guidance for AI coding agents (Claude Code, Copilot, Cursor) working in recon-engine.

## What this repo is

The Recon Engine reconciles an operational event stream against a general ledger and decomposes the residual. [SPEC.md](SPEC.md) is the design of record: read it before changing anything, and change it (not just the code) when a design decision moves. Work follows the build order in SPEC.md section 6; done means the step's behaviour is implemented, tested, and described in README.md.

**Read [docs/constitution.md](docs/constitution.md) first.** It is the highest-precedence rule set here and wins over this file when they disagree.

## Stack & commands

Python 3.12, standard library only for the core package (`recon_engine/`). Adapters may declare their own dependencies, never the core.

```bash
python3 -m pip install -e .
python3 -m pytest
python3 tools/unwrap-prose.py --check    # markdown is one paragraph per line
```

## Layout

See [`SCHEMA.md`](SCHEMA.md). In brief: `SPEC.md` is the design of record, `recon_engine/` is the core package (a stub until build step 1 lands), `docs/` holds the constitution, the amendment log and the ADRs, `features/features.yml` is the feature catalog (ids `RECON-NNN`), `tools/` holds the vendored prose check, and `.github/` holds the CI callers, the issue forms and the SDLC profile. `tests/` arrives with build step 1.

## Conventions

- **Backlog of record:** GitHub Issues with the fleet labels. Pick up issues labelled `agent:ready`; never touch `agent:hold` or `human-review`.
- **Definition of Done:** the checklist in `.github/pull_request_template.md`. Every box is ticked before merge.
- **Decisions:** ADRs in `docs/adr/NNNN-slug.md`, indexed in `docs/adr/README.md`. Add one for anything hard to reverse; a design decision also changes SPEC.md in the same PR.
- **Commits:** Conventional Commits: `type(scope): description` (`feat`/`fix`/`docs`/`refactor`/`test`/`chore`/`ci`). The PR title is the squash subject.
- **Branches:** the default branch is `main` — branch from it (`feature/`, `fix/`, `docs/`, `refactor/`, `test/` or `chore/`) and open a PR; never push to it directly.
- **Changelog:** `CHANGELOG.md` is written by release-please from the PR titles. Never edit it, or a version number, by hand.
- README-First, README-Last: read the nearest `README.md` before changing a directory, and update it after.
- Files are placed per `SCHEMA.md`; a new directory gets its own `SCHEMA.md` and a row in its parent.
- Markdown is one paragraph per line.
- Don't suppress type errors or leave empty exception handlers.
- Two rules from the spec bind the code: residual buckets are gross, never net, and every inter-bucket transfer without an operational event flows into Unexplained.

## Fleet context

This repo is one of ~40 managed by the [bamr87/bamr87 dash](https://github.com/bamr87/bamr87) (registry: `_data/projects.yml`; tiered baseline: `docs/STANDARDS.md`; the Universal Project Standard: `specs/`). It is vendored there as a git submodule: commit and push changes **here** first — the hub only bumps its pointer afterwards. Shared CI, release, schema, and agent kits are seeded from the hub's `templates/`; prefer adopting those over hand-rolling equivalents. The repo's SDLC declaration is `.github/sdlc.yml`.

## Standard deviations

none

## Governance

Read [`docs/constitution.md`](docs/constitution.md) before changing anything. It changes only through a numbered record in [`docs/amendments/`](docs/amendments/), ratified by the maintainer merging the PR; agents propose, never merge. Every planned or shipped capability has a stable id in [`features/features.yml`](features/features.yml) with a `status` and the SPEC.md sections it serves; SPEC.md's "Feature catalog" block is generated from it (`python3 <bamr87/bamr87>/tools/governance_lint.py prd-sync . --write`; check with `… check .`). Never hand-edit that block or `CHANGELOG.md`.
