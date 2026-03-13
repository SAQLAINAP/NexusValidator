import pytest

from validator import SQLValidator


validator = SQLValidator("postgresql://user:password@localhost:5432/academic_db")  # TODO: update credentials


def test_valid_query():
    query = (
        "SELECT s.name, m.marks FROM Student s "
        "JOIN Marks m ON s.student_id = m.student_id "
        "WHERE s.year = 1 AND s.semester = 1"
    )
    is_valid, _ = validator.validate(query)
    assert is_valid


def test_invalid_year():
    query = "SELECT * FROM Student WHERE year = 5"
    is_valid, _ = validator.validate(query)
    assert not is_valid


def test_sql_injection():
    query = "SELECT * FROM Student; DROP TABLE Student;"
    is_valid, _ = validator.validate(query)
    assert not is_valid


def test_nonexistent_table():
    query = "SELECT * FROM Nonexistent"
    is_valid, _ = validator.validate(query)
    assert not is_valid


def test_syntax_error():
    query = "SELECT * FROM Student WHERE year = "
    is_valid, _ = validator.validate(query)
    assert not is_valid
