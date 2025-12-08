def match_field(
    table: str,
    column: str,
    input: str,
    ignore_case: bool = True,
    include_substring_matches: bool = False,
) -> str:
    """
    Generate a generic SQL query to match a field in a table.

    Args:
        table (str): The table name to query from.
        column (str): The column name to match against.
        input (str): The value to search for.
        ignore_case (bool): Whether to ignore case in matching.
        include_substring_matches (bool): Whether to include substring matches.
    Returns:
        str: SQL query string.
    """
    if ignore_case:
        input_expr = f"LOWER('{input}')"
        column_expr = f"LOWER({column})"
    else:
        input_expr = f"'{input}'"
        column_expr = column

    # Exact match condition
    where_clause = (
        f"{column_expr} = {input_expr}"
        if not include_substring_matches
        else f"{column_expr} LIKE '%' || {input_expr} || '%'"
    )

    sql_query = f"""
    SELECT {column}, source
    FROM {table}
    WHERE {where_clause};
    """
    return sql_query


# Create specialized functions using wrapper functions
def match_passwords(
    input: str, ignore_case: bool = True, include_substring_matches: bool = False
) -> str:
    """
    Generate SQL query to match passwords in the database.

    Args:
        input (str): The password to check.
        ignore_case (bool): Whether to ignore case in matching.
        include_substring_matches (bool): Whether to include substring matches.
    Returns:
        str: SQL query string.
    """
    return match_field(
        table="passwords",
        column="password",
        input=input,
        ignore_case=ignore_case,
        include_substring_matches=include_substring_matches,
    )


def match_usernames(
    input: str, ignore_case: bool = True, include_substring_matches: bool = False
) -> str:
    """
    Generate SQL query to match usernames in the database.

    Args:
        input (str): The username to check.
        ignore_case (bool): Whether to ignore case in matching.
        include_substring_matches (bool): Whether to include substring matches.
    Returns:
        str: SQL query string.
    """
    return match_field(
        table="usernames",
        column="username",
        input=input,
        ignore_case=ignore_case,
        include_substring_matches=include_substring_matches,
    )


def test_match_field() -> None:
    # Test exact match with ignore case
    sql = match_field(
        table="passwords",
        column="password",
        input="password123",
        ignore_case=True,
        include_substring_matches=False,
    )
    expected_sql = """
    SELECT password, source
    FROM passwords
    WHERE LOWER(password) = LOWER('password123');
    """
    assert sql.strip() == expected_sql.strip()

    # Test substring match without ignore case
    sql = match_field(
        table="passwords",
        column="password",
        input="admin",
        ignore_case=False,
        include_substring_matches=True,
    )
    expected_sql = """
    SELECT password, source
    FROM passwords
    WHERE password LIKE '%' || 'admin' || '%';
    """
    assert sql.strip() == expected_sql.strip()

    # Test substring match with ignore case
    sql = match_field(
        table="passwords",
        column="password",
        input="TestPass",
        ignore_case=True,
        include_substring_matches=True,
    )
    expected_sql = """
    SELECT password, source
    FROM passwords
    WHERE LOWER(password) LIKE '%' || LOWER('TestPass') || '%';
    """
    assert sql.strip() == expected_sql.strip()

    # Test exact match without ignore case
    sql = match_field(
        table="passwords",
        column="password",
        input="ExactMatch!",
        ignore_case=False,
        include_substring_matches=False,
    )
    expected_sql = """
    SELECT password, source
    FROM passwords
    WHERE password = 'ExactMatch!';
    """
    assert sql.strip() == expected_sql.strip()


def test_match_passwords() -> None:
    # Test using the partial function
    sql = match_passwords(
        input="password123", ignore_case=True, include_substring_matches=False
    )
    expected_sql = """
    SELECT password, source
    FROM passwords
    WHERE LOWER(password) = LOWER('password123');
    """
    assert sql.strip() == expected_sql.strip()

    sql = match_passwords(
        input="admin", ignore_case=False, include_substring_matches=True
    )
    expected_sql = """
    SELECT password, source
    FROM passwords
    WHERE password LIKE '%' || 'admin' || '%';
    """
    assert sql.strip() == expected_sql.strip()


def test_match_usernames() -> None:
    # Test using the username partial function
    sql = match_usernames(
        input="john_doe", ignore_case=True, include_substring_matches=False
    )
    expected_sql = """
    SELECT username, source
    FROM usernames
    WHERE LOWER(username) = LOWER('john_doe');
    """
    assert sql.strip() == expected_sql.strip()
