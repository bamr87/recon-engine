<!-- kit: governance v0.1.1 · seeded from bamr87/bamr87 templates/governance/. Owned by this repo after seeding;
     change it ONLY through an amendment record in docs/amendments/ (see § 8). Validate: python3 <hub>/tools/governance_lint.py check . -->
# recon-engine — Constitution

> The rules every change to this repo must satisfy, whoever makes it — a human or an AI agent.
> Agents read this before [AGENTS.md](../AGENTS.md) conventions, the specification [SPEC.md](../SPEC.md) (this repo's PRD), or the
> [feature catalog](../features/features.yml). Ratified by merged PR; amended only per § 8.

## 1. Missions

The Recon Engine's direction is to become the ultimate open home for all things operational-to-ledger reconciliation — data, tools, resources and transparency, gathered in one place that anyone can inspect and reuse.

1. **Provide data, tools, resources and transparency for all stakeholders, finance and operations professionals, and the general public.** Finance and operations teams, ERP operators, builders, and the general public are first-class audiences. The aim is a shared, open commons: the same residual, the same tools, and the same trail of evidence for everyone.
2. **Make every month's residual honest, queryable and auditable.** Residual = Finance − Operations, decomposed gross-not-net into six buckets, with every inter-bucket transfer that has no operational event flowing into Unexplained. Interpretation is scored where it has drifted from fact; items are never silently netted against each other.
3. **Put that recon in every operator's and builder's hands, starting with the path into the Django ERP.** Serve it as an open engine with a dependency-free core and a published build order — an open toolkit for working with all things operational-to-ledger reconciliation. The repo is at specification stage; these missions set the course and do not claim the engine already runs.

These missions set the course; they do not claim the work is finished. They serve SPEC.md, the design of record: one monthly residual, six buckets, gross-never-net, and the build order in §6. The earlier single-mission paragraph from the governance-baseline PR is absorbed into these three. Invariants already stated in constitution §2 (spec leads, gross never net, transfers are events, dependency-free core, build order) stay in §2, unchanged. Every feature must trace to them.

_Source: [../SPEC.md](../SPEC.md) §1.1._

## 2. Invariants (non-negotiable)

- **The spec leads.** [SPEC.md](../SPEC.md) is the design of record. Read it before changing anything; a design decision that moves changes SPEC.md in the same PR, not only the code.
- **Gross, never net.** Offsetting items never cancel each other inside or across residual buckets (SPEC § 3).
- **Transfers are events.** Every reclassification between buckets that has no matching operational event is recorded as a flow into Unexplained (SPEC § 3, § 3.6).
- **A dependency-free core.** `recon_engine/` imports only the standard library. An adapter that needs a dependency declares it with the adapter, never in the core.
- **The build order holds.** Work follows SPEC § 6. A step is done when its behaviour is implemented, tested and described in README.md.
- **Files have a place.** Files are placed per `SCHEMA.md`; a new directory gets its own `SCHEMA.md` and a row in its parent.
- **Every change is a pull request.** Branch from `main` and open a PR with a Conventional Commit title; nothing is pushed to `main` directly, and an agent never merges.
- **No silent failures.** No suppressed type errors and no empty exception handlers.

## 3. Authority and precedence

When two documents disagree, the higher one wins and the lower one is fixed in the same PR:

1. This constitution (and its ratified amendments in [docs/amendments/](amendments/))
2. [AGENTS.md](../AGENTS.md) — how to work here (commands, conventions, Definition of Done)
3. [SPEC.md](../SPEC.md) — what the product must do (cited by section, `§ n`; the PRD's part in this repo)
4. [features/features.yml](../features/features.yml) — what it does today (stable feature ids)
5. ADRs in [docs/adr/](adr/) and specs — why and how a specific change was made
6. Code, tests, generated files

## 4. Roles: humans and AI agents

| Actor | May | May not |
| --- | --- | --- |
| Maintainer (human) | Ratify amendments, SPEC changes and releases by merging PRs; change settings, secrets, branch protection | — |
| AI agent | Read this file first; open PRs on a branch with Conventional Commit titles; update the feature catalog, the SPEC's generated block and docs in the same PR as the change; propose amendments | Merge its own PRs; push to the default branch; force-push; change repo settings or branch protection; print or commit secrets; invent features or requirements (unknown = **TBD**) |

## 5. How the artifacts relate

| Artifact | Answers | Owned by | Rule |
| --- | --- | --- | --- |
| `docs/constitution.md` | What must always hold | Maintainer | Changes only by amendment (§ 8) |
| `docs/amendments/NNNN-*.md` | How and why the rules changed | Proposer → maintainer | Append-only; ratified by merged PR |
| `AGENTS.md` / `CLAUDE.md` | How to work here | Repo | Must link this file; `CLAUDE.md` imports `@AGENTS.md` |
| `SPEC.md` (the PRD here) | What the product must do | Maintainer | The design of record; requirements are cited by section (`§ n`), and section numbers are never reused |
| `features/features.yml` | What the product does, where, proven how | Repo | Every user-facing feature has an id, `status`, location and `prd:` refs |
| SPEC.md "Feature catalog" block | Spec → feature trace | Generated | `governance_lint.py prd-sync`; never hand-edit |
| `docs/adr/NNNN-*.md` | Why a hard-to-reverse decision was made | Proposer | One ADR per decision; an amendment may cite one |
| `CHANGELOG.md` | What shipped | release-please | Generated from Conventional Commits; never hand-edit |

## 6. Change process

| Change | Required in the same PR |
| --- | --- |
| Typo, docs fix, refactor with no user-visible effect | Conventional Commit title |
| New or changed user-facing feature | Entry in `features/features.yml` (`status`, `link`/`docs`, `prd:`), regenerated SPEC.md block |
| New or changed requirement or design decision | SPEC.md edit (a new section number is never a reused one), feature `prd:` refs updated |
| Hard-to-reverse technical decision | ADR in `docs/adr/` |
| Change to this constitution | Amendment record in `docs/amendments/` (§ 8) |

## 7. Quality gates

```bash
python3 -m pip install -e .
python3 -m pytest                                              # once the first test lands (SPEC § 6, step 1)
python3 tools/unwrap-prose.py --check                          # markdown is one paragraph per line
python3 <bamr87/bamr87>/tools/schema_lint.py check .           # every file has a place in SCHEMA.md
python3 <bamr87/bamr87>/tools/governance_lint.py check .       # this constitution, the amendment log, the catalog and the SPEC block agree
```

plus the shared fleet gate in CI, `bamr87/bamr87/.github/workflows/standard-ci.yml@v2` (`.github/workflows/ci.yml`). The conformance check (`.github/workflows/conformance.yml`) is advisory until the repo's MUST rows pass.

## 8. Amendments

This constitution changes only through a numbered record in [docs/amendments/](amendments/) (`NNNN-kebab-slug.md`, copied from [0000-template.md](amendments/0000-template.md)):

1. **Propose** — open a PR that adds the record (`Status: proposed`) *and* the edit to this file it describes. Name what it affects: constitution sections, SPEC sections, feature ids.
2. **Review** — the maintainer reviews; an agent never approves or merges its own amendment.
3. **Ratify** — merging the PR ratifies it. The record says `Status: ratified` and `Ratified by:` the PR. A rejected or withdrawn PR keeps its record with that status; numbers are never reused.
4. **Supersede** — a later amendment may replace an earlier one; mark the old record `superseded by NNNN`.

Records are append-only history: fix a ratified rule with a new amendment, never by editing an old record. [0001](amendments/0001-ratify-constitution.md) ratifies this document.
