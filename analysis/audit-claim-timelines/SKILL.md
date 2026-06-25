---
name: audit-claim-timelines
description: Detect semantic claim timelines across documentation, specifications, changelogs, archived findings, git history, or versioned snapshots. Use when Codex needs to determine whether requirements, policies, examples, contracts, or findings are oscillating A/B/A, drifting, superseded, unresolved in parallel, historically resolved, or materially consistent across revisions.
---

# Audit Claim Timelines

## Overview

Use this skill to analyze how a rule, requirement, policy, example, contract, or finding changes over time. Treat wording changes as evidence, but classify the timeline by the underlying assertion about what behavior, obligation, prohibition, precedence rule, decision point, or interpretation is required or implied, regardless of how that assertion is phrased in a particular revision.

## Core Workflow

1. Identify revision sources.
   - Use bounded sources named by the user or discovered from local context: git history, archived snapshots, dated run directories, changelogs, review ledgers, or supplied document versions.
   - Keep the search scope narrow. Prefer exact paths, date ranges, commit ranges, run directories, or artifact names over broad repository scans.

2. Extract normative claims.
   - Look for requirements, prohibitions, precedence rules, examples that define expected behavior, schema rules, policy bullets, acceptance criteria, and finding recommendations.
   - Ignore purely editorial wording unless it changes the expected behavior or interpretation.

3. Normalize claim labels.
   - Give each candidate a stable semantic label, such as `target-resolution-scope`, `missing-provenance-behavior`, or `source-copy-equality`.
   - Group wording variants under the same label only when they govern the same behavior or decision point.

4. Build a chronological timeline.
   - Record each material state as `revision | source | claim_label | state | evidence | notes`.
   - Preserve enough evidence for a reader to verify the classification: path, line when available, commit/run/date/version, and a short paraphrase.
   - Keep historical states separate from the current state.

5. Classify the timeline.
   - Assign one verdict from the Verdict Schema below.
   - Require actual A/B/A evidence before calling something oscillation.
   - Distinguish true flip-flops from one-off contradictions, ordinary corrections, resolved history, and current parallel conflicts.

6. Report materiality.
   - Explain whether the issue is currently blocking convergence, only historical context, or an unresolved current contradiction.
   - Recommend the next action at the claim level: fix source-of-truth wording, leave as resolved history, inspect a sibling artifact, or avoid applying a stale finding.

## Reference Routing

- Read [references/report-template.md](references/report-template.md) before producing a user-facing audit report.
- Read [references/worker-prompt.md](references/worker-prompt.md) only when splitting a large history across subagents or worker threads.

## Verdict Schema

Use these verdicts when classifying a semantic claim timeline.

| Verdict | Use When | Minimum Evidence |
| --- | --- | --- |
| `true_oscillation` | A claim changes from state A to incompatible state B, then later restores state A or an equivalent of A. | At least three chronological states: A, B, A. Each state must cite a revision and source. |
| `one_off_contradiction` | A later revision conflicts with an earlier claim, but there is no later restoration of the earlier state. | At least two incompatible states and evidence that the current or later direction is not yet A/B/A. |
| `superseded` | A later revision intentionally replaces an earlier claim and current sources consistently follow the replacement. | Earlier state, replacement state, and current-state evidence. |
| `semantic_drift` | A claim changes incrementally across revisions so the current behavior differs materially from the start, without a clean A/B/A or direct contradiction. | Multiple states showing cumulative movement and the current resulting behavior. |
| `current_parallel_conflict` | Two or more current sources assert incompatible states for the same claim. | Current evidence for each incompatible source; history is optional but useful. |
| `resolved_history` | Historical contradiction or oscillation existed, but current sources now align. | Historical conflict evidence plus current aligned evidence. |
| `no_material_conflict` | Revisions differ in wording, location, or detail without changing the governed behavior. | Evidence that the states are semantically equivalent or non-overlapping. |

### Oscillation Rules

- Require semantic A/B/A, not just repeated edits or repeated findings.
- Treat A' as A only when it restores the same behavior, refusal, precedence, obligation, or acceptance rule.
- Do not classify A/B as oscillation. Use `one_off_contradiction`, `superseded`, or `current_parallel_conflict`.
- Do not classify A/B/C as oscillation unless C materially restores A.
- Do not count a stale archived finding as current A unless current sources or later revisions adopt it.

### Materiality

After the verdict, classify impact:

- `blocking`: current sources or findings can drive contradictory implementation or documentation changes.
- `stale`: the issue appears only in historical artifacts and should not drive current fixes.
- `needs_owner_decision`: current sources conflict and no source-of-truth rule resolves precedence.
- `resolved`: current sources agree and no active finding remains.

### Disqualifiers

Do not mark a claim as material when:

- only filenames, headings, or wording changed;
- the change narrows a rule without later broadening it back;
- the claim moved between files but retained the same behavior;
- the evidence lacks revision identity, source path, or enough text to verify the state.

## Evidence Discipline

- Do not infer oscillation from repeated findings alone. Show the semantic state changes.
- Do not treat newer text as automatically correct. Determine whether the current state is consistent with the intended source of truth.
- Do not collapse incompatible claims into one "clarification" when they require different behavior.
- Do not report a material contradiction without evidence from at least two revisions or sources.
- State uncertainty explicitly when a claim cannot be normalized or a revision source is incomplete.
