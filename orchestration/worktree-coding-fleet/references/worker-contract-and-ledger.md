# Worker Contract and Ledger

Read this reference before launching worktree workers or writing the final fleet ledger.

## Worker Assignment Skeleton

Use this shape for each worker. Keep the assignment concrete enough that the worker can operate without touching sibling worktrees or guessing ownership.

```text
Use the assigned worktree only.

slice_id:
base_commit:
worker_branch:
worktree_path:
owned_files: files/globs you may edit, stage, and commit.
read_only_files: files/globs you may read for context if needed, but must not edit, stage, commit, regenerate, format, delete, or otherwise mutate.
excluded_context: sources you must not read, inspect, quote, summarize, or use for decisions.
off_limits_surfaces: paths, worktrees, branches, processes, services, or artifacts you must neither inspect/read nor mutate.
shared_surfaces:
task:
commands_allowed:
validation_required:

Rules:
- Work only in worktree_path on worker_branch.
- Do not push, rebase the integration branch, edit sibling worktrees, or clean up branches/worktrees.
- If you need to mutate anything listed under read_only_files, stop and report why.
- If you need excluded_context or off_limits_surfaces access, stop and report why.
- Before finishing, report git status, changed files, commands run, failures, boundary deviations, and likely integration conflicts.
```

## Worker Report Skeleton

Require each worker to return this information.

```text
slice_id:
child_session:
worker_branch:
worktree_path:
base_commit:
changed_files:
worker_commit:
commands_run:
validation_result:
failures_or_blockers:
read_only_files_mutated:
excluded_context_used:
off_limits_surfaces_accessed:
expected_conflicts:
handoff_notes:
```

Use `worker_commit: none` when the worker leaves changes uncommitted. If uncommitted changes are allowed, the parent must inspect and commit or discard them according to the user's request and repository policy.

## Parent Ledger Template

Use one row per worker branch plus extra rows for conflict redispatches when needed.
Before final reporting, backfill every row with the same concrete `parent_session` value. In Codex, use `$CODEX_THREAD_ID` when available; otherwise use the harness-provided parent session/thread ID or `unknown:<reason>`.

| Field | Record |
| --- | --- |
| `parent_session` | Actual parent thread/session identifier, e.g. `$CODEX_THREAD_ID` in Codex; otherwise the harness-provided ID or `unknown:<reason>`. |
| `child_session` | Worker thread/session identifier when known. |
| `base_commit` | Commit used to create the worker branch/worktree. |
| `slice_id` | Stable short label for the worker lane. |
| `worker_branch` | Branch assigned to the worker. |
| `worktree_path` | Absolute path to the worker worktree. |
| `owned_files` | Files or globs the worker was allowed to edit. |
| `read_only_files` | Files or globs the worker was allowed to read if needed, but not allowed to edit, stage, commit, regenerate, format, delete, or otherwise mutate. |
| `excluded_context` | Sources the worker was not allowed to read, inspect, quote, summarize, or use for decisions. |
| `off_limits_surfaces` | Paths, worktrees, branches, services, or artifacts the worker was not allowed to inspect/read or mutate. |
| `shared_surfaces` | APIs, schemas, generated outputs, docs, or tests likely to overlap. |
| `commands_run` | Commands the worker or parent actually ran for the slice. |
| `changed_files` | Files changed by the worker branch before merge. |
| `worker_commit` | Worker commit ID, or `none` if uncommitted. |
| `merge_commit` | Merge or squash commit ID after parent integration. |
| `merge_status` | `merged`, `skipped`, `conflict-resolved`, `conflict-redispatched`, or `blocked`. |
| `validation_after_merge` | Exact command and result after this branch was merged. |
| `raw_issue_count` | Count of issues reported by the worker before parent dedupe. |
| `adopted_issue_count` | Count of issues the parent accepted as real or still relevant. |
| `boundary_deviations` | Any mutation of `read_only_files`, use of `excluded_context`, or access to `off_limits_surfaces`, plus the parent disposition. |
| `blockers` | Remaining blocker, if any. |
| `cleanup_status` | `removed`, `kept:<reason>`, `pending:<reason>`, or `blocked:<reason>`. Use `removed` for the normal successful cleanup path. |
| `cleanup_command_result` | Cleanup commands attempted by the parent and their result, including worktree removal and safe branch deletion. Use `none:<reason>` only when no cleanup command was appropriate. |
| `final_worktree_list` | Post-cleanup `git worktree list` result or a compact summary naming any remaining worker worktrees. |
| `retained_owner_followup` | Required when `cleanup_status` is not `removed`; name the owner and follow-up condition for retained, pending, or blocked worktrees/branches. |

Default cleanup policy: after final validation, the parent removes clean completed worker worktrees whose branches were merged or intentionally skipped, unless an explicit retention reason exists. The parent then deletes eligible merged worker branches with safe branch deletion after their worktrees are gone. The parent never removes the integration branch or parent target repo worktree. Audit evidence alone is not a retention reason; preserve evidence in the ledger first.

## Merge Verdicts

- `merged`: branch integrated without unresolved conflict and passed required validation.
- `skipped`: branch was intentionally not merged; record the reason.
- `conflict-resolved`: parent resolved conflicts and validation is recorded.
- `conflict-redispatched`: conflict was sent back to one owner with enough context to continue.
- `blocked`: branch cannot be merged safely with current evidence.

## Final Report Shape

Summarize the fleet in this order:

1. Integration branch and base commit.
2. Worker branches merged, skipped, or blocked.
3. Validation run after each merge and after final integration.
4. Conflicts and how they were resolved or redispatched.
5. Boundary deviations and parent disposition.
6. Remaining blockers or risk.
7. Cleanup status for worktrees and branches, including post-cleanup `git worktree list` evidence and owner/follow-up condition for anything not `removed`.
