"""
demo_frontend.py — Streamlit Web Frontend for NexusValidator

Three tabs:
  1. Try Examples  — pre-built scenarios with validation results
  2. Custom Query  — free-form SQL input with Validate / Validate & Run
  3. Pipeline Simulation — step-by-step feedback-loop walkthrough

Sidebar: database schema browser (all 12 tables with columns).

Usage:
    streamlit run demo_frontend.py
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text, inspect

# ---------------------------------------------------------------------------
# Ensure the validator module is importable
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from validator import SQLValidator  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DB_PATH = BASE_DIR / "academic.db"
DB_URI = f"sqlite:///{DB_PATH}"

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NexusValidator Demo",
    page_icon="🛡️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Cached validator
# ---------------------------------------------------------------------------
@st.cache_resource
def get_validator():
    if not DB_PATH.exists():
        st.error(
            f"Database not found at `{DB_PATH}`. "
            "Run `python init_db.py` first."
        )
        st.stop()
    return SQLValidator(DB_URI)


validator = get_validator()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def run_validation(query: str):
    """Return (is_valid, results_list)."""
    return validator.validate(query)


def execute_query(query: str) -> pd.DataFrame:
    """Execute a validated query and return a DataFrame."""
    with validator.engine.connect() as conn:
        result = conn.execute(text(query))
        columns = list(result.keys())
        rows = result.fetchall()
    return pd.DataFrame(rows, columns=columns)


def display_checks(results: list):
    """Render validation check results as coloured indicators."""
    for r in results:
        icon = "✅" if r["valid"] else "❌"
        st.markdown(f"{icon} **{r['check']}**: {r['message']}")


def get_schema_info() -> dict:
    """Return {table_name: [col_name, ...]} for sidebar browser."""
    insp = inspect(validator.engine)
    schema = {}
    for table in sorted(insp.get_table_names()):
        cols = [c["name"] for c in insp.get_columns(table)]
        schema[table] = cols
    return schema


# ---------------------------------------------------------------------------
# Sidebar — Schema Browser
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Database Schema")
    schema = get_schema_info()
    st.caption(f"{len(schema)} tables")
    for table, cols in schema.items():
        with st.expander(f"**{table}** ({len(cols)} cols)"):
            for c in cols:
                st.text(f"  • {c}")

# ---------------------------------------------------------------------------
# Main title
# ---------------------------------------------------------------------------
st.title("NexusValidator Demo")
st.caption(
    "4-layer SQL validation: Syntax → Semantics → Data Range → Security"
)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_examples, tab_custom, tab_pipeline = st.tabs(
    ["Try Examples", "Custom Query", "Pipeline Simulation"]
)

# ===================================================================
# Tab 1 — Try Examples
# ===================================================================
EXAMPLES = {
    "Valid: First-year CSE students": {
        "sql": "SELECT name, email, semester FROM Student WHERE year = 1 AND department = 'CSE'",
        "description": "Simple SELECT with valid year range and existing table.",
    },
    "Valid: Average marks per subject (semester 1)": {
        "sql": "SELECT subject_id, AVG(marks) AS avg_marks FROM Marks WHERE semester_id = 1 GROUP BY subject_id",
        "description": "Aggregation query — passes all checks.",
    },
    "Valid: Late submissions with student names": {
        "sql": (
            "SELECT s.name, a.title, sub.submitted_date, a.due_date "
            "FROM Submission sub "
            "JOIN Student s ON s.student_id = sub.student_id "
            "JOIN Assignment a ON a.assignment_id = sub.assignment_id "
            "WHERE sub.status = 'late'"
        ),
        "description": "3-table JOIN across new tables — valid query.",
    },
    "Valid: Available ECE lab equipment": {
        "sql": "SELECT name, lab_room, quantity FROM LabEquipment WHERE department = 'ECE' AND status = 'available'",
        "description": "Query on the new LabEquipment table.",
    },
    "Valid: Overdue book loans": {
        "sql": (
            "SELECT s.name, lb.title, bl.due_date "
            "FROM BookLoan bl "
            "JOIN Student s ON s.student_id = bl.student_id "
            "JOIN LibraryBook lb ON lb.book_id = bl.book_id "
            "WHERE bl.status = 'overdue'"
        ),
        "description": "JOIN across BookLoan, Student, LibraryBook.",
    },
    "Valid: Faculty list with subjects": {
        "sql": (
            "SELECT f.name, f.designation, f.department, sub.name AS subject "
            "FROM Faculty f "
            "JOIN Subjects sub ON f.subject_id = sub.subject_id"
        ),
        "description": "Faculty and their assigned subjects.",
    },
    "FAIL — Syntax: Missing FROM clause": {
        "sql": "SELECT subject_id, AVG(marks) WHERE semester_id = 1 GROUP BY subject_id",
        "description": "Missing FROM — will fail syntax check.",
    },
    "FAIL — Semantics: Non-existent table 'Books'": {
        "sql": "SELECT title, author FROM Books WHERE department = 'CSE'",
        "description": "Table 'Books' doesn't exist (it's LibraryBook).",
    },
    "FAIL — Data Range: year = 6": {
        "sql": "SELECT name, department FROM Student WHERE year = 6",
        "description": "Year must be 1-4; 6 is out of range.",
    },
    "FAIL — Security: DELETE statement": {
        "sql": "DELETE FROM Student WHERE student_id = 99",
        "description": "DELETE is a forbidden keyword.",
    },
    "FAIL — Security: SQL injection attempt": {
        "sql": "SELECT * FROM Student WHERE year = 1; DROP TABLE Student",
        "description": "Injection attempt with ';' and 'DROP'.",
    },
    "Valid: Department details": {
        "sql": "SELECT code, name, head_of_department FROM Department",
        "description": "Simple query on the Department table.",
    },
}

with tab_examples:
    selected = st.selectbox(
        "Choose a scenario:",
        list(EXAMPLES.keys()),
    )
    example = EXAMPLES[selected]
    st.info(example["description"])
    st.code(example["sql"], language="sql")

    if st.button("Validate & Run", key="ex_run"):
        is_valid, results = run_validation(example["sql"])
        display_checks(results)
        if is_valid:
            st.success("Query passed all checks.")
            df = execute_query(example["sql"])
            st.dataframe(df, use_container_width=True)
        else:
            st.error("Query blocked by validator.")

# ===================================================================
# Tab 2 — Custom Query
# ===================================================================
with tab_custom:
    st.subheader("Enter your own SQL")
    user_sql = st.text_area(
        "SQL Query",
        value="SELECT name, department FROM Student WHERE year = 2",
        height=120,
        key="custom_sql",
    )

    col1, col2 = st.columns(2)
    validate_only = col1.button("Validate Only", key="cust_validate")
    validate_run = col2.button("Validate & Run", key="cust_run")

    if validate_only or validate_run:
        if not user_sql.strip():
            st.warning("Please enter a SQL query.")
        else:
            is_valid, results = run_validation(user_sql)
            display_checks(results)
            if is_valid:
                st.success("Query is valid.")
                if validate_run:
                    try:
                        df = execute_query(user_sql)
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Execution error: {e}")
            else:
                st.error("Query blocked by validator.")

# ===================================================================
# Tab 3 — Pipeline Simulation
# ===================================================================
PIPELINE_SCENARIOS = [
    {
        "title": "Syntax Error → Feedback → Correction",
        "prompt": "Get average marks per subject",
        "steps": [
            {
                "label": "LLM generates SQL (attempt 1)",
                "sql": "SELECT subject_id, AVG(marks) WHERE semester_id = 1 GROUP BY subject_id",
                "expect_fail": True,
            },
            {
                "label": "Feedback sent to LLM",
                "feedback": "Syntax error: missing FROM clause. The table is 'Marks'. Please add FROM Marks.",
            },
            {
                "label": "LLM generates corrected SQL (attempt 2)",
                "sql": "SELECT subject_id, AVG(marks) AS avg_marks FROM Marks WHERE semester_id = 1 GROUP BY subject_id",
                "expect_fail": False,
            },
        ],
    },
    {
        "title": "Security Block → Safe Rewrite",
        "prompt": "Delete all records for student 99",
        "steps": [
            {
                "label": "LLM generates SQL (attempt 1)",
                "sql": "DELETE FROM Student WHERE student_id = 99",
                "expect_fail": True,
            },
            {
                "label": "Feedback sent to LLM",
                "feedback": "Security check failed — DELETE is forbidden. Only SELECT queries are allowed. Rephrase as a SELECT.",
            },
            {
                "label": "LLM generates safe SQL (attempt 2)",
                "sql": "SELECT COUNT(*) AS record_count FROM Student WHERE student_id = 99",
                "expect_fail": False,
            },
        ],
    },
    {
        "title": "Wrong Table + Bad Range → Double Fix",
        "prompt": "Show books borrowed by year-6 students",
        "steps": [
            {
                "label": "LLM generates SQL (attempt 1)",
                "sql": "SELECT * FROM Books b JOIN Student s ON s.student_id = b.student_id WHERE s.year = 6",
                "expect_fail": True,
            },
            {
                "label": "Feedback sent to LLM",
                "feedback": (
                    "Semantics: table 'Books' doesn't exist (use 'BookLoan' joined with 'LibraryBook'). "
                    "Data Range: year must be 1-4."
                ),
            },
            {
                "label": "LLM generates corrected SQL (attempt 2)",
                "sql": (
                    "SELECT s.name, lb.title, bl.borrow_date "
                    "FROM BookLoan bl "
                    "JOIN Student s ON s.student_id = bl.student_id "
                    "JOIN LibraryBook lb ON lb.book_id = bl.book_id "
                    "WHERE s.year = 4"
                ),
                "expect_fail": False,
            },
        ],
    },
    {
        "title": "Injection Cascade → Clean Query",
        "prompt": "Show students; DROP TABLE Student",
        "steps": [
            {
                "label": "LLM generates SQL (attempt 1)",
                "sql": "SELECT * FROM Student WHERE year = 10; DROP TABLE Student",
                "expect_fail": True,
            },
            {
                "label": "Feedback sent to LLM",
                "feedback": "Security: ';' and 'DROP' detected. Data Range: year 10 is invalid (1-4). Rewrite as clean SELECT.",
            },
            {
                "label": "LLM generates clean SQL (attempt 2)",
                "sql": "SELECT name, department FROM Student WHERE year = 4",
                "expect_fail": False,
            },
        ],
    },
]

with tab_pipeline:
    st.subheader("Pipeline Simulation")
    st.caption(
        "Step through scenarios showing the feedback loop: "
        "Prompt → LLM → Validate → Feedback → LLM → Validate → Execute"
    )

    scenario_titles = [s["title"] for s in PIPELINE_SCENARIOS]
    chosen_idx = st.selectbox(
        "Choose a pipeline scenario:",
        range(len(scenario_titles)),
        format_func=lambda i: scenario_titles[i],
        key="pipeline_select",
    )
    scenario = PIPELINE_SCENARIOS[chosen_idx]

    st.markdown(f"**User Prompt:** *\"{scenario['prompt']}\"*")

    if st.button("Run Pipeline", key="run_pipeline"):
        for step in scenario["steps"]:
            st.markdown(f"---\n**{step['label']}**")

            if "feedback" in step:
                st.warning(f"Feedback: {step['feedback']}")
                continue

            sql = step["sql"]
            st.code(sql, language="sql")

            is_valid, results = run_validation(sql)
            display_checks(results)

            if is_valid:
                st.success("All checks passed — executing query.")
                try:
                    df = execute_query(sql)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Execution error: {e}")
            else:
                st.error("Validation failed — sending feedback to LLM.")
