import json

import requests


API_URL = "http://localhost:8000/validate"


TEST_CASES = [
    {
        "name": "valid_basic",
        "query": "SELECT name, email FROM Student WHERE year = 1 AND semester = 1",
        "expect_valid": True,
    },
    {
        "name": "invalid_year",
        "query": "SELECT * FROM Student WHERE year = 5",
        "expect_valid": False,
    },
    {
        "name": "nonexistent_table",
        "query": "SELECT * FROM Nonexistent",
        "expect_valid": False,
    },
    {
        "name": "sql_injection",
        "query": "SELECT * FROM Student; DROP TABLE Student;",
        "expect_valid": False,
    },
    {
        "name": "syntax_error",
        "query": "SELECT * FROM Student WHERE year = ",
        "expect_valid": False,
    },
]


def run_case(name: str, query: str, expect_valid: bool) -> bool:
    print(f"=== {name} ===")
    print("Query:", query)

    try:
        resp = requests.post(API_URL, json={"query": query}, timeout=10)
    except Exception as e:
        print("HTTP error:", e)
        return False

    print("HTTP status:", resp.status_code)

    if resp.status_code == 200:
        data = resp.json()
        actual_valid = bool(data.get("valid", False))
        results = data.get("results", [])
    else:
        detail = resp.json().get("detail", {})
        actual_valid = bool(detail.get("valid", False))
        results = detail.get("results", [])

    print("Expected valid:", expect_valid)
    print("Actual valid:", actual_valid)
    print("Checks:")
    for check in results:
        print(
            f"  - {check.get('check')}: "
            f"valid={check.get('valid')} msg={check.get('message')}"
        )

    success = actual_valid == expect_valid
    print("Result:", "PASS" if success else "FAIL")
    print()
    return success


def main() -> None:
    passed = 0
    failed = 0

    for case in TEST_CASES:
        ok = run_case(case["name"], case["query"], case["expect_valid"])
        if ok:
            passed += 1
        else:
            failed += 1

    summary = {
        "total": passed + failed,
        "passed": passed,
        "failed": failed,
    }

    print("=== Summary ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
