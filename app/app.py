from typing import Any

import duckdb
from fastapi import FastAPI

from app.database import setup_database
from app.models import StringMatch, StringQuery
from app.paths import db as db_path
from app.queries import match_passwords, match_usernames

# Initialize the database on startup if it doesn't exist
if not db_path.exists():
    try:
        setup_database()
    except Exception as e:
        print(f"Database already initialized or error: {e}")


app = FastAPI(title="Credential Checker", version="0.1.0")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/password", response_model=list[StringMatch])
def check_password(query: StringQuery) -> list[StringMatch]:
    """
    Check if a password exists in the breach database.

    Parameters:
    - password: The password to search for
    - exact_match: If True, search for exact matches; if False, search for partial matches (default: False)
    - ignore_case: If True, search case-insensitively (default: False)

    Returns a list of matches with their sources.
    """
    with duckdb.connect(db_path, read_only=True) as conn:
        sql = match_passwords(
            input=query.query_string,
            ignore_case=query.ignore_case,
            include_substring_matches=query.include_substring_matches,
        )
        results = conn.execute(sql).fetchall()

        matches = [StringMatch(matched_string=row[0], source=row[1]) for row in results]
        return matches


@app.post("/username", response_model=list[StringMatch])
def check_username(query: StringQuery) -> list[StringMatch]:
    """
    Check if a username exists in the breach database.

    Parameters:
    - username: The username to search for
    - exact_match: If True, search for exact matches; if False, search for partial matches (default: False)
    - ignore_case: If True, search case-insensitively (default: False)

    Returns a list of matches with their sources.
    """
    with duckdb.connect(db_path, read_only=True) as conn:
        sql = match_usernames(
            input=query.query_string,
            ignore_case=query.ignore_case,
            include_substring_matches=query.include_substring_matches,
        )
        results = conn.execute(sql).fetchall()

        matches = [StringMatch(matched_string=row[0], source=row[1]) for row in results]
        return matches


@app.get("/stats")
def get_stats() -> dict[str, Any]:
    """Get statistics about the password database"""
    conn = duckdb.connect(db_path, read_only=True)
    try:
        _total = conn.execute("SELECT COUNT(*) FROM passwords;").fetchone()
        total = _total if _total is not None else 0
        sources = conn.execute(
            "SELECT source, COUNT(*) as count FROM passwords GROUP BY source ORDER BY count DESC;"
        ).fetchall()

        return {
            "total_passwords": total,
            "sources": [{"name": s[0], "count": s[1]} for s in sources],
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
