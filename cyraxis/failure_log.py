"""
cyraxis/failure_log.py — persistent failure database
Module 5 of CYRAXIS: Grounded Research for Open Knowledge

Logs every answer that scores below 6 to a SQLite database.
Data persists between Python sessions — unlike memory.py's
in-memory list, these failures survive restarts.

WHY SQLITE AND NOT JSON:
A JSON file of failures works for 100 entries.
At 10,000 entries, loading the entire file is slow.
SQLite allows queries: "give me failures from this week"
or "count failures per topic" without loading everything.
These queries are exactly what nightly_audit.py will run.

WHY THE THRESHOLD IS 6:
evaluate_answer() returns scores 1-10.
Grade C starts at 5, Grade B at 7.
6 is the boundary between "inadequate" and "acceptable."
Logging scores below 6 captures genuine failures —
not minor imperfections, but responses GROK should not
have given. These become the audit trail.

"""

import sqlite3
import os
from datetime import datetime

# Database file — stored in the repo root
DB_PATH = "cyraxis_failures.db"


def _get_connection() -> sqlite3.Connection:
    """
    Return a SQLite connection, creating the database and
    table if they do not exist yet.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    cursor = conn.cursor()

    # Create table if it does not exist
    # IF NOT EXISTS means this is safe to call on every connection
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS failures (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            question  TEXT    NOT NULL,
            answer    TEXT    NOT NULL,
            score     INTEGER NOT NULL,
            critique  TEXT    NOT NULL,
            timestamp TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def log_failure(
    question: str,
    answer:   str,
    score:    int,
    critique: str,
) -> int:
    """
    Log a failure (score < 6) to the database.

    Args:
        question: The question that was asked.
        answer:   The answer CYRAXIS gave.
        score:    The quality score (should be < 6 to be a failure).
        critique: The evaluator's specific critique.

    Returns:
        int: The database row ID of the inserted failure.

    Note: This function logs ANY score passed to it.
    The caller is responsible for only calling log_failure
    when score < 6. This keeps the module flexible.
    """
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO failures (question, answer, score, critique, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (question, answer, score, critique,
          datetime.now().isoformat()))

    conn.commit()
    row_id = cursor.lastrowid
    conn.close()

    return row_id


def get_all_failures() -> list[dict]:
    """
    Retrieve all logged failures from the database.

    Returns:
        list of dicts, each with keys:
        id, question, answer, score, critique, timestamp
        Ordered by timestamp descending (most recent first).
    """
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question, answer, score, critique, timestamp
        FROM failures
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_failures_below(threshold: int = 4) -> list[dict]:
    """
    Retrieve failures with score below a threshold.
    Useful for finding the worst responses specifically.
    """
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question, answer, score, critique, timestamp
        FROM failures
        WHERE score < ?
        ORDER BY score ASC, timestamp DESC
    """, (threshold,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def count_failures() -> int:
    """Return the total number of logged failures."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM failures")
    count = cursor.fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    print("Testing cyraxis/failure_log.py")
    print("=" * 55)

    # Log 3 test failures
    id1 = log_failure(
        question="What is 2 + 2?",
        answer="The answer is 5.",
        score=1,
        critique="Factually incorrect. Basic arithmetic error."
    )
    id2 = log_failure(
        question="Explain transformers",
        answer="Transformers are robots that turn into cars.",
        score=2,
        critique="Confuses ML architecture with fictional robots."
    )
    id3 = log_failure(
        question="What is AI safety?",
        answer="I don't know.",
        score=3,
        critique="No attempt to answer. Incomplete response."
    )

    print(f"Logged 3 failures with IDs: {id1}, {id2}, {id3}")
    print(f"Total failures in database: {count_failures()}")

    print("\nAll failures (most recent first):")
    for f in get_all_failures():
        print(f"  [{f['score']}/10] {f['question'][:40]}")
        print(f"  Critique: {f['critique'][:60]}")
        print()

    print(f"Failures with score below 3: {len(get_failures_below(3))}")
    print(f"\nDatabase file: {os.path.abspath(DB_PATH)}")