#!/usr/bin/env python

import duckdb as ddb

from app import paths


def setup_pw_table():
    """Initialize and populate the password database from parquet files"""
    create_cmd = """
    CREATE OR REPLACE TABLE passwords (
      password VARCHAR,
      source VARCHAR,
      UNIQUE(password, source)
    )
    """

    conn = ddb.connect(paths.db)
    conn.execute(create_cmd)

    for pwpath in paths.pw.glob("*.parquet"):
        insert_cmd = f"""
        INSERT INTO passwords
        SELECT password, '{pwpath.stem}' as source
        FROM '{pwpath}'
        """
        conn.execute(insert_cmd)

    n_rows = conn.execute("SELECT count(*) FROM passwords;").fetchall()[0][0]
    print(f"Number of Rows in password table: {n_rows:_}")

    conn.close()


def setup_usernames_table():
    """Initialize and populate the usernames table from parquet files"""
    create_cmd = """
    CREATE OR REPLACE TABLE usernames (
      username VARCHAR,
      source VARCHAR,
      UNIQUE(username, source)
    )
    """

    conn = ddb.connect(paths.db)
    conn.execute(create_cmd)

    for upath in paths.user.glob("*.parquet"):
        insert_cmd = f"""
        INSERT INTO usernames
        SELECT username, '{upath.stem}' as source
        FROM '{upath}'
        """
        conn.execute(insert_cmd)

    n_rows = conn.execute("SELECT count(*) FROM usernames;").fetchall()[0][0]
    print(f"Number of Rows in usernames table: {n_rows:_}")

    conn.close()


def setup_database():
    """Initialize and populate the password database"""
    setup_pw_table()
    setup_usernames_table()


if __name__ == "__main__":
    setup_database()
