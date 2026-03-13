import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "academic.db"
SQL_PATH = BASE_DIR / "init_db.sql"


def main() -> None:
    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_PATH}")

    sql = SQL_PATH.read_text(encoding="utf-8")

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(sql)
        conn.commit()
        print(f"Database initialized at: {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
