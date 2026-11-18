<!-- kit: governance v0.1.0 -->
# 0002 — Missions

- **Status:** proposed
- **Date:** 2026-11-16
- **Proposed by:** Grok Bot (agent), at the maintainer's request
- **Ratified by:**
- **Affects:** constitution §1; SPEC.md §1.1; RECON-007
- **Supersedes:** none
- **Related:** [SPEC.md](../../SPEC.md) §1.1

## Context

Constitution §1 was a single mission sentence or short paragraph, not one direction statement with exactly three numbered missions. The fleet rule is that every repo's constitution §1 uses that form, adopted through a numbered amendment the maintainer ratifies by merging. Mission 1 is the maintainer's own wording, adapted to this repo: provide data, tools, resources and transparency for all stakeholders, practitioners in the domain, and the general public. The ambition is the direction, not a claim that the work is already finished.

The earlier §1 text was:

> The Recon Engine reconciles a business's operational event stream against its general ledger the way debits reconcile against credits. It serves the finance and operations sides of a manufacturing or technology business, first through the Django ERP (bamr87/djangoerp), by assembling one honest monthly residual (Residual = Finance − Operations), decomposing it into six buckets, and scoring where interpretation has drifted from fact. The repo is at specification stage: SPEC.md is the design of record and its § 6 is the build order.

## Amendment

Retitle constitution §1 **Missions**. Replace the body of §1 with the following. Any invariants or other normative rules that already lived outside §1 are unchanged.

The Recon Engine's direction is to become the ultimate open home for all things operational-to-ledger reconciliation — data, tools, resources and transparency, gathered in one place that anyone can inspect and reuse.

1. **Provide data, tools, resources and transparency for all stakeholders, finance and operations professionals, and the general public.** Finance and operations teams, ERP operators, builders, and the general public are first-class audiences. The aim is a shared, open commons: the same residual, the same tools, and the same trail of evidence for everyone.
2. **Make every month's residual honest, queryable and auditable.** Residual = Finance − Operations, decomposed gross-not-net into six buckets, with every inter-bucket transfer that has no operational event flowing into Unexplained. Interpretation is scored where it has drifted from fact; items are never silently netted against each other.
3. **Put that recon in every operator's and builder's hands, starting with the path into the Django ERP.** Serve it as an open engine with a dependency-free core and a published build order — an open toolkit for working with all things operational-to-ledger reconciliation. The repo is at specification stage; these missions set the course and do not claim the engine already runs.

These missions set the course; they do not claim the work is finished. They serve SPEC.md, the design of record: one monthly residual, six buckets, gross-never-net, and the build order in §6. The earlier single-mission paragraph from the governance-baseline PR is absorbed into these three. Invariants already stated in constitution §2 (spec leads, gross never net, transfers are events, dependency-free core, build order) stay in §2, unchanged. Every feature must trace to them.

_Source: [../SPEC.md](../SPEC.md) §1.1._

## Consequences

Agents and reviewers judge fit against these three missions before inventing scope, treating them as the direction of the repo rather than a description of what already ships. The same text is added as SPEC.md §1.1 so the constitution's `_Source:` line stays accurate. The PRD purpose, goals, feature catalog and invariants outside this addition are unchanged except for a new catalog entry (RECON-007) and a regenerated feature-catalog block where the repo already has one. This PR also aligns the README and AGENTS.md one-liners with the missions and links them to constitution §1.
