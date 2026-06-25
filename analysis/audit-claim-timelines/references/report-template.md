# Report Template

Use this structure for user-facing semantic timeline audits. Keep it compact unless the user asks for a full ledger.

## Summary

State the overall result in one or two sentences:

```md
Verdict: `<verdict>` / Impact: `<impact>`

The claim `<claim_label>` <oscillated | drifted | was superseded | remains conflicted | is resolved>. The current state is <short current-state summary>.
```

## Verdict Table

Use one row per material claim:

| Claim | Verdict | Impact | Current State | Evidence |
| --- | --- | --- | --- | --- |
| `<claim_label>` | `<verdict>` | `<impact>` | `<current state>` | `<key path/revision refs>` |

## Timeline

Use one chronological table per material claim:

| Revision | Source | State | Evidence |
| --- | --- | --- | --- |
| `<commit/run/date/version>` | `<path:line or artifact>` | `A: <paraphrase>` | `<short quote/paraphrase>` |
| `<commit/run/date/version>` | `<path:line or artifact>` | `B: <paraphrase>` | `<short quote/paraphrase>` |
| `<commit/run/date/version>` | `<path:line or artifact>` | `A: <paraphrase>` | `<short quote/paraphrase>` |

## Required Evidence

- Include path and line when available.
- Include commit, run number, date, version, or snapshot identity.
- Paraphrase long passages; quote only short phrases needed to identify the state.
- Mark evidence as `current` or `historical` when that distinction affects materiality.
- Name missing evidence explicitly instead of filling gaps with inference.

## Recommended Next Action

Choose one:

- `fix_current_source_conflict`: align current sources before applying downstream findings.
- `apply_current_finding`: the finding matches current source-of-truth behavior and does not undo later fixes.
- `ignore_stale_history`: historical churn is resolved and should not drive current changes.
- `request_owner_decision`: current sources conflict and precedence is not derivable.
- `split_claims`: apparent conflict is caused by conflating two different claims.

## Compact Final Form

For small audits, this is enough:

```md
Verdict: `<verdict>` / Impact: `<impact>`

Timeline:
- `<revision>`: `<state>` (`<path:line>`)
- `<revision>`: `<state>` (`<path:line>`)
- `<revision>`: `<state>` (`<path:line>`)

Current state: <summary>.
Next action: `<recommended_next_action>`.
```
