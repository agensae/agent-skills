#!/usr/bin/env python3
"""Locate Codex session logs for a thread ID without broad filesystem crawling."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("thread_id", help="Codex thread/session UUID or unique prefix")
    parser.add_argument(
        "--date",
        help="Optional date to narrow search: YYYY-MM-DD or YYYY/MM/DD",
    )
    parser.add_argument(
        "--sessions-root",
        default=str(codex_home / "sessions"),
        help="Active sessions root. Defaults to $CODEX_HOME/sessions or ~/.codex/sessions",
    )
    parser.add_argument(
        "--sqlite-root",
        help="Directory containing state_*.sqlite. Defaults to the sessions root's parent",
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


def normalized_date(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.replace("/", "-")
    parts = normalized.split("-")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise SystemExit("--date must be YYYY-MM-DD or YYYY/MM/DD")
    return normalized


def path_matches_date(path: Path, date: str | None) -> bool:
    return not date or f"rollout-{date}T" in path.name


def state_databases(sqlite_root: Path) -> list[Path]:
    def version(path: Path) -> int:
        suffix = path.stem.removeprefix("state_")
        return int(suffix) if suffix.isdigit() else -1

    return sorted(sqlite_root.glob("state_*.sqlite"), key=version, reverse=True)


def state_db_matches(
    thread_id: str, sqlite_root: Path
) -> tuple[list[str], list[Path], list[str]]:
    matches: list[str] = []
    rollout_paths: list[Path] = []
    relations: set[str] = set()
    lower_bound = thread_id
    upper_bound = f"{thread_id}\U0010ffff"

    for database in state_databases(sqlite_root):
        try:
            with sqlite3.connect(
                f"{database.resolve().as_uri()}?mode=ro", uri=True, timeout=1
            ) as connection:
                columns = {
                    row[1] for row in connection.execute("PRAGMA table_info(threads)")
                }
                if "id" not in columns:
                    continue

                def column(name: str, fallback: str = "''") -> str:
                    return f'"{name}"' if name in columns else fallback

                order_by = column("updated_at_ms", column("updated_at", "id"))
                query = f"""
                    SELECT id,
                           {column('rollout_path')},
                           {column('title')},
                           {column('archived', '0')},
                           {column('cli_version')}
                    FROM threads
                    WHERE id >= ? AND id < ?
                    ORDER BY {order_by} DESC
                """
                rows = connection.execute(query, (lower_bound, upper_bound))
                matched_ids: list[str] = []
                for row_id, rollout_path, title, archived, cli_version in rows:
                    matched_ids.append(row_id)
                    matches.append(
                        f"{database}:{row_id}\t{rollout_path}\tarchived={archived}"
                        f"\tcli={cli_version}\t{title}"
                    )
                    if rollout_path:
                        rollout_paths.append(Path(rollout_path).expanduser())

                edge_columns = {
                    row[1]
                    for row in connection.execute(
                        "PRAGMA table_info(thread_spawn_edges)"
                    )
                }
                if (
                    matched_ids
                    and {"parent_thread_id", "child_thread_id"} <= edge_columns
                ):
                    status_column = "status" if "status" in edge_columns else "''"
                    edge_query = f"""
                        SELECT parent_thread_id, child_thread_id, {status_column}
                        FROM thread_spawn_edges
                        WHERE parent_thread_id = ? OR child_thread_id = ?
                    """
                    for row_id in matched_ids:
                        for parent_id, child_id, status in connection.execute(
                            edge_query, (row_id, row_id)
                        ):
                            relations.add(
                                f"{database}:parent={parent_id}\tchild={child_id}"
                                f"\tstatus={status}"
                            )

                if matched_ids:
                    break
        except (OSError, sqlite3.Error):
            continue

    return matches, rollout_paths, sorted(relations)


def collect_matches(
    thread_id: str,
    sessions_root: Path,
    search_root: Path,
    sqlite_root: Path,
    date: str | None,
) -> dict[str, list[str]]:
    logs = (
        {path.resolve() for path in search_root.rglob(f"*{thread_id}*.jsonl")}
        if search_root.exists()
        else set()
    )

    archived_root = sessions_root.parent / "archived_sessions"
    if archived_root.exists():
        logs.update(
            path.resolve()
            for path in archived_root.glob(f"*{thread_id}*.jsonl")
            if path_matches_date(path, date)
        )

    database_matches, database_rollouts, thread_relations = state_db_matches(
        thread_id, sqlite_root
    )
    logs.update(
        path.resolve()
        for path in database_rollouts
        if path.is_file() and path_matches_date(path, date)
    )

    shell_root = sessions_root.parent / "shell_snapshots"
    snapshots: list[str] = []
    if shell_root.exists():
        snapshots = sorted(str(path) for path in shell_root.glob(f"*{thread_id}*.sh"))

    index_path = sessions_root.parent / "session_index.jsonl"
    index_matches: list[str] = []
    if index_path.exists():
        with index_path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    if thread_id in line:
                        index_matches.append(f"{index_path}:{line_no}:{line.strip()}")
                else:
                    if str(item.get("id", "")).startswith(thread_id):
                        index_matches.append(
                            f"{index_path}:{line_no}:"
                            f"{item.get('id', '')}\t{item.get('thread_name', '')}\t"
                            f"{item.get('updated_at', '')}"
                        )

    return {
        "session_logs": sorted(str(path) for path in logs),
        "shell_snapshots": snapshots,
        "state_database": database_matches,
        "thread_relations": thread_relations,
        "session_index": index_matches,
    }


def main() -> int:
    args = parse_args()
    sessions_root = Path(os.path.expanduser(args.sessions_root)).resolve()
    sqlite_root = (
        Path(os.path.expanduser(args.sqlite_root)).resolve()
        if args.sqlite_root
        else sessions_root.parent
    )
    search_root = date_dir(sessions_root, args.date)
    date = normalized_date(args.date)

    if not sessions_root.exists():
        raise SystemExit(f"sessions root does not exist: {sessions_root}")
    result = collect_matches(
        args.thread_id, sessions_root, search_root, sqlite_root, date
    )
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
