"""
sql_generator.py
----------------
AI SQL generation using Groq.

This module:
1. Loads GROQ_API_KEY from the project-root .env file.
2. Uses an available Groq model.
3. Converts a plain-English question into SQLite SQL.
4. Returns SQL, explanation, and assumptions.
5. Provides query optimization suggestions.
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# PROJECT / ENVIRONMENT SETUP
# ============================================================

# sql_generator.py is inside:
#
# project/
#     app.py
#     .env
#     src/
#         sql_generator.py
#
# Therefore parent.parent points to the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

# Load .env explicitly.
load_dotenv(dotenv_path=ENV_FILE, override=False)


# ============================================================
# GROQ MODEL
# ============================================================

# Free-tier Groq model.
MODEL_NAME = "openai/gpt-oss-120b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an expert SQL analyst assistant embedded in a business
intelligence application.

Business users who do NOT know SQL will ask questions in plain
English about a SQLite database.

Your job is to convert the user's question into ONE safe,
read-only SQLite SELECT query.

Rules:

1. Write only one SQL SELECT statement.
2. The SQL must work with SQLite.
3. Only use tables and columns provided in the database schema.
4. Never invent table names.
5. Never invent column names.
6. Use JOIN when relationships between tables are required.
7. Use WHERE for filtering.
8. Use GROUP BY for grouped calculations.
9. Use ORDER BY when ranking or sorting is required.
10. Use LIMIT when the user asks for top/bottom N records.
11. Use SQLite-compatible date functions.
12. Never use INSERT.
13. Never use UPDATE.
14. Never use DELETE.
15. Never use DROP.
16. Never use ALTER.
17. Never use CREATE.
18. Never use PRAGMA.
19. Never return multiple SQL statements.
20. Do not use markdown code fences.

Database schema:

{schema}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "sql": "SELECT ...;",
    "explanation": "A simple 2-3 sentence explanation of what the query does.",
    "assumptions": "Any assumptions made, or an empty string."
}}
"""


# ============================================================
# API KEY / CLIENT
# ============================================================

def _get_api_key() -> str:
    """
    Load and validate the Groq API key.

    The .env file is expected at:

    project/
        .env
    """

    # Explicitly reload the project .env.
    load_dotenv(dotenv_path=ENV_FILE, override=False)

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "\n"
            "GROQ_API_KEY is not set.\n\n"
            f"Expected .env file here:\n{ENV_FILE}\n\n"
            "Create the file and add:\n\n"
            "GROQ_API_KEY=your_actual_groq_api_key\n\n"
            "Do NOT type the API key directly into PowerShell.\n"
        )

    api_key = api_key.strip()

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY exists but is empty."
        )

    return api_key


def _get_client() -> Groq:
    """
    Create and return a Groq client.
    """

    api_key = _get_api_key()

    try:
        return Groq(api_key=api_key)
    except Exception as e:
        raise RuntimeError(
            f"Could not initialize Groq client: {e}"
        ) from e


# ============================================================
# RESPONSE CLEANING
# ============================================================

def _strip_code_fences(text: str) -> str:
    """
    Remove accidental markdown code fences from the model response.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove ```json
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove ```JSON
    text = re.sub(
        r"^```JSON\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove generic ```
    text = re.sub(
        r"^```\s*",
        "",
        text,
    )

    # Remove ending ```
    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    return text.strip()


# ============================================================
# SQL SAFETY CHECK
# ============================================================

def _basic_sql_safety_check(sql: str) -> None:
    """
    Basic protection against destructive SQL returned by the model.

    The main application also has query_validator.py, but this gives
    an additional safety layer before returning generated SQL.
    """

    if not sql:
        raise RuntimeError("The model returned an empty SQL query.")

    normalized = sql.strip().lower()

    # Must start with SELECT or WITH.
    if not (
        normalized.startswith("select")
        or normalized.startswith("with")
    ):
        raise RuntimeError(
            "Generated SQL is not a read-only SELECT query."
        )

    forbidden = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "replace ",
        "truncate ",
        "attach ",
        "detach ",
        "pragma ",
    ]

    for keyword in forbidden:
        if keyword in normalized:
            raise RuntimeError(
                f"Unsafe SQL detected: {keyword.strip()}"
            )

    # Prevent multiple statements.
    # A semicolon is allowed at the end.
    without_final_semicolon = normalized.rstrip(";").strip()

    if ";" in without_final_semicolon:
        raise RuntimeError(
            "Generated SQL contains multiple SQL statements."
        )


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(question: str, schema_context: str) -> dict:
    """
    Convert a natural-language question into SQL.

    Returns:

    {
        "sql": "...",
        "explanation": "...",
        "assumptions": "..."
    }
    """

    if not question or not question.strip():
        raise RuntimeError(
            "Question cannot be empty."
        )

    if not schema_context or not schema_context.strip():
        raise RuntimeError(
            "Database schema information is empty."
        )

    client = _get_client()

    system_prompt = SYSTEM_PROMPT.format(
        schema=schema_context
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1200,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": question.strip(),
                },
            ],
        )

    except Exception as e:
        raise RuntimeError(
            f"AI service call failed: {e}"
        ) from e

    raw_text = (
        response.choices[0].message.content
        if response.choices
        else ""
    ) or ""

    cleaned = _strip_code_fences(raw_text)

    if not cleaned:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:
        parsed = json.loads(cleaned)

    except json.JSONDecodeError as e:
        raise RuntimeError(
            "Model did not return valid JSON.\n\n"
            f"Model response:\n{raw_text}\n\n"
            f"JSON error:\n{e}"
        ) from e

    # --------------------------------------------------------
    # Validate response fields
    # --------------------------------------------------------

    if not isinstance(parsed, dict):
        raise RuntimeError(
            "Model response is not a JSON object."
        )

    if "sql" not in parsed:
        raise RuntimeError(
            "Model response is missing the 'sql' field."
        )

    if "explanation" not in parsed:
        raise RuntimeError(
            "Model response is missing the 'explanation' field."
        )

    parsed.setdefault(
        "assumptions",
        "",
    )

    sql = str(parsed["sql"]).strip()

    # --------------------------------------------------------
    # Basic SQL safety
    # --------------------------------------------------------

    _basic_sql_safety_check(sql)

    # --------------------------------------------------------
    # Normalize SQL ending
    # --------------------------------------------------------

    if not sql.endswith(";"):
        sql += ";"

    parsed["sql"] = sql
    parsed["explanation"] = str(
        parsed["explanation"]
    ).strip()

    parsed["assumptions"] = str(
        parsed.get("assumptions", "")
    ).strip()

    return parsed


# ============================================================
# QUERY OPTIMIZATION
# ============================================================

def suggest_optimizations(
    sql: str,
    explain_plan: str,
) -> str:
    """
    Ask Groq to review a SQL query and its SQLite
    EXPLAIN QUERY PLAN output.
    """

    client = _get_client()

    prompt = f"""
You are a SQLite query optimization expert.

Review the following SQL query and SQLite EXPLAIN QUERY PLAN.

SQL query:
{sql}

EXPLAIN QUERY PLAN:
{explain_plan}

Provide 2-4 concise optimization suggestions.

Focus on:
- Missing indexes
- Full table scans
- Inefficient joins
- Filtering
- GROUP BY / ORDER BY efficiency
- Avoiding unnecessary columns
- Query simplification

If the query is already efficient, say that clearly.

Return plain text.
Do not generate a replacement query.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=500,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

    except Exception as e:
        raise RuntimeError(
            f"Optimization AI call failed: {e}"
        ) from e

    if not response.choices:
        return "No optimization suggestions were returned."

    return (
        response.choices[0].message.content or ""
    ).strip()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Because this file is inside src/, make sure imports
    # from other src files work when executing:
    #
    # python src/sql_generator.py
    #
    import sys

    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent)
    )

    from schema_explainer import (
        get_schema,
        schema_to_prompt_context,
    )

    print("=" * 60)
    print("AI SQL GENERATOR TEST")
    print("=" * 60)

    print(f"Project root : {PROJECT_ROOT}")
    print(f".env file    : {ENV_FILE}")
    print(f".env exists  : {ENV_FILE.exists()}")
    print(f"Model        : {MODEL_NAME}")

    api_key = os.getenv("GROQ_API_KEY")

    print(
        "API key      : "
        + (
            "LOADED"
            if api_key
            else "NOT LOADED"
        )
    )

    print("=" * 60)

    if not ENV_FILE.exists():
        raise RuntimeError(
            f".env file does not exist:\n{ENV_FILE}\n\n"
            "Create it with:\n"
            "GROQ_API_KEY=your_actual_groq_api_key"
        )

    database_path = PROJECT_ROOT / "database" / "store.db"

    if not database_path.exists():
        raise RuntimeError(
            f"Database not found:\n{database_path}"
        )

    schema = get_schema(
        str(database_path)
    )

    schema_context = schema_to_prompt_context(
        schema
    )

    question = (
        "Find customers who purchased twice "
        "but haven't purchased in 90 days."
    )

    print("Question:")
    print(question)
    print()
    print("Calling Groq...")
    print()

    result = generate_sql(
        question,
        schema_context,
    )

    print("RESULT:")
    print(
        json.dumps(
            result,
            indent=2,
        )
    )