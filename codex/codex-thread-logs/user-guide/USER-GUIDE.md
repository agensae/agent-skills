# Codex Thread Logs User Guide

Use this guide when you want an Agent to inspect a saved Codex thread and need 
to provide the right session ID.

Codex may refer to the same ID as a `thread ID` or a `session ID`. For this 
skill, either label is fine: provide the ID for the conversation you want
inspected.

## What To Provide

When requesting a log review, include:

Required:
- The session ID.
- What you want checked: a review of the decisions made by Codex, how well Codex
followed instructions, an analysis of a specific claim Codex made, what tools
Codex used, etc.

Optional / helpful:
- The date, if you know it.
- Whether the run came from the Codex app, interactive CLI, or `codex exec`.

Example:

```text
Use $codex-thread-logs to inspect session 0192661e-9384-4d75-b122-40a1cff1996b
from July 1, 2026. Check whether the final answer was supported by tool output.
```

## Find A Session ID

### Codex App (Recommended)

1. Find the chat in the Codex app sidebar.
2. Right-click the chat.
3. Click `Copy session ID`.
4. Paste that ID into your request.

### Codex CLI

In an active interactive CLI session, type:

```text
/status
```

The status view shows the current thread ID under 'Session:'.

## Advanced Options

### Codex CLI - Previous Sessions

To find a previous interactive CLI session, run:

```bash
codex resume
```

The resume picker lists recent sessions. Highlight the session you want and
copy its session ID from the picker or details pane. Use these variants when
needed:

```bash
codex resume --all
codex resume --include-non-interactive
```

`--all` includes sessions outside the current working directory.
`--include-non-interactive` includes `codex exec` runs in the picker.

If you only need the most recent session, run `codex resume --last`, then type
`/status` after the session opens.

### Codex Install Directory

If the picker is not enough, Codex stores local session files under:

```text
~/.codex/sessions/
```

Those files are organized by date, and the session ID is usually the last UUID
in the `.jsonl` filename.

For non-interactive runs, start the run with JSON output if you know you will
need the ID later:

```bash
codex exec --json "your prompt here"
```

The JSONL stream includes a `thread.started` event with a `thread_id`. Note
that `codex exec --ephemeral` does not write the saved session files used for
log review.

