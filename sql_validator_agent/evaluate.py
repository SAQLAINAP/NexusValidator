import json
from typing import List, Dict

import requests


API_URL = "http://localhost:8000/validate"


CANDIDATE_QUERIES: List[str] = [
    # Valid queries
    "SELECT name, email FROM Student WHERE year = 1 AND semester = 1",
    "SELECT s.name, m.marks FROM Student s JOIN Marks m ON s.student_id = m.student_id WHERE s.year = 2",
    "SELECT * FROM Subjects WHERE credits = 4",
    "SELECT * FROM Semester WHERE year IN (1, 2)",
    "SELECT t.day, t.time, sub.name FROM Timetable t JOIN Subjects sub ON t.subject_id = sub.subject_id WHERE t.semester_id = 3",
    # Data range issues
    "SELECT * FROM Student WHERE year = 5",
    "SELECT * FROM Semester WHERE semester IN (0, 9)",
    # Nonexistent table
    "SELECT * FROM Nonexistent",
    # Syntax error
    "SELECT * FROM Student WHERE year = ",
    # SQL injection / dangerous
    "SELECT * FROM Student; DROP TABLE Student;",
]


def call_validator(query: str) -> Dict:
    payload = {"query": query}
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
    except Exception as e:
        return {
            "query": query,
            "http_error": str(e),
            "valid": False,
            "results": [],
        }

    if resp.status_code == 200:
        data = resp.json()
        return {
            "query": query,
            "http_status": resp.status_code,
            "valid": data.get("valid", False),
            "results": data.get("results", []),
        }
    else:
        try:
            data = resp.json()
        except Exception:
            data = {}
        detail = data.get("detail", {})
        return {
            "query": query,
            "http_status": resp.status_code,
            "valid": detail.get("valid", False),
            "results": detail.get("results", []),
        }


def main() -> None:
    all_results: List[Dict] = []
    valid_count = 0
    invalid_count = 0

    for idx, query in enumerate(CANDIDATE_QUERIES, start=1):
        result = call_validator(query)
        all_results.append(result)

        is_valid = result.get("valid", False)
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1

        print(f"=== Query {idx} ===")
        print(query)
        print(f"HTTP status: {result.get('http_status')}")
        print(f"Valid: {is_valid}")
        print("Checks:")
        for check in result.get("results", []):
            print(f"  - {check.get('check')}: valid={check.get('valid')} msg={check.get('message')}")
        print()

    summary = {
        "total": len(CANDIDATE_QUERIES),
        "valid": valid_count,
        "invalid": invalid_count,
    }

    print("=== Summary ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
