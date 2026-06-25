# Worker Prompt

Use this template only when the history is large enough to split by artifact, claim cluster, subsystem, or ledger type.

## Template

```text
Use $audit-claim-timelines at <skill-path> to audit one bounded semantic-claim history.

Repository or workspace: <absolute path>

Assigned scope:
- Artifact, claim cluster, or ledger type: <scope>
- Revision sources to inspect: <git range, archive directory, snapshots, changelogs, or supplied files>
- Current source-of-truth candidates: <paths or rules>
- Output expected: raw claim-timeline findings only

Rules:
- Read the skill fully before analysis.
- Do not inspect sibling worker outputs.
- Do not mutate files, ledgers, specs, docs, or source code.
- Do not apply fixes.
- Do not infer oscillation from repeated findings alone; prove semantic A/B/A.
- Report `no_material_conflict` when wording changed but behavior did not.
- Include path, line when available, revision identity, claim label, state, verdict, impact, and recommended next action.

Return:
1. Scope reviewed.
2. Raw finding count.
3. One compact timeline per material claim.
4. Any missing evidence or uncertainty.
```

## Split Guidance

- Split by artifact when each document has its own history.
- Split by claim cluster when one document has many independent rules.
- Split by ledger type when archived findings are already organized by target area.
- Keep current source-of-truth files visible to every worker when they are needed for materiality.
- Avoid broad "integration" workers unless a cross-source conflict remains after scoped workers report.

## Merge Guidance

- Dedupe only when two workers report the same claim, same state sequence, and same required next action.
- Preserve separate findings when the same files contain different claim labels.
- Re-check any `true_oscillation` centrally before reporting it, because it is the highest-risk verdict.
