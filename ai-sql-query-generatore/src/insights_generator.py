"""
insights_generator.py
---------------------

Converts SQL query results into a short,
business-friendly explanation.
"""

import os

from groq import Groq


MODEL_NAME = "openai/gpt-oss-120b"


def _get_client() -> Groq:
    """Create Groq client."""

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set."
        )

    return Groq(api_key=api_key)


def generate_insight(
    question: str,
    sql: str,
    columns: list[str],
    rows: list[tuple],
) -> str:
    """
    Convert SQL results into a business insight.
    """

    if not question.strip():
        raise RuntimeError(
            "Original question is empty."
        )

    client = _get_client()

    preview_rows = rows[:20]

    if columns:
        table_preview = " | ".join(
            str(column)
            for column in columns
        )
    else:
        table_preview = "(no columns)"

    if preview_rows:

        table_preview += "\n"

        table_preview += "\n".join(
            " | ".join(
                str(value)
                for value in row
            )
            for row in preview_rows
        )

    else:
        table_preview += "\n(no rows returned)"

    prompt = f"""
You are a business data analyst.

A business user asked:

"{question}"

The following SQL query was executed:

{sql}

The query returned {len(rows)} row(s).

Here is a preview of the results:

{table_preview}

Write a short business insight.

Requirements:

1. Directly answer the original question.
2. Highlight the most important number or pattern.
3. Explain the result in simple business language.
4. Suggest ONE concrete next action.
5. Write 3-5 sentences.
6. Do not explain SQL.
7. Do not discuss programming.
8. Do not invent numbers.
9. Only use numbers visible in the results.
10. If there are no rows, clearly explain that no matching data was found.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
            max_tokens=500,
        )

    except Exception as exc:
        raise RuntimeError(
            "AI business insight request failed.\n\n"
            f"Model: {MODEL_NAME}\n"
            f"Error: {exc}"
        ) from exc

    if not response.choices:
        raise RuntimeError(
            "AI returned no business insight."
        )

    insight = (
        response.choices[0]
        .message
        .content
        or ""
    ).strip()

    if not insight:
        raise RuntimeError(
            "AI returned an empty business insight."
        )

    return insight