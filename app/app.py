from typing import Any

import duckdb
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import RequestValidationError

from app.database import setup_database
from app.models import StringMatch, StringQuery
from app.paths import app as app_dir, db as db_path
from app.queries import match_passwords, match_usernames

# Initialize the database on startup if it doesn't exist
if not db_path.exists():
    try:
        setup_database()
    except Exception as e:
        print(f"Database already initialized or error: {e}")

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Credential Checker", version="0.1.0")
app.state.limiter = limiter

# Mount static files
static_dir = app_dir / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Serve the main web interface"""
    return FileResponse(str(app_dir / "static" / "index.html"))


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/search/password", response_model=list[StringMatch])
@limiter.limit("30/minute")
def search_password(request: Request, query: StringQuery) -> list[StringMatch]:
    """Search for passwords in the database (limit: 30 requests/minute)"""
    with duckdb.connect(db_path, read_only=True) as conn:
        sql = match_passwords(
            input=query.query_string,
            ignore_case=query.ignore_case,
            include_substring_matches=query.include_substring_matches,
        )
        results = conn.execute(sql).fetchall()

        matches = [StringMatch(matched_string=row[0], source=row[1]) for row in results]
        return matches


@app.post("/search/username", response_model=list[StringMatch])
@limiter.limit("30/minute")
def search_username(request: Request, query: StringQuery) -> list[StringMatch]:
    """Search for usernames in the database (limit: 30 requests/minute)"""
    with duckdb.connect(db_path, read_only=True) as conn:
        sql = match_usernames(
            input=query.query_string,
            ignore_case=query.ignore_case,
            include_substring_matches=query.include_substring_matches,
        )
        results = conn.execute(sql).fetchall()

        matches = [StringMatch(matched_string=row[0], source=row[1]) for row in results]
        return matches


@app.post("/password", response_model=list[StringMatch])
@limiter.limit("30/minute")
def check_password(request: Request, query: StringQuery) -> list[StringMatch]:
    """
    Check if a password exists in the breach database (limit: 30 requests/minute).

    Parameters:
    - password: The password to search for
    - ignore_case: If True, search case-insensitively (default: True)
    - include_substring_matches: If True, search for partial matches (default: False)

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
@limiter.limit("30/minute")
def check_username(request: Request, query: StringQuery) -> list[StringMatch]:
    """
    Check if a username exists in the breach database (limit: 30 requests/minute).

    Parameters:
    - username: The username to search for
    - ignore_case: If True, search case-insensitively (default: True)
    - include_substring_matches: If True, search for partial matches (default: False)

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
    import sys
    
    # Ensure the project root is in the path
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
