---
name: codex-thread-logs
description: Find, inspect, and summarize Codex or Codex Desktop thread/session logs. Use when working with Codex thread IDs, session JSONL files, session_index, shell snapshots, log discovery, thread/log shape, tool-call extraction or line references.
---

# Codex Thread Logs

Use this skill for the technical mechanics of working with Codex thread logs. Keep this work objective: locate logs, extract evidence, understand JSONL shape, and control token cost.

## Locate Logs

Preferred locator: use this skill's `scripts/find_thread_log.py` to find threads by ID or unique prefix.

Use `--date YYYY-MM-DD` when the date is known.

The default search area is the Codex data directory under the current user's home directory:

- macOS/Linux: `~/.codex/sessions`, sibling `~/.codex/shell_snapshots`, and `~/.codex/session_index.jsonl`.
- Windows: `%USERPROFILE%\.codex\sessions`, sibling `%USERPROFILE%\.codex\shell_snapshots`, and `%USERPROFILE%\.codex\session_index.jsonl`.

Avoid broad home-directory, application-data, or machine-wide crawls unless the user explicitly asks for them. Examples of large paths agents might be tempted to search:

- macOS: `$HOME`, `$HOME/Library/Application Support`.
- Linux: `$HOME`, `$HOME/.config`, `$HOME/.local/share`.
- Windows: `%USERPROFILE%`, `%APPDATA%`, `%LOCALAPPDATA%`.

Those searches are slow, noisy, and often produce permission-denial output.

## JSONL Shape

Codex session logs are newline-delimited JSON. Each line can have a different payload shape. Common forms:

- `session_meta`: large metadata object with session ID, cwd, source, base instructions, tools, skills, model provider, and sometimes subagent parent details.
- `turn_context`: environment snapshot for a turn.
- `response_item`: model-visible items such as messages, reasoning, `function_call`, and `function_call_output`.
- `event_msg`: app/runtime events such as `agent_message`, `task_complete`, `token_count`, `exec_command_end`, and `collab_*` subagent events.

Use defensive `jq`: prefer `?`, `//`, `select(...)`, and `input_line_number`. Do not assume every payload has `.payload.type`, `.payload.name`, `.payload.content`, or `.payload.output`. Avoid `keys` or fixed-path assumptions as primary inspection; use them only after confirming the line family.

When projecting rows for `@tsv`, remember that selected fields may be objects or arrays, not only scalars. Use `tostring` or `tojson` for uncertain values, or select explicit scalar subfields before formatting.

## Useful Extractors

Use `jq` defensively. The filters below are shell-neutral; pass the target JSONL log file to `jq` using the syntax appropriate for the current OS and shell.

Find tool calls:

```jq
select(.type=="response_item" and .payload.type=="function_call")
  | [input_line_number, .payload.name, (.payload.arguments|gsub("\n";" ")|.[0:1200])] | @tsv
```

Find final messages and task completion:

```jq
select(.type=="event_msg" and (.payload.type=="agent_message" or .payload.type=="task_complete"))
  | [input_line_number, .payload.type, ((.payload.message // .payload.last_agent_message // "")|gsub("\n";" ")|.[0:1600])] | @tsv
```

Find token counts:

```jq
select(.type=="event_msg" and .payload.type=="token_count")
  | [input_line_number, .payload.info.last_token_usage.total_tokens, .payload.info.total_token_usage.total_tokens] | @tsv
```

Find collaboration/subagent events:

```jq
select(.type=="event_msg" and (.payload.type|test("collab_"))) | input_line_number
```

## Token Discipline

- Do not open line 1 blindly. `session_meta` often contains huge base instructions and skill metadata.
- Locate first, then use a targeted text search such as `rg -n` to find relevant anchors before opening line ranges.
- Prefer projected `jq` rows over full raw dumps of JSONL lines.
- Keep `max_output_tokens` low by default: 4k to 12k. Raise it only for a specific line range that is already justified.
- Avoid repeated large slices. Once a section is understood, refer to line numbers instead of reopening it.
- Inspect child logs only when they are material to the current investigation.
- When a command reports a huge "Original token count", remember the model usually sees the retained/truncated output, not the full original stream. Still treat large retained outputs as costly because they are re-sent in later model turns.

## Technical Friction Checklist

When reporting log-work mechanics, note whether any of these happened:

- Wrong search root or missed session log.
- Permission errors from broad filesystem crawling.
- Token-heavy dumps or repeated large retained outputs.
- JSONL-shape assumptions that failed.
- Stale paths after referenced files, artifacts, or worktrees moved or were archived.
- Useless shell snapshots or unrelated cache matches.
- Interrupted commands, killed searches, closed stdin, or cleanup issues.
- Bare line numbers without the log path.
