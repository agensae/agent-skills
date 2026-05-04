# Local Customization Guide

Use this guide when adapting the public `codex-thread-logs` skill for a specific project, workstation, or Codex installation. The public skill intentionally avoids guessing local facts. A private or project-local copy should add only facts that have been verified in that environment.

## What To Customize

Customize the skill when you can verify one or more of these facts:

- The project-relative path where the skill is installed.
- The local Codex data directory, if it is not the default `~/.codex`.
- The project or toolchain layout that affects where referenced worktrees, artifacts, or archived files move.
- Shell or runtime conventions that make examples directly runnable in that environment.

Do not add speculative operating-system matrices, package-manager alternatives, or broad filesystem search advice. If a local fact is unknown, keep the public generic wording.

## Verify The Skill Path

The public skill says to use this skill's `scripts/find_thread_log.py`. In a project-local installation, replace that with the shortest correct command agents can run from the usual repository root.

Example:

```bash
python3 .agents/skills/codex-thread-logs/scripts/find_thread_log.py <thread-id>
```

Before changing `SKILL.md`, verify the path exists from the expected working directory:

```bash
test -f .agents/skills/codex-thread-logs/scripts/find_thread_log.py
```

If agents may run from multiple roots, keep the generic wording in `SKILL.md` and document project-specific invocation details in a separate project-local reference named `references/project-local-thread-logs.md`. 

## Verify The Codex Data Directory

The locator defaults to:

- `~/.codex/sessions`
- `~/.codex/shell_snapshots`
- `~/.codex/session_index.jsonl`

If the local Codex installation uses another data directory, verify it before editing examples:

```bash
python3 <skill-path>/scripts/find_thread_log.py <thread-id> --sessions-root <absolute-sessions-root>
```

Then update local guidance to prefer that explicit `--sessions-root` value. Keep the default-path explanation only if it remains true for the environment.

Good local customization:

```bash
python3 .agents/skills/codex-thread-logs/scripts/find_thread_log.py <thread-id> --sessions-root /path/to/codex/sessions
```

Bad local customization:

```bash
find "$HOME" -name "*<thread-id>*"
```

Broad crawls are still a fallback only when the user explicitly asks for them or the Codex data root cannot be established any other way.

## Add Project-Specific Stale Path Notes

The public checklist says to watch for stale paths after referenced files, artifacts, or worktrees moved or were archived. A project-local copy can be sharper if the project has a known archive or generated-output convention.

For example, if completed work moves to a project archive directory, update the checklist with the exact path pattern:

```markdown
- Stale live paths after project artifacts moved to `work/archive`.
```

Only name paths that are stable for the project. Avoid including a developer's personal absolute path unless the skill is private to that machine.

## Preserve Portability Boundaries

When editing the skill for local use:

- Keep the JSONL inspection guidance defensive.
- Keep the warnings against opening huge `session_meta` lines blindly.
- Keep line-reference guidance path-specific: report both log path and line number.
- Prefer adding one verified local command over adding many conditional examples.
- Put detailed local environment notes in `references/project-local-thread-logs.md` instead of bloating `SKILL.md`.

## Suggested Localization Workflow

1. Find the installed skill directory from the target project root.
2. Run the locator once against a known thread ID.
3. Confirm whether `~/.codex` is correct or an explicit `--sessions-root` is needed.
4. Check whether the project has stable archive, artifact, or worktree relocation paths that affect stale log references.
5. Edit `SKILL.md` only for high-value facts agents should see immediately.
6. Put lower-frequency details in `references/project-local-thread-logs.md`.
7. Re-run the locator command from the expected working directory.

## Review Checklist

Before considering a localized copy ready, confirm:

- The main locator command works as written.
- The command does not require broad filesystem crawling.
- Any absolute paths are appropriate for the intended audience.
- Project-specific stale-path notes are accurate and current.
- Public distribution copies do not contain private project paths, usernames, internal archive names, or machine-specific Codex install paths.
