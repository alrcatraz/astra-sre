"""Shared SQLite access layer for Astra SRE scripts.

Reads from the same database as astra-knowledge-base-mcp.
Uses the ASTRA_KB_PATH environment variable (default: ~/.astra/knowledge-base.db).
"""

import json
import os
import sqlite3

DEFAULT_DB_PATH = os.path.expanduser("~/.astra/knowledge-base.db")


def get_db_path() -> str:
    return os.environ.get("ASTRA_KB_PATH", DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def build_fts5_query(query: str) -> str | None:
    """Convert natural language query to FTS5 query syntax."""
    tokens = []
    for word in query.strip().lower().split():
        word = word.strip("'\"")
        if len(word) > 1:
            tokens.append(f"{word}*")
        elif word:
            tokens.append(word)
    if not tokens:
        return None
    return " AND ".join(tokens)


def parse_tags(tags_json: str) -> list[str]:
    if not tags_json:
        return []
    try:
        return json.loads(tags_json)
    except (json.JSONDecodeError, TypeError):
        return []


def search_kb(kb_name: str, query: str, limit: int = 5) -> list[dict]:
    """Search a single knowledge base using FTS5."""
    fts_query = build_fts5_query(query)
    if not fts_query:
        return []

    try:
        with get_connection() as conn:
            cur = conn.execute(
                """SELECT c.id, c.title, c.content, c.source, c.tags, rank AS score
                   FROM chunks_fts
                   JOIN chunks c ON c.id = chunks_fts.rowid
                   WHERE chunks_fts MATCH ?
                     AND c.kb_name = ?
                   ORDER BY rank
                   LIMIT ?""",
                (fts_query, kb_name, limit),
            )
            results = []
            for row in cur.fetchall():
                score = round(-row["score"], 4) if row["score"] < 0 else 0.0
                results.append({
                    "kb": kb_name,
                    "title": row["title"] or "",
                    "content": row["content"] or "",
                    "score": score,
                    "source": row["source"],
                    "tags": parse_tags(row["tags"]),
                })
            return results
    except Exception as e:
        print(f"❌ DB query failed: {e}", file=__import__("sys").stderr)
        return []


def list_all(kb_name: str) -> list[dict]:
    """List all entries in a knowledge base."""
    try:
        with get_connection() as conn:
            cur = conn.execute(
                """SELECT DISTINCT c.title, c.content, c.source, c.tags
                   FROM chunks c
                   WHERE c.kb_name = ?
                   ORDER BY c.title, c.id""",
                (kb_name,),
            )
            results = []
            for row in cur.fetchall():
                results.append({
                    "title": row["title"] or "",
                    "content": row["content"] or "",
                    "source": row["source"],
                    "tags": parse_tags(row["tags"]),
                })
            return results
    except Exception as e:
        print(f"❌ DB query failed: {e}", file=__import__("sys").stderr)
        return []
