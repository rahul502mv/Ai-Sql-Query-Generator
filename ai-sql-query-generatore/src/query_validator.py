"""
query_validator.py
------------------

Validates AI-generated SQL before execution.

Safety checks:
    - exactly one SQL statement
    - SELECT only
    - blocks write/destructive SQL keywords
    - blocks multiple-statement injection
    - checks referenced tables
    - asks SQLite to compile the query
    - reports useful warnings
"""

import re
import sqlite3

import sqlparse
from sqlparse.tokens import DML, Keyword, Name


BLOCKED_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "ATTACH",
    "DETACH",
    "REPLACE",
    "CREATE",
    "PRAGMA",
    "VACUUM",
    "REINDEX",
    "ANALYZE",
}


class ValidationResult:
    """Result returned by validate_sql()."""

    def __init__(
        self,
        is_valid: bool,
        errors=None,
        warnings=None,
    ):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self):
        return self.is_valid


def _extract_table_names(sql: str) -> set[str]:
    """
    Best-effort extraction of tables following FROM and JOIN.

    Handles examples such as:

        FROM customers
        FROM customers c
        JOIN orders o
        LEFT JOIN orders AS o
    """

    tables = set()

    parsed = sqlparse.parse(sql)

    if not parsed:
        return tables

    tokens = list(
        parsed[0].flatten()
    )

    for index, token in enumerate(tokens):

        if token.ttype is Keyword:

            keyword = token.value.upper()

            if keyword not in {
                "FROM",
                "JOIN",
            }:
                continue

            for next_token in tokens[index + 1:]:

                if next_token.is_whitespace:
                    continue

                if next_token.ttype is Name:

                    name = (
                        next_token.value
                        .strip("`\"[]")
                    )

                    if (
                        name
                        and name.upper()
                        not in BLOCKED_KEYWORDS
                    ):
                        tables.add(
                            name.lower()
                        )

                break

    return tables


def _get_real_tables(
    db_path: str,
) -> set[str]:

    conn = None

    try:
        conn = sqlite3.connect(
            db_path
        )

        rows = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            """
        ).fetchall()

        return {
            str(row[0]).lower()
            for row in rows
        }

    finally:

        if conn:
            conn.close()


def _contains_blocked_keyword(
    sql: str,
) -> list[str]:

    found = []

    upper_sql = sql.upper()

    for keyword in BLOCKED_KEYWORDS:

        if re.search(
            rf"\b{re.escape(keyword)}\b",
            upper_sql,
        ):
            found.append(keyword)

    return sorted(found)


def validate_sql(
    sql: str,
    db_path: str,
) -> ValidationResult:

    errors = []
    warnings = []

    if not sql or not sql.strip():

        return ValidationResult(
            False,
            ["Empty query generated."],
        )

    sql = sql.strip()

    # ---------------------------------------------------------------
    # 1. Parse SQL
    # ---------------------------------------------------------------

    statements = [
        statement
        for statement in sqlparse.parse(sql)
        if statement.token_first(
            skip_cm=True
        )
    ]

    if len(statements) != 1:

        errors.append(
            "Only one SQL statement is allowed."
        )

        return ValidationResult(
            False,
            errors,
            warnings,
        )

    statement = statements[0]

    # ---------------------------------------------------------------
    # 2. Must start with SELECT
    # ---------------------------------------------------------------

    first_token = statement.token_first(
        skip_cm=True
    )

    if (
        not first_token
        or first_token.ttype is not DML
        or first_token.value.upper()
        != "SELECT"
    ):

        errors.append(
            "Only SELECT statements are permitted."
        )

    # ---------------------------------------------------------------
    # 3. Block dangerous keywords
    # ---------------------------------------------------------------

    blocked = _contains_blocked_keyword(
        sql
    )

    for keyword in blocked:

        errors.append(
            f"Blocked SQL keyword detected: {keyword}"
        )

    # ---------------------------------------------------------------
    # 4. Prevent multiple statements
    # ---------------------------------------------------------------

    stripped = sql.rstrip(";").strip()

    if ";" in stripped:

        errors.append(
            "Multiple SQL statements are not allowed."
        )

    if errors:

        return ValidationResult(
            False,
            errors,
            warnings,
        )

    # ---------------------------------------------------------------
    # 5. Get real database tables
    # ---------------------------------------------------------------

    try:

        real_tables = _get_real_tables(
            db_path
        )

    except sqlite3.Error as exc:

        return ValidationResult(
            False,
            [
                "Could not inspect database schema: "
                f"{exc}"
            ],
        )

    # ---------------------------------------------------------------
    # 6. Check referenced tables
    # ---------------------------------------------------------------

    referenced_tables = _extract_table_names(
        sql
    )

    unknown_tables = (
        referenced_tables
        - real_tables
    )

    if unknown_tables:

        errors.append(
            "Query references unknown table(s): "
            + ", ".join(
                sorted(unknown_tables)
            )
        )

    # ---------------------------------------------------------------
    # 7. SQLite compile check
    #
    # EXPLAIN QUERY PLAN causes SQLite to parse,
    # resolve tables/columns and prepare the query.
    # It does NOT execute the SELECT.
    # ---------------------------------------------------------------

    if not errors:

        conn = None

        try:

            conn = sqlite3.connect(
                db_path
            )

            conn.execute(
                "EXPLAIN QUERY PLAN "
                + stripped
            ).fetchall()

        except sqlite3.Error as exc:

            errors.append(
                "SQLite rejected the generated query: "
                f"{exc}"
            )

        finally:

            if conn:
                conn.close()

    # ---------------------------------------------------------------
    # 8. Warnings
    # ---------------------------------------------------------------

    lower_sql = sql.lower()

    if (
        "select *" in lower_sql
        and "limit" not in lower_sql
    ):

        warnings.append(
            "The query uses SELECT * without LIMIT. "
            "This may return more data than necessary."
        )

    if (
        " order by " in lower_sql
        and "limit" not in lower_sql
    ):

        warnings.append(
            "ORDER BY is used without LIMIT. "
            "Consider limiting results when appropriate."
        )

    return ValidationResult(
        len(errors) == 0,
        errors,
        warnings,
    )


if __name__ == "__main__":

    database = "database/store.db"

    tests = [

        "SELECT * FROM customers LIMIT 10;",

        "SELECT name, city FROM customers;",

        "SELECT c.name, o.amount "
        "FROM customers c "
        "JOIN orders o "
        "ON c.customer_id = o.customer_id "
        "LIMIT 10;",

        "DROP TABLE customers;",

        "SELECT * FROM customers; "
        "DELETE FROM orders;",

        "SELECT * FROM not_a_real_table;",

        "SELECT unknown_column "
        "FROM customers;",
    ]

    for test_sql in tests:

        result = validate_sql(
            test_sql,
            database,
        )

        if result:
            status = "VALID"
        else:
            status = (
                "INVALID: "
                + "; ".join(
                    result.errors
                )
            )

        print(
            f"\n{test_sql}\n"
            f"-> {status}"
        )