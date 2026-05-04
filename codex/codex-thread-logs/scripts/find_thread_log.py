#!/usr/bin/env python3
"""Locate Codex session logs for a thread ID without broad filesystem crawling."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("thread_id", help="Codex thread/session UUID or unique prefix")
    parser.add_argument(
        "--date",
        help="Optional date to narrow search: YYYY-MM-DD or YYYY/MM/DD",
    )
    parser.add_argument(
        "--sessions-root",
        default=str(Path.home() / ".codex" / "sessions"),
        help="Codex sessions root. Defaults to ~/.codex/sessions",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of plain paths",
    )
    return parser.parse_args()


def date_dir(root: Path, value: str | None) -> Path:
    if not value:
        return root
    normalized = value.replace("-", "/")
    parts = normalized.split("/")
    if len(parts) != 3:
        raise SystemExit("--date must be YYYY-MM-DD or YYYY/MM/DD")
    return root / parts[0] / parts[1] / parts[2]


def collect_matches(thread_id: str, sessions_root: Path, search_root: Path) -> dict[str, list[str]]:
    logs = sorted(str(path) for path in search_root.rglob(f"*{thread_id}*.jsonl"))

    shell_root = sessions_root.parent / "shell_snapshots"
    snapshots: list[str] = []
    if shell_root.exists():
        snapshots = sorted(str(path) for path in shell_root.glob(f"*{thread_id}*.sh"))

    index_path = sessions_root.parent / "session_index.jsonl"
    index_matches: list[str] = []
    if index_path.exists():
        with index_path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if thread_id in line:
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        index_matches.append(f"{index_path}:{line_no}:{line.strip()}")
                    else:
                        index_matches.append(
                            f"{index_path}:{line_no}:"
                            f"{item.get('id', '')}\t{item.get('thread_name', '')}\t"
                            f"{item.get('updated_at', '')}"
                        )

    return {
        "session_logs": logs,
        "shell_snapshots": snapshots,
        "session_index": index_matches,
    }


def main() -> int:
    args = parse_args()
    sessions_root = Path(os.path.expanduser(args.sessions_root)).resolve()
    search_root = date_dir(sessions_root, args.date)

    if not sessions_root.exists():
        raise SystemExit(f"sessions root does not exist: {sessions_root}")
    if not search_root.exists():
        raise SystemExit(f"search root does not exist: {search_root}")

    result = collect_matches(args.thread_id, sessions_root, search_root)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    found = False
    for label, paths in result.items():
        if paths:
            found = True
            print(f"{label}:")
            for path in paths:
                print(path)
    if not found:
        print(f"No matches under {search_root}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

