"""
app.py
------

AI SQL Query Generator + Data Explainer.

Flow:

Business question
        ↓
Groq AI
        ↓
Generated SQL
        ↓
SQL validation
        ↓
SQLite execution
        ↓
Results
        ↓
Business insight
        ↓
Optimization suggestions

Run:

    python -m streamlit run app.py
"""

import os
import sqlite3
import sys
import time
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv


# ---------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

SRC_DIR = BASE_DIR / "src"

DATABASE_DIR = BASE_DIR / "database"

DB_PATH = DATABASE_DIR / "store.db"


# Make src modules importable
if str(SRC_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIR),
    )


# ---------------------------------------------------------------
# Imports from project
# ---------------------------------------------------------------

from schema_explainer import (
    get_schema,
    schema_to_plain_english,
    schema_to_prompt_context,
)

from query_validator import (
    validate_sql,
)

from sql_generator import (
    generate_sql,
    suggest_optimizations,
)

from insights_generator import (
    generate_insight,
)


# ---------------------------------------------------------------
# Environment
# ---------------------------------------------------------------

load_dotenv(
    BASE_DIR / ".env"
)


# ---------------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------------

st.set_page_config(
    page_title="AI SQL Query Generator",
    page_icon="🧠",
    layout="wide",
)


# ---------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------

def database_exists() -> bool:
    return DB_PATH.exists()


def get_database_connection():
    return sqlite3.connect(
        str(DB_PATH)
    )


# ---------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------

with st.sidebar:

    st.title(
        "🧠 AI SQL Query Generator"
    )

    st.caption(
        "Ask questions about your business data "
        "in plain English."
    )

    # -----------------------------------------------------------
    # Database check
    # -----------------------------------------------------------

    if not database_exists():

        st.error(
            "Database not found."
        )

        st.code(
            "python database/create_db.py"
        )

        st.stop()

    # -----------------------------------------------------------
    # Schema
    # -----------------------------------------------------------

    st.subheader(
        "📋 Database schema"
    )

    try:

        schema_tables = get_schema(
            str(DB_PATH)
        )

        schema_description = (
            schema_to_plain_english(
                schema_tables
            )
        )

        st.markdown(
            schema_description
        )

    except Exception as exc:

        st.error(
            "Could not read database schema."
        )

        st.exception(exc)

        st.stop()

    # -----------------------------------------------------------
    # Example questions
    # -----------------------------------------------------------

    st.divider()

    st.subheader(
        "💡 Example questions"
    )

    examples = [

        "Find customers who purchased twice but haven't purchased in 90 days.",

        "What is the total revenue by city?",

        "Which 5 customers spent the most money overall?",

        "How many orders were cancelled or refunded in the last 60 days?",

        "Show monthly order volume for the last 6 months.",

    ]

    for example in examples:

        if st.button(
            example,
            use_container_width=True,
        ):

            st.session_state[
                "question"
            ] = example

    # -----------------------------------------------------------
    # API status
    # -----------------------------------------------------------

    st.divider()

    if os.environ.get(
        "GROQ_API_KEY"
    ):

        st.success(
            "Groq API key loaded."
        )

    else:

        st.warning(
            "GROQ_API_KEY is missing. "
            "Add it to your .env file."
        )


# ---------------------------------------------------------------
# Main application
# ---------------------------------------------------------------

st.title(
    "Ask a question about your data"
)

st.write(
    "Type a business question and the AI will "
    "generate SQL, validate it, execute it, "
    "and explain the results."
)


question = st.text_input(
    "Your question",
    placeholder=(
        "e.g. What is the total revenue by city?"
    ),
    key="question",
)


run = st.button(
    "Generate & Run ▶",
    type="primary",
)


# ---------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------

if run:

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

        st.stop()

    # -----------------------------------------------------------
    # Schema context
    # -----------------------------------------------------------

    schema_context = (
        schema_to_prompt_context(
            schema_tables
        )
    )

    # ===========================================================
    # STEP 1 - Generate SQL
    # ===========================================================

    st.subheader(
        "1️⃣ Generated SQL"
    )

    with st.spinner(
        "AI is writing the SQL query..."
    ):

        try:

            start_time = time.time()

            result = generate_sql(
                question,
                schema_context,
            )

            generation_time = (
                time.time()
                - start_time
            )

        except RuntimeError as exc:

            st.error(
                "❌ SQL generation failed"
            )

            st.error(
                str(exc)
            )

            st.stop()

        except Exception as exc:

            st.error(
                "❌ Unexpected AI error"
            )

            st.exception(exc)

            st.stop()

    sql = result[
        "sql"
    ].strip()

    st.code(
        sql,
        language="sql",
    )

    st.caption(
        f"Generated in "
        f"{generation_time:.1f} seconds"
    )

    # ===========================================================
    # STEP 2 - Explanation
    # ===========================================================

    st.subheader(
        "2️⃣ Query explanation"
    )

    st.write(
        result[
            "explanation"
        ]
    )

    assumptions = (
        result.get(
            "assumptions",
            "",
        )
        or ""
    ).strip()

    if assumptions:

        st.info(
            f"**Assumptions:** "
            f"{assumptions}"
        )

    # ===========================================================
    # STEP 3 - Validation
    # ===========================================================

    st.subheader(
        "3️⃣ Validation"
    )

    validation = validate_sql(
        sql,
        str(DB_PATH),
    )

    if not validation.is_valid:

        st.error(
            "❌ Query failed validation."
        )

        for error in validation.errors:

            st.error(
                f"• {error}"
            )

        st.stop()

    st.success(
        "✅ Query passed safety and schema checks."
    )

    for warning in validation.warnings:

        st.warning(
            f"⚠️ {warning}"
        )

    # ===========================================================
    # STEP 4 - Execute SQL
    # ===========================================================

    st.subheader(
        "4️⃣ Results"
    )

    conn = None

    try:

        conn = get_database_connection()

        df = pd.read_sql_query(
            sql,
            conn,
        )

    except sqlite3.Error as exc:

        st.error(
            "❌ SQL execution failed."
        )

        st.error(
            str(exc)
        )

        st.stop()

    except Exception as exc:

        st.error(
            "❌ Could not load query results."
        )

        st.exception(exc)

        st.stop()

    finally:

        if conn is not None:

            conn.close()

    # -----------------------------------------------------------
    # Display results
    # -----------------------------------------------------------

    if df.empty:

        st.info(
            "The query executed successfully, "
            "but no matching rows were found."
        )

    else:

        st.dataframe(
            df,
            use_container_width=True,
        )

    st.caption(
        f"{len(df)} row(s) returned."
    )

    # ===========================================================
    # STEP 5 - Business insight
    # ===========================================================

    st.subheader(
        "5️⃣ Business insights"
    )

    if not os.environ.get(
        "GROQ_API_KEY"
    ):

        st.info(
            "Add GROQ_API_KEY to .env "
            "to generate AI business insights."
        )

    else:

        with st.spinner(
            "AI is analyzing the results..."
        ):

            try:

                rows = list(
                    df.itertuples(
                        index=False,
                        name=None,
                    )
                )

                insight = generate_insight(
                    question=question,
                    sql=sql,
                    columns=list(
                        df.columns
                    ),
                    rows=rows,
                )

                st.write(
                    insight
                )

            except RuntimeError as exc:

                st.error(
                    "❌ Business insight generation failed."
                )

                st.error(
                    str(exc)
                )

            except Exception as exc:

                st.error(
                    "❌ Unexpected insight error."
                )

                st.exception(exc)

    # ===========================================================
    # STEP 6 - Optimization
    # ===========================================================

    with st.expander(
        "⚙️ Advanced: validation & optimization"
    ):

        st.subheader(
            "SQLite query plan"
        )

        plan_conn = None

        try:

            plan_conn = (
                get_database_connection()
            )

            plan_rows = (
                plan_conn.execute(
                    "EXPLAIN QUERY PLAN "
                    + sql.rstrip(";")
                ).fetchall()
            )

            plan_text = "\n".join(
                str(row)
                for row in plan_rows
            )

            if plan_text:

                st.code(
                    plan_text,
                    language="text",
                )

            else:

                st.info(
                    "No query plan details available."
                )

        except sqlite3.Error as exc:

            st.warning(
                "Could not generate query plan: "
                f"{exc}"
            )

            plan_text = ""

        finally:

            if plan_conn is not None:

                plan_conn.close()

        # -------------------------------------------------------
        # AI optimization
        # -------------------------------------------------------

        if (
            os.environ.get(
                "GROQ_API_KEY"
            )
            and plan_text
        ):

            st.subheader(
                "AI optimization suggestions"
            )

            with st.spinner(
                "AI is checking for optimization opportunities..."
            ):

                try:

                    tips = suggest_optimizations(
                        sql,
                        plan_text,
                    )

                    st.write(
                        tips
                    )

                except RuntimeError as exc:

                    st.error(
                        str(exc)
                    )

                except Exception as exc:

                    st.exception(
                        exc
                    )

elif not run:

    st.info(
        "Enter a question above and click "
        "**Generate & Run ▶**."
    )