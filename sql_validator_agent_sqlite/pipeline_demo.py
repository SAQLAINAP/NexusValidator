"""
pipeline_demo.py — CLI Pipeline Simulation for NexusValidator

Demonstrates the full prompt → LLM → validate → feedback → re-validate → execute
pipeline using 8 scenarios.  Imports SQLValidator directly (no server needed).

Usage:
    python pipeline_demo.py
"""

import sys
from pathlib import Path
from sqlalchemy import text

from validator import SQLValidator

# ---------------------------------------------------------------------------
# Optional: rich for coloured output; plain-text fallback
# ---------------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.table import Table as RichTable

    console = Console()

    def heading(msg: str):
        console.rule(f"[bold cyan]{msg}[/bold cyan]")

    def label(tag: str, msg: str):
        colours = {
            "USER PROMPT": "bold green",
            "LLM": "bold yellow",
            "VALIDATOR": "bold magenta",
            "FEEDBACK → LLM": "bold red",
            "EXECUTE": "bold blue",
            "RESULT": "bold white",
        }
        style = colours.get(tag, "bold")
        console.print(f"  [{style}][{tag}][/{style}]  {msg}")

    def check_line(name: str, passed: bool, message: str):
        icon = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        console.print(f"    {icon}  {name}: {message}")

    def show_rows(columns, rows):
        if not rows:
            console.print("    (no rows returned)")
            return
        t = RichTable(show_lines=False)
        for c in columns:
            t.add_column(str(c))
        for row in rows[:15]:
            t.add_row(*[str(v) for v in row])
        if len(rows) > 15:
            t.add_row(*["..." for _ in columns])
        console.print(t)

    RICH = True

except ImportError:
    RICH = False

    def heading(msg: str):
        width = 60
        print("\n" + "=" * width)
        print(f"  {msg}")
        print("=" * width)

    def label(tag: str, msg: str):
        print(f"  [{tag}]  {msg}")

    def check_line(name: str, passed: bool, message: str):
        icon = "PASS" if passed else "FAIL"
        print(f"    {icon}  {name}: {message}")

    def show_rows(columns, rows):
        if not rows:
            print("    (no rows returned)")
            return
        header = " | ".join(str(c) for c in columns)
        print(f"    {header}")
        print(f"    {'-' * len(header)}")
        for row in rows[:15]:
            print(f"    {' | '.join(str(v) for v in row)}")
        if len(rows) > 15:
            print(f"    ... ({len(rows)} rows total)")


# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "academic.db"
DB_URI = f"sqlite:///{DB_PATH}"

if not DB_PATH.exists():
    print(f"ERROR: Database not found at {DB_PATH}")
    print("Run `python init_db.py` first.")
    sys.exit(1)

validator = SQLValidator(DB_URI)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def validate_and_show(query: str) -> bool:
    """Validate a query, print check results, return True if valid."""
    is_valid, results = validator.validate(query)
    for r in results:
        check_line(r["check"], r["valid"], r["message"])
    return is_valid


def execute_query(query: str):
    """Execute a validated query and print the result rows."""
    with validator.engine.connect() as conn:
        result = conn.execute(text(query))
        columns = list(result.keys())
        rows = result.fetchall()
    label("RESULT", f"{len(rows)} row(s) returned")
    show_rows(columns, rows)


def run_scenario(num: int, title: str, prompt: str, attempts):
    """
    Run one demo scenario.

    attempts: list of dicts with keys:
        - sql:      the SQL the simulated LLM generates
        - feedback: (optional) the feedback message sent back to the LLM
    The last attempt should pass validation (or we show the failure).
    """
    heading(f"Scenario {num}: {title}")
    label("USER PROMPT", prompt)
    print()

    for i, attempt in enumerate(attempts, 1):
        sql = attempt["sql"]
        is_retry = i > 1

        if is_retry:
            label("FEEDBACK → LLM", attempt.get("feedback", "Fix the query."))
            print()

        tag = "LLM" if not is_retry else "LLM"
        label(tag, f"(attempt {i}) {sql}")

        label("VALIDATOR", "Running 4-check validation …")
        passed = validate_and_show(sql)
        print()

        if passed:
            label("EXECUTE", "Query passed all checks — executing …")
            execute_query(sql)
            break
        else:
            if i == len(attempts):
                label("EXECUTE", "Final attempt still invalid — query blocked.")
    print()


# ---------------------------------------------------------------------------
# 8 Scenarios
# ---------------------------------------------------------------------------
SCENARIOS = [
    # 1 — Valid first try
    {
        "title": "Valid first try — first-year CSE students",
        "prompt": "Show me all first-year CSE students",
        "attempts": [
            {
                "sql": (
                    "SELECT name, email, semester "
                    "FROM Student "
                    "WHERE year = 1 AND department = 'CSE'"
                ),
            },
        ],
    },
    # 2 — Syntax error → fix
    {
        "title": "Syntax error → LLM corrects",
        "prompt": "Get average marks per subject",
        "attempts": [
            {
                "sql": (
                    "SELECT subject_id, AVG(marks) "
                    "WHERE semester_id = 1 "
                    "GROUP BY subject_id"
                ),
                "feedback": (
                    "Syntax error — missing FROM clause. "
                    "The table is 'Marks'. Please add FROM Marks."
                ),
            },
            {
                "sql": (
                    "SELECT subject_id, AVG(marks) AS avg_marks "
                    "FROM Marks "
                    "WHERE semester_id = 1 "
                    "GROUP BY subject_id"
                ),
            },
        ],
    },
    # 3 — Data range fail → fix
    {
        "title": "Data range violation → LLM adjusts",
        "prompt": "Show students in year 6",
        "attempts": [
            {
                "sql": "SELECT name, department FROM Student WHERE year = 6",
                "feedback": (
                    "Data range check failed — year must be 1-4. "
                    "There is no year 6. Use year = 4 for final-year students."
                ),
            },
            {
                "sql": "SELECT name, department FROM Student WHERE year = 4",
            },
        ],
    },
    # 4 — Security block → fix
    {
        "title": "Security block → LLM pivots to safe query",
        "prompt": "Delete all records for student 99",
        "attempts": [
            {
                "sql": "DELETE FROM Student WHERE student_id = 99",
                "feedback": (
                    "Security check failed — DELETE is a forbidden keyword. "
                    "Only SELECT queries are allowed. "
                    "Rephrase as a SELECT to show the student's data instead."
                ),
            },
            {
                "sql": (
                    "SELECT COUNT(*) AS record_count "
                    "FROM Student WHERE student_id = 99"
                ),
            },
        ],
    },
    # 5 — Semantics fail → fix
    {
        "title": "Wrong table name → LLM corrects",
        "prompt": "Show all library books in the CSE department",
        "attempts": [
            {
                "sql": (
                    "SELECT title, author FROM Books "
                    "WHERE department = 'CSE'"
                ),
                "feedback": (
                    "Semantics check failed — table 'Books' does not exist. "
                    "The correct table name is 'LibraryBook'."
                ),
            },
            {
                "sql": (
                    "SELECT title, author, copies_available "
                    "FROM LibraryBook "
                    "WHERE department = 'CSE'"
                ),
            },
        ],
    },
    # 6 — Valid complex JOIN
    {
        "title": "Complex JOIN — late submissions",
        "prompt": "Which students submitted assignments late?",
        "attempts": [
            {
                "sql": (
                    "SELECT s.name, a.title, sub.submitted_date, a.due_date "
                    "FROM Submission sub "
                    "JOIN Student s ON s.student_id = sub.student_id "
                    "JOIN Assignment a ON a.assignment_id = sub.assignment_id "
                    "WHERE sub.status = 'late'"
                ),
            },
        ],
    },
    # 7 — Valid new-table query
    {
        "title": "Lab equipment availability",
        "prompt": "Show available lab equipment in the ECE department",
        "attempts": [
            {
                "sql": (
                    "SELECT name, lab_room, quantity "
                    "FROM LabEquipment "
                    "WHERE department = 'ECE' AND status = 'available'"
                ),
            },
        ],
    },
    # 8 — Multi-error cascade
    {
        "title": "Multi-error cascade — injection + bad range",
        "prompt": "Show students in year 10; DROP TABLE Student",
        "attempts": [
            {
                "sql": (
                    "SELECT * FROM Student WHERE year = 10; "
                    "DROP TABLE Student"
                ),
                "feedback": (
                    "Security check failed — forbidden keywords detected "
                    "(';', 'DROP'). Also, year 10 is out of range (must be 1-4). "
                    "Rewrite as a clean SELECT with a valid year."
                ),
            },
            {
                "sql": "SELECT name, department FROM Student WHERE year = 4",
            },
        ],
    },
]


def main():
    if RICH:
        console.print(
            "\n[bold cyan]NexusValidator — CLI Pipeline Demo[/bold cyan]"
        )
        console.print(
            "Simulates: User Prompt → LLM SQL → Validate → "
            "Feedback → Re-validate → Execute\n"
        )
    else:
        print("\nNexusValidator — CLI Pipeline Demo")
        print(
            "Simulates: User Prompt → LLM SQL → Validate → "
            "Feedback → Re-validate → Execute\n"
        )

    for i, scenario in enumerate(SCENARIOS, 1):
        run_scenario(
            num=i,
            title=scenario["title"],
            prompt=scenario["prompt"],
            attempts=scenario["attempts"],
        )

    if RICH:
        console.rule("[bold green]All 8 scenarios complete[/bold green]")
    else:
        print("=" * 60)
        print("  All 8 scenarios complete")
        print("=" * 60)


if __name__ == "__main__":
    main()
