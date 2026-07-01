---
name: worktree-coding-fleet
description: Coordinate parallel coding subagents in isolated git worktrees, then merge and validate the combined result. Use when the user explicitly wants parallel implementation work and the slices may need overlapping files, branches, risky integration, or independent implementation attempts. Do not use for read-only review or small coding tasks that fit one shared-workspace owner.
---

# Worktree Coding Fleet

Use this skill when parallel implementation is worth the overhead of isolated branches and worktrees. The parent agent owns orchestration, merge order, conflict decisions, final validation, and the user-facing report.

## Decision Gate

Use a worktree fleet only when at least one of these is true:

- The user explicitly asks for parallel coding agents, isolated worktrees, independent branches, or branch arbitration.
- The work can be sliced into implementation lanes but the write sets may overlap.
- Workers need to explore competing implementations before the parent chooses or merges.
- Shared-workspace subagents would risk overwriting files, racing commands, or confusing validation state.

Use a simpler path instead when the task is read-only or a small, clearly single-owner writing task.

## Parent Responsibilities

1. Inspect the repository state before creating worktrees.
   - Read local instructions such as `AGENTS.md`.
   - Scope instruction discovery to allowed paths. Once `excluded_context` or `off_limits_surfaces` paths are known or declared, prune them from discovery commands; for example: `find . -path './docs/internal' -prune -o -path './protected' -prune -o -name AGENTS.md -print`.
   - Do not traverse `excluded_context` or `off_limits_surfaces` paths merely to find repo instructions.
   - Run `git status --short` and identify existing user changes.
   - Record the base commit with `git rev-parse HEAD`.
   - Record the parent checkout before any branch switch: current branch with `git branch --show-current` or detached state, current commit, whether this is the user's primary checkout, the intended `target_branch`, and the intended `return_branch`. Default both `target_branch` and `return_branch` to the entry branch for local implementation tasks. Use a different target only when the user asks for a branch-only handoff, pull request, or another explicit integration target.
   - If the parent checkout is already on an old fleet/integration branch but the task should start from `main` or trunk, resolve that mismatch before creating another integration branch. Do not silently stack a new integration branch on top of a stale checked-out fleet branch.
   - Create or select one integration branch where worker branches will be merged.

2. Plan slices before delegation.
   - Give each slice a stable `slice_id`, branch name, and worktree path.
   - Name owned files, likely shared surfaces, read-only files, excluded context, off-limits surfaces, validation commands, and expected output.
   - Keep edit boundaries separate from context boundaries. Use `read_only_files` for readable write-protected files.
   - Prefer disjoint ownership, but explicitly list overlap where integration risk is expected.
   - Read [references/worker-contract-and-ledger.md](references/worker-contract-and-ledger.md) before launching workers.

3. Create isolated worktrees.
   - Use `git worktree add` from the parent repository and record the absolute path.
   - Choose a repo-adjacent or temporary path that is writable in the current sandbox or permission model.
   - Avoid nesting worktrees inside the primary worktree unless the repo already supports that layout and ignores the path.
   - Do not let workers share a worktree.

4. Dispatch workers with strict boundaries.
   - Tell each worker to operate only in its assigned worktree and branch.
   - Tell workers not to push, rebase the integration branch, edit sibling worktrees, access off-limits surfaces, or clean up branches/worktrees.
   - If the harness supports Codex subagents, default to `fork_context: false` unless the task needs inherited context.
   - Require a worker report with changed files, commits or uncommitted status, commands run, failures, and expected conflicts.

5. Merge one worker at a time.
   - Read each worker's changed-file list before merging.
   - Merge into the integration branch in the parent worktree, not from a worker worktree.
   - Run at least slice-relevant validation after each merge.
   - Run full or broad validation after the final merge when the task risk justifies it.
   - Record merge status and validation evidence in the ledger.

6. Arbitrate conflicts centrally.
   - Resolve simple conflicts in the parent branch when the correct result is clear.
   - Re-dispatch to the owning worker with conflict context when domain judgment is needed.
   - Do not ask multiple workers to resolve the same conflict concurrently.
   - Do not merge a branch whose tests or status are unknown unless the ledger marks the risk explicitly.

7. Deliver or explicitly defer the integrated result.
   - After final validation and after the integration result is committed, decide whether `target_branch` should receive the integration branch result. Do this before presenting the work as complete.
   - If the user requested a branch-only handoff, pull request, review branch, or explicitly said not to update the target branch, record `delivery_status: not-delivered:<reason>` and keep the integration branch as the deliverable.
   - Otherwise, move `target_branch` to the integrated result using the safest normal Git operation that matches repository policy. Prefer a fast-forward-only merge when `target_branch` is an ancestor of the integration branch. Use a non-fast-forward merge only when that is required and acceptable for the repo. Never force-push, reset, rebase, squash, or discard user changes as part of delivery unless the user explicitly asks.
   - If delivery is blocked by divergence, dirty state, approval limits, failed validation, or unclear policy, record `delivery_status: blocked:<reason>` or `pending:<reason>` with the exact active branch, integration branch, target branch, and next command or decision needed.
   - If the integration branch is not delivered to `target_branch`, the final report must lead with: work is on `<integration_branch>` and is not on `<target_branch>`. Include the exact next command when a fast-forward or merge appears safe.
   - If delivery succeeds, record the delivered commit and verify `target_branch` contains the integration head.

8. Record evidence and clean up.
   - Before cleanup, record branch names, worktree paths, worker commits, merge commits, validation commands and results, conflict dispositions, and boundary deviations in the ledger.
   - After final validation, remove each worker worktree by default when the worker has finished, the worktree is clean, the branch is merged or intentionally skipped, and no explicit retention reason exists.
   - Delete eligible merged worker branches only after their worktrees are removed, using safe branch deletion. Never delete skipped, unmerged, dirty, or unexplained worker branches as routine cleanup.
   - Never remove the integration branch or the parent target repo worktree.
   - Do not retain a worker worktree only because it contains audit evidence; preserve that evidence in the ledger first.
   - If a worker worktree or branch is not removed, record `kept:<reason>`, `pending:<reason>`, or `blocked:<reason>` in `cleanup_status`. Include the owner and follow-up condition for every retained or deferred item.
   - After worker cleanup, restore the user's primary parent checkout to `return_branch` when the integration result is committed, validation evidence is recorded, and the parent worktree is clean. Use a normal `git switch`; never force, reset, stash, or discard user changes just to restore the branch.
   - If the parent checkout cannot be restored, record `parent_checkout_status` as `kept:<reason>`, `pending:<reason>`, or `blocked:<reason>` with owner and follow-up condition. The final report must name the active branch left behind.
   - Run `git status` and `git worktree list` after branch restoration or after recording the restoration blocker, and record the final result in the ledger.
   - Follow the environment's approval policy for destructive cleanup commands. If approval or sandbox limits prevent cleanup, record `pending:<reason>` instead of silently retaining worktrees.

## Worker Contract

Every worker assignment must include:

- `slice_id`
- `base_commit`
- `worker_branch`
- `worktree_path`
- `owned_files`
- `read_only_files`
- `excluded_context`
- `off_limits_surfaces`
- `shared_surfaces`
- `task`
- `commands_allowed`
- `validation_required`
- `report_required`

Use the prompt skeleton in [references/worker-contract-and-ledger.md](references/worker-contract-and-ledger.md) when the assignment is more than a trivial slice.

## Boundary Terms

Use these terms consistently:

- `owned_files`: files or globs the worker may edit, stage, and commit in its assigned worktree.
- `read_only_files`: files or globs the worker may read when needed for local context, but must not edit, stage, commit, regenerate, format, delete, or otherwise mutate.
- `excluded_context`: sources the worker must not read, inspect, quote, summarize, or use for decisions. Use this for black-box constraints, hidden evaluator files, sibling-agent outputs, root-cause notes, private logs, or documents that would leak the answer.
- `off_limits_surfaces`: paths, worktrees, processes, branches, services, or artifacts the worker must neither inspect/read nor mutate. Use this for sibling worktrees, a live worker's owned files, production state, or any surface where even probing can interfere with ownership or test integrity.
- `shared_surfaces`: APIs, schemas, generated outputs, docs, tests, or behaviors that may require integration coordination even when write ownership is separate.

Use `excluded_context` for reasoning-context read bans. Use `off_limits_surfaces` when any interaction with the surface is unsafe.

## Evidence Ledger

Maintain a compact ledger while the fleet runs. Set `parent_session` to the actual parent thread/session identifier before adding rows. In Codex, use `$CODEX_THREAD_ID` when available. In other harnesses, use the harness-provided parent session or thread ID. If unavailable, record `unknown:<reason>` and mention the missing source in the final report. Do not use vague placeholders.

At minimum, track:

- `parent_session`
- `parent_entry_branch`
- `target_branch`
- `parent_return_branch`
- `child_session`
- `base_commit`
- `worker_branch`
- `worktree_path`
- `slice_id`
- `owned_files`
- `read_only_files`
- `excluded_context`
- `off_limits_surfaces`
- `shared_surfaces`
- `commands_run`
- `changed_files`
- `worker_commit`
- `merge_commit`
- `merge_status`
- `validation_after_merge`
- `raw_issue_count`
- `adopted_issue_count`
- `blockers`
- `boundary_deviations`
- `cleanup_status`
- `cleanup_command_result`
- `delivery_status`
- `delivery_command_result`
- `parent_checkout_status`
- `final_target_status`
- `final_worktree_list`
- `retained_owner_followup`

For final reports, include only the high-signal ledger rows: branch, slice, merge result, validation result, boundary deviations, remaining blockers, delivery state, cleanup state with reason when not `removed`, parent checkout restoration state, and post-cleanup `git status`/`git worktree list` evidence for any remaining worker worktrees or non-restored parent branch. If delivery did not put the integration result on `target_branch`, make that the first final-report item.

## Guardrails

- Do not use worktrees to bypass sandbox, approval, network, or repository policy.
- Do not allow a worker to edit the parent integration worktree.
- Do not race a live worker by accessing any surface assigned under `off_limits_surfaces` unless the worker has finished or explicitly handed it back.
- Do not merge without reading the worker report and checking repository status.
- Do not rely on slice tests as whole-system proof after multiple branches merge.
- Do not delete worktrees or branches until the parent has recorded the evidence needed to recover or audit the run and final validation is complete.
- Do not keep worker worktrees solely for audit evidence. Use `kept:<reason>` only when retention is explicitly required and has an owner plus follow-up condition.
- Do not imply the user's target branch contains the work merely because the primary checkout is clean on that branch. Verify branch containment and report when the integration result is branch-only.
- Do not leave the user's primary checkout on a fleet integration branch as the routine end state. Restore the recorded `return_branch`, or report the exact blocker and active branch.
- Treat any mutation of `read_only_files`, any use of `excluded_context`, or any access to `off_limits_surfaces` as a boundary deviation that must be reported and resolved before merge.
