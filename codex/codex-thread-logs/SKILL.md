---
name: codex-thread-logs
description: Find, inspect, and summarize Codex CLI or ChatGPT desktop thread/session logs, including legacy Codex Desktop metadata. Use when working with Codex thread IDs, active or archived session JSONL, SQLite thread indexes, session_index, shell snapshots, log discovery, compaction, subagent events, tool-call extraction, or line references.
---

# Codex Thread Logs

Use this skill for the technical mechanics of working with Codex thread logs. Keep this work objective: locate logs, extract evidence, understand JSONL shape, and control token cost.

## Locate Logs

Preferred locator: use this skill's `scripts/find_thread_log.py` to find threads by ID or unique prefix.

Use `--date YYYY-MM-DD` when the date is known.

The locator searches active and archived rollout JSONL, shell snapshots, `session_index.jsonl`, and the read-only `threads` and `thread_spawn_edges` indexes in versioned `state_*.sqlite` databases. Rollout JSONL is the transcript; the other sources are indexes or supporting state.

The default Codex data directory is `$CODEX_HOME` when set, otherwise the current user's `.codex` directory:

- macOS/Linux: `~/.codex/sessions`, `~/.codex/archived_sessions`, `~/.codex/shell_snapshots`, `~/.codex/session_index.jsonl`, and `~/.codex/state_*.sqlite`.
- Windows: the equivalent paths under `%USERPROFILE%\.codex`.

If `sqlite_home` points elsewhere, pass that directory with `--sqlite-root`. Treat `state_*.sqlite` as an internal, versioned index and query it read-only. Do not search `logs_*.sqlite` for conversation content: those databases contain runtime diagnostics, can be very large, and are not rollout transcripts.

Avoid broad home-directory, application-data, or machine-wide crawls unless the user explicitly asks for them. Examples of large paths agents might be tempted to search:

- macOS: `$HOME`, `$HOME/Library/Application Support`.
- Linux: `$HOME`, `$HOME/.config`, `$HOME/.local/share`.
- Windows: `%USERPROFILE%`, `%APPDATA%`, `%LOCALAPPDATA%`.

Those searches are slow, noisy, and often produce permission-denial output.

## JSONL Shape

Codex session logs are newline-delimited JSON. Each line can have a different payload shape. Common forms:

- `session_meta`: metadata with session ID, cwd, source, instructions, dynamic tools, model provider, and sometimes subagent details.
- `world_state` and `turn_context`: app, workspace, permissions, tool, and turn snapshots.
- `response_item`: model-visible messages, reasoning, tool calls/outputs, web or tool search, and inter-agent messages.
- `event_msg`: app/runtime events such as `agent_message`, `task_complete`, `token_count`, `context_compacted`, and `sub_agent_activity`.
- `compacted`: replacement history and compaction-window metadata; it can be especially large.
- `inter_agent_communication_metadata`: routing metadata around inter-agent messages.

Record and payload vocabularies are version-dependent. Inventory a log before assuming its schema:

```jq
[.type, (.payload.type? // "")] | @tsv
```

Use defensive `jq`: prefer `?`, `//`, `select(...)`, and `input_line_number`. Do not assume every payload has `.payload.type`, `.payload.name`, `.payload.content`, or `.payload.output`. Avoid `keys` or fixed-path assumptions as primary inspection; use them only after confirming the line family.

When projecting rows for `@tsv`, remember that selected fields may be objects or arrays, not only scalars. Use `tostring` or `tojson` for uncertain values, or select explicit scalar subfields before formatting.

## Useful Extractors

Use `jq` defensively. The filters below are shell-neutral; pass the target JSONL log file to `jq` using the syntax appropriate for the current OS and shell.

Find tool calls:

```jq
select(.type=="response_item" and ((.payload.type? // "")|endswith("_call")))
  | [input_line_number,
     .payload.type,
     (.payload.name? // .payload.action.type? // ""),
     (.payload.call_id? // .payload.id? // ""),
     ((.payload.arguments? // .payload.input? // .payload.action? // "")|tostring|gsub("\n";" ")|.[0:1200])]
  | @tsv
```

Find tool outputs:

```jq
select(.type=="response_item" and ((.payload.type? // "")|endswith("_output")))
  | [input_line_number,
     .payload.type,
     (.payload.call_id? // ""),
     ((.payload.output? // .payload.tools? // .payload.content? // "")|tostring|gsub("\n";" ")|.[0:1600])]
  | @tsv
```

Find agent messages and task completion:

```jq
select(.type=="event_msg" and (.payload.type=="agent_message" or .payload.type=="task_complete"))
  | [input_line_number,
     .payload.type,
     (.payload.phase? // ""),
     ((.payload.message? // .payload.last_agent_message? // "")|tostring|gsub("\n";" ")|.[0:1600])]
  | @tsv
```

Find token counts:

```jq
select(.type=="event_msg" and .payload.type=="token_count")
  | [input_line_number,
     (.payload.info.last_token_usage.total_tokens? // ""),
     (.payload.info.total_token_usage.total_tokens? // ""),
     (.payload.info.model_context_window? // "")]
  | @tsv
```

Find collaboration/subagent events:

```jq
select(
  (.type=="event_msg" and
    ((((.payload.type? // "")|startswith("collab_"))) or .payload.type?=="sub_agent_activity"))
  or
  (.type=="response_item" and .payload.type?=="agent_message")
)
  | [input_line_number,
     .type,
     (.payload.type? // ""),
     (.payload.agent_thread_id? // .payload.author? // ""),
     (.payload.agent_path? // .payload.recipient? // ""),
     (.payload.kind? // "")]
  | @tsv
```

For `multi_agent_version: "v2"`, follow parent/child evidence carefully:

- Parent `event_msg/sub_agent_activity.agent_thread_id` is the child thread ID; run the locator again with that ID when the child is material. Child threads may be absent from `session_index.jsonl` but present in the SQLite index.
- In a child `session_meta`, `.payload.id` and the rollout filename identify the child. `.payload.session_id` may identify the root session, and `.payload.source` may be an object containing `subagent.thread_spawn` metadata rather than a string.
- Returned child messages appear in the parent as `response_item/agent_message` with `author`, `recipient`, and content. The delegated prompt may be stored as `encrypted_content` or an opaque encrypted argument. Do not reconstruct or claim its exact text; inspect the child's visible context and report the limitation.

Find compaction boundaries:

```jq
select(.type=="compacted" or (.type=="event_msg" and .payload.type?=="context_compacted"))
  | [input_line_number,
     .type,
     (.payload.window_number? // ""),
     (.payload.window_id? // "")]
  | @tsv
```

## Token Discipline

- Do not open raw lines blindly. `session_meta`, `world_state`, `turn_context`, `compacted`, and tool outputs may each contain tens or hundreds of kilobytes.
- Locate first, then use a targeted text search such as `rg -n` to find relevant anchors before opening line ranges.
- Prefer projected `jq` rows over full raw dumps of JSONL lines.
- Keep `max_output_tokens` low by default: 4k to 12k. Raise it only for a specific line range that is already justified.
- Avoid repeated large slices. Once a section is understood, refer to line numbers instead of reopening it.
- Inspect child logs only when they are material to the current investigation.
- When a command reports a huge "Original token count", remember the model usually sees the retained/truncated output, not the full original stream. Still treat large retained outputs as costly because they are re-sent in later model turns.

## Technical Friction Checklist

When reporting log-work mechanics, note whether any of these happened:

- Wrong search root or missed session log.
- Missed archived rollout or stale `rollout_path` in the SQLite thread index.
- Permission errors from broad filesystem crawling.
- Token-heavy dumps or repeated large retained outputs.
- JSONL-shape assumptions that failed.
- Opaque or encrypted delegated prompts that prevent exact subagent-instruction review.
- Stale paths after referenced files, artifacts, or worktrees moved or were archived.
- Useless shell snapshots, runtime `logs_*.sqlite` scans, or unrelated cache matches.
- Interrupted commands, killed searches, closed stdin, or cleanup issues.
- Bare line numbers without the log path.
