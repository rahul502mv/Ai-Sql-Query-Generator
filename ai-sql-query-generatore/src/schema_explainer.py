"""
schema_explainer.py
-------------------

Reads the SQLite database schema and creates:

1. Structured schema information.
2. Compact schema context for the AI.
3. Plain-English schema description for Streamlit users.
"""

import sqlite3
from dataclasses import dataclass, field


@dataclass
class ColumnInfo:
    name: str
    type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: str = ""


@dataclass
class TableInfo:
    name: str
    columns: list[ColumnInfo] = field(
        default_factory=list
    )
    row_count: int = 0


def _quote_identifier(name: str) -> str:
    """
    Safely quote a SQLite identifier.
    """

    return '"' + name.replace(
        '"',
        '""'
    ) + '"'


def get_schema(
    db_path: str,
) -> list[TableInfo]:

    conn = sqlite3.connect(
        db_path
    )

    try:

        cursor = conn.cursor()

        table_rows = cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        tables = []

        for (
            table_name,
        ) in table_rows:

            quoted_table = (
                _quote_identifier(
                    table_name
                )
            )

            # Foreign keys
            foreign_keys = {}

            fk_rows = cursor.execute(
                f"PRAGMA foreign_key_list({quoted_table})"
            ).fetchall()

            for row in fk_rows:

                # SQLite PRAGMA foreign_key_list:
                # id, seq, table, from, to, on_update,
                # on_delete, match, ...
                column_name = row[3]
                referenced_table = row[2]
                referenced_column = row[4]

                foreign_keys[
                    column_name
                ] = (
                    f"{referenced_table}."
                    f"{referenced_column}"
                )

            # Columns
            column_rows = cursor.execute(
                f"PRAGMA table_info({quoted_table})"
            ).fetchall()

            columns = []

            for row in column_rows:

                column_name = row[1]
                column_type = row[2]

                columns.append(
                    ColumnInfo(
                        name=column_name,
                        type=column_type,
                        is_primary_key=bool(
                            row[5]
                        ),
                        is_foreign_key=(
                            column_name
                            in foreign_keys
                        ),
                        references=foreign_keys.get(
                            column_name,
                            "",
                        ),
                    )
                )

            row_count = cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM {quoted_table}
                """
            ).fetchone()[0]

            tables.append(
                TableInfo(
                    name=table_name,
                    columns=columns,
                    row_count=row_count,
                )
            )

        return tables

    finally:

        conn.close()


def schema_to_prompt_context(
    tables: list[TableInfo],
) -> str:

    lines = []

    for table in tables:

        column_descriptions = []

        for column in table.columns:

            tags = []

            if column.is_primary_key:
                tags.append("PK")

            if column.is_foreign_key:
                tags.append(
                    f"FK -> {column.references}"
                )

            tag_text = ""

            if tags:
                tag_text = (
                    " ["
                    + ", ".join(tags)
                    + "]"
                )

            column_descriptions.append(
                f"{column.name} "
                f"({column.type})"
                f"{tag_text}"
            )

        lines.append(
            f"Table {table.name} "
            f"({table.row_count} rows): "
            + ", ".join(
                column_descriptions
            )
        )

    return "\n".join(lines)


def schema_to_plain_english(
    tables: list[TableInfo],
) -> str:

    if not tables:

        return (
            "No application tables were found "
            "in the database."
        )

    output = []

    for table in tables:

        primary_key = next(
            (
                column.name
                for column in table.columns
                if column.is_primary_key
            ),
            "id",
        )

        foreign_keys = [
            column
            for column in table.columns
            if column.is_foreign_key
        ]

        description = (
            f"**{table.name}** — "
            f"contains {table.row_count} records. "
            f"Each row is identified by "
            f"`{primary_key}`."
        )

        if foreign_keys:

            links = ", ".join(
                f"`{column.name}` → "
                f"`{column.references}`"
                for column in foreign_keys
            )

            description += (
                " It connects to other tables "
                f"through {links}."
            )

        column_names = ", ".join(
            f"`{column.name}`"
            for column in table.columns
        )

        description += (
            f" Available columns: "
            f"{column_names}."
        )

        output.append(
            description
        )

    return "\n\n".join(output)


if __name__ == "__main__":

    database = "database/store.db"

    schema = get_schema(
        database
    )

    print(
        "--- AI Schema Context ---"
    )

    print(
        schema_to_prompt_context(
            schema
        )
    )

    print(
        "\n--- Business Explanation ---"
    )

    print(
        schema_to_plain_english(
            schema
        )
    )