# Nexus SQL Validator

**Nexus SQL Validator** is an intelligent microservice suite built to validate and score SQL queries against complex academic schema requirements. This repository contains the building blocks for an autonomous validation feedback loop designed to empower large language models (LLMs) to natively debug and hone their SQL generations.

---

## Overview

The validation framework runs a given SQL query through a gauntlet of four separate tests:

1. **Syntax Checking**: Uses the backend database's native `EXPLAIN` to catch parsing errors.
2. **Schema Semantics**: Parses the query's AST to guarantee that all referenced tables and aliases exist within the live target database.
3. **Business Logic & Data Ranges**: Enforces custom constraints (e.g., student years must fall between 1 and 4, semesters between 1 and 8).
4. **Security & Heuristics**: Applies static analysis to block obvious SQL injections (`DROP`, `--`, `1=1`), ensuring the validation environment remains safe from destructive queries.

---

## Repository Structure

```
NexusValidator/
├── sql_validator_agent/           # PostgreSQL version
│   ├── app.py                     # FastAPI REST API (port 8000)
│   ├── validator.py               # 4-layer SQL validator
│   ├── evaluate.py                # Evaluation harness
│   ├── init_db.sql                # Schema + seed data
│   ├── test_validator.py          # Pytest suite
│   └── requirements.txt
├── sql_validator_agent_sqlite/    # SQLite version (recommended for local use)
│   ├── app.py                     # FastAPI REST API (port 8000)
│   ├── validator.py               # 4-layer SQL validator
│   ├── demo_frontend.py           # FastAPI web frontend (port 8080)
│   ├── pipeline_demo.py           # CLI pipeline simulation
│   ├── init_db.py                 # Database initializer
│   ├── init_db.sql                # Schema + seed data (12 tables, ~330 rows)
│   ├── test_validator.py          # Pytest suite
│   └── requirements.txt
├── WIKI.md                        # Detailed documentation
└── README.md
```

- **[`/sql_validator_agent`](./sql_validator_agent/)** — The **PostgreSQL** version. Ideal for production stacks.
- **[`/sql_validator_agent_sqlite`](./sql_validator_agent_sqlite/)** — The lightweight **SQLite** version. Runs locally with zero external database setup.
- **[`WIKI.md`](./WIKI.md)** — Comprehensive documentation with sequence diagrams and architecture notes.

---

## Quick Start (SQLite version)

### 1. Install dependencies

```bash
cd sql_validator_agent_sqlite
pip install -r requirements.txt
```

### 2. Initialize the database

```bash
python init_db.py
```

This creates `academic.db` with 12 tables and ~330 rows of sample academic data.

### 3. Run

You have three ways to interact with the validator:

#### Web Frontend (recommended)

```bash
python demo_frontend.py
```

Open **http://localhost:8080** in your browser. The frontend provides:

- **Try Examples** — 12 pre-built scenarios covering valid queries, syntax errors, semantic failures, data range violations, and security blocks
- **Custom Query** — Write your own SQL with Validate Only / Validate & Run buttons
- **Pipeline Simulation** — Step-by-step animated walkthroughs showing the LLM feedback loop (Prompt → SQL → Validate → Feedback → Correct → Execute)
- **Schema Browser** — Collapsible sidebar listing all 12 tables and their columns

#### REST API

```bash
python app.py
```

API available at **http://localhost:8000** with two endpoints:

```bash
# Validate only
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT name FROM Student WHERE year = 1"}'

# Validate and execute
curl -X POST http://localhost:8000/validate_and_run \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT name FROM Student WHERE year = 1"}'
```

#### CLI Pipeline Demo

```bash
python pipeline_demo.py
```

Runs 8 scenarios in the terminal showing the full feedback loop with coloured output (via `rich`).

### 4. Run tests

```bash
python -m pytest test_validator.py -v
```

---

## Quick Start (PostgreSQL version)

```bash
cd sql_validator_agent
pip install -r requirements.txt
# Set up your PostgreSQL database and load init_db.sql
python app.py
```

See [`WIKI.md`](./WIKI.md) for detailed PostgreSQL configuration instructions.

---

## API Reference

### `POST /validate`

Validates a SQL query without executing it.

**Request:**
```json
{ "query": "SELECT name FROM Student WHERE year = 1" }
```

**Response (valid):**
```json
{
  "valid": true,
  "message": "Query is valid",
  "results": [
    { "check": "Syntax", "valid": true, "message": "Syntax valid" },
    { "check": "Semantics", "valid": true, "message": "Semantics valid" },
    { "check": "Data Range", "valid": true, "message": "Data range valid" },
    { "check": "Security", "valid": true, "message": "Security valid" }
  ]
}
```

### `POST /validate_and_run`

Validates and executes the query, returning result rows on success.

---

## License

See [LICENSE](./LICENSE) for details.
