# Local Customization Guide

Use this guide when adapting the `worktree-coding-fleet` skill for a specific project, workstation, public distribution target, or agent harness. The base skill should stay focused on the portable workflow: isolated git worktrees, explicit worker contracts, parent-owned serial merges, validation, and cleanup.

## What To Customize

Customize the skill only when you can verify one or more of these facts:

- The local harness can delegate workers and expose stable worker or session IDs.
- The harness can run each worker in a separate git worktree or a separately configured process pointed at that worktree.
- The local approval, sandbox, commit, branch, cleanup, or validation policy differs from the base skill.
- The local installation has stable commands, flags, branch conventions, or worktree directory conventions worth making directly runnable.

Do not add speculative platform matrices, unverified feature claims, or broad installation advice. If a local fact is unknown, keep the generic baseline in `SKILL.md`.

## Preserve The Portable Baseline

Every local adaptation must preserve these parent-owned responsibilities:

- Create or select the integration branch.
- Assign each worker one branch and one worktree.
- Pass explicit worker contracts instead of relying on inherited context.
- Keep sibling worktrees and live worker surfaces off-limits unless handed back.
- Merge worker branches serially in the parent worktree.
- Run validation after merges.
- Record branch, worktree, worker, merge, validation, boundary, and cleanup evidence in the ledger.
- Remove eligible worker worktrees and branches only after evidence is recorded and final validation is complete.

Unknown or weakly documented harnesses should use the portable baseline: one process or session per isolated git worktree, explicit worker contracts, serial parent merges, and a final validation ledger.

## Harness Mapping Notes

Use these notes only as starting points for verified local customization:

- Codex: map workers to subagents in subagent-capable app or CLI sessions after explicit delegation; default to `fork_context: false` and pass worker contracts explicitly. Parent owns approval policy, final integration or merge commits, and cleanup; workers may commit only when assigned.
- Claude Code: map workers to worktree-isolated subagents (`isolation: worktree`) or Agent View/`claude --bg`; use Agent Teams only when enabled and do not assume teammates are worktree-isolated.
- OpenCode: map workers to configured primary agents or subagents with per-agent permissions; use separate git worktree directories or instances for isolation.
- pi.dev: use only with a Pi extension/package or external SDK/RPC wrapper that provides delegated agents and separate git worktrees.
- OpenClaw: map slices to specialist lanes or spawned sub-agents with lane contracts, handoff rules, and tool-risk/tool-policy limits; provide git worktree isolation separately.
- Cursor: map workers to background or cloud subagents when available; record agent IDs and keep parent-owned serial merges, validation, and cleanup.
- GitHub Copilot: map workers to cloud-agent sessions, CLI sessions, or Agent HQ tasks; treat cloud branches and pull requests as worker evidence, not final merge authority.
- Devin Desktop/Windsurf: map workers to Cascade or Devin Local sessions in worktree mode or Agent Command Center spaces; record auto-created worktree paths.
- Cline: map workers to CLI/Kanban agent-team tasks or one Cline process per worktree; treat built-in subagents as read-only unless documented otherwise.
- Gemini CLI/Aider: run one process or session per isolated worktree; keep branch coordination, conflict arbitration, and cleanup parent-controlled.

## Add Local Commands Sparingly

Prefer one verified command pattern over multiple conditional examples. Before adding local commands, verify they work from the expected repository root and that they do not depend on private paths unless the skill copy is private to that machine or project.

Good local customization:

```bash
git worktree add ../my-repo-slice-a codex/slice-a
```

Bad local customization:

```bash
find "$HOME" -name "my-repo" -type d
```

Broad filesystem searches and guessed install paths make future agents slower and less reliable.

## Review Checklist

Before considering a localized copy ready, confirm:

- Delegation commands, worktree paths, and branch naming rules are verified.
- Worker IDs or session IDs can be recorded in the ledger.
- The customization preserves parent-owned merges, validation, and cleanup.
- Any absolute paths are appropriate for the intended audience.
- Public distribution copies do not contain usernames, private repository paths, internal service names, private branch names, or machine-specific tool locations.
