import json
from typing import List, Dict, Any

import requests


API_URL = "http://localhost:8000/validate_and_run"


SCENARIOS: List[Dict[str, Any]] = [
    {
        "name": "valid_basic",
        "description": "Valid query for first-year, first-semester students",
        "query": "SELECT name, email FROM Student WHERE year = 1 AND semester = 1",
    },
    {
        "name": "invalid_year",
        "description": "Year out of allowed range (5)",
        "query": "SELECT * FROM Student WHERE year = 5",
    },
    {
        "name": "nonexistent_table",
        "description": "Query against a table that does not exist",
        "query": "SELECT * FROM Nonexistent",
    },
    {
        "name": "sql_injection",
        "description": "Dangerous query with DROP TABLE",
        "query": "SELECT * FROM Student; DROP TABLE Student;",
    },
    {
        "name": "syntax_error",
        "description": "Incomplete WHERE clause (syntax error)",
        "query": "SELECT * FROM Student WHERE year = ",
    },
]


def explain_decision(valid: bool, checks: List[Dict[str, Any]]) -> str:
    if valid:
        return "APPROVED: all validation checks passed. Query is safe to run."

    failing = [c for c in checks if not c.get("valid")]
    if not failing:
        return "REJECTED: validator reported invalid but no specific failing checks were returned."

    reasons = []
    for check in failing:
        name = check.get("check") or "Unknown"
        msg = check.get("message") or "No details provided"
        if name == "Syntax":
            reasons.append(
                f"Syntax check failed: the database could not parse this SQL ({msg})."
            )
        elif name == "Semantics":
            reasons.append(
                "Semantics check failed: the query references tables/objects that do not exist "
                f"or are not visible in the schema ({msg})."
            )
        elif name == "Data Range":
            reasons.append(
                "Data range check failed: year/semester values are outside the allowed ranges "
                f"(year 1-4, semester 1-8) ({msg})."
            )
        elif name == "Security":
            reasons.append(
                "Security check failed: the query contains dangerous patterns (e.g. DROP, UNION, "
                f"multiple statements) and was blocked ({msg})."
            )
        elif name == "Execution":
            reasons.append(
                "Execution failed even though validation passed: the database raised an error "
                f"while running the query ({msg})."
            )
        else:
            reasons.append(f"{name} failed: {msg}")

    return "REJECTED: " + " ".join(reasons)


def call_api(query: str) -> Dict[str, Any]:
    try:
        resp = requests.post(API_URL, json={"query": query}, timeout=10)
    except Exception as e:
        return {
            "http_error": str(e),
            "http_status": None,
            "valid": False,
            "results": [],
            "rows": [],
        }

    if resp.status_code == 200:
        data = resp.json()
        return {
            "http_status": resp.status_code,
            "valid": bool(data.get("valid", False)),
            "results": data.get("results", []),
            "rows": data.get("rows", []),
        }

    # 400 with validation details
    try:
        data = resp.json()
    except Exception:
        data = {}

    detail = data.get("detail", {})
    return {
        "http_status": resp.status_code,
        "valid": bool(detail.get("valid", False)),
        "results": detail.get("results", []),
        "rows": [],
    }


def pretty_print_rows(rows: List[Dict[str, Any]], max_rows: int = 5) -> None:
    if not rows:
        print("Data rows: (none)")
        return

    print(f"Data rows (showing up to {max_rows}):")
    for i, row in enumerate(rows[:max_rows], start=1):
        print(f"  {i}. {row}")
    if len(rows) > max_rows:
        print(f"  ... ({len(rows) - max_rows} more rows not shown)")


def run_scenarios() -> None:
    for scenario in SCENARIOS:
        name = scenario["name"]
        desc = scenario["description"]
        query = scenario["query"]

        print("=" * 80)
        print(f"Scenario: {name}")
        print(f"Description: {desc}")
        print("Query:")
        print("  " + query)
        print()

        result = call_api(query)
        http_status = result.get("http_status")
        valid = result.get("valid", False)
        checks = result.get("results", [])
        rows = result.get("rows", [])

        print(f"HTTP status: {http_status}")
        print(f"Validator overall verdict: {'VALID' if valid else 'INVALID'}")
        print("Per-check results:")
        for check in checks:
            print(
                f"  - {check.get('check')}: "
                f"valid={check.get('valid')} msg={check.get('message')}"
            )

        reasoning = explain_decision(valid, checks)
        print()
        print("Decision:")
        print("  " + reasoning)
        print()

        if valid:
            pretty_print_rows(rows)
        else:
            print("Data rows: (not executed due to failed validation)")

        print()

    summary = {
        "total_scenarios": len(SCENARIOS),
    }
    print("=" * 80)
    print("Master script completed.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run_scenarios()
