# NexusValidator — Product Requirements Document & Handoff Reference

> **Version:** 1.0
> **Date:** March 2026
> **Repository:** `SAQLAINAP/NexusValidator`
> **License:** GNU General Public License v3.0

---

## 1. Executive Summary

NexusValidator is a multi-layered SQL validation microservice designed to act as a programmatic guardrail between Large Language Model (LLM) query generators and live relational databases. It intercepts generated SQL, subjects it to four sequential validation checks (syntax, schema semantics, business-rule data ranges, and security heuristics), and returns structured, machine-readable feedback that an LLM agent can consume to iteratively self-correct its output.

The system operates on a synthetic academic-domain database and is shipped in two backend variants — PostgreSQL (production-grade) and SQLite (zero-config local use) — both exposing identical FastAPI REST interfaces.

---

## 2. Problem Statement

When LLMs generate SQL from natural-language prompts, the resulting queries frequently contain:

- **Syntactic errors** — malformed clauses, missing keywords.
- **Semantic mistakes** — references to tables or columns that do not exist in the target schema.
- **Business-logic violations** — literal values outside the domain's valid ranges (e.g., `year = 6` in a four-year degree programme).
- **Security hazards** — destructive statements (`DROP`, `DELETE`), injection patterns (`;`, `--`, `UNION`).

Without an automated validation layer, these errors either crash at execution time or, worse, silently corrupt data. NexusValidator provides the structured feedback loop that enables an LLM to detect, understand, and fix each class of error before the query ever reaches the database.

---

## 3. Core Validation Pipeline

Every SQL query passes through four checks executed **in strict sequential order**. Validation halts at the first failure and returns all results accumulated up to that point, so the consumer always knows which layer rejected the query and why.

| Layer | Check | Technique | Failure Example |
|-------|-------|-----------|-----------------|
| 1 | **Syntax** | Executes `EXPLAIN <query>` against the live database engine. If the engine cannot parse the statement, it is syntactically invalid. | `SELECT name WHERE year = 1` (missing `FROM`) |
| 2 | **Schema Semantics** | Parses the query AST via `sqlparse`, extracts identifier tokens, and cross-references them against `SQLAlchemy`'s reflected `MetaData`. At least one referenced table must exist. | `SELECT * FROM Books` (table is `LibraryBook`) |
| 3 | **Data Range** | Regex extraction of `year = <n>`, `semester = <n>`, and `IN (...)` clauses. Year must be 1-4; semester must be 1-8. | `WHERE year = 6` |
| 4 | **Security** | Case-insensitive substring scan for forbidden tokens: `drop`, `delete`, `insert`, `update`, `union`, `exec`, `--`, `;`. | `SELECT *; DROP TABLE Student` |

### Validation Response Schema

```json
{
  "valid": true | false,
  "results": [
    {
      "check": "Syntax | Semantics | Data Range | Security",
      "valid": true | false,
      "message": "<human-readable explanation>"
    }
  ]
}
```

When `valid` is `false`, the `results` array contains entries only up to and including the first failing check. This early-exit design gives the LLM the most actionable, non-redundant feedback possible.

---

## 4. Prerequisite Data — Academic Database Schema

The validator operates on a synthetic academic institution database. The SQLite variant ships with **12 tables** and approximately **330 rows** of seed data; the PostgreSQL variant contains the original **5 core tables** with the same student/marks/timetable data.

### 4.1 Entity-Relationship Summary

#### Core Tables (both variants)

| Table | Primary Key | Key Columns | Row Count | Purpose |
|-------|------------|-------------|-----------|---------|
| `Student` | `student_id` | `name`, `email`, `year` (1-4), `semester` (1-8), `department` | 25 | Student roster across 6 departments |
| `Semester` | `semester_id` | `year`, `semester`, `start_date`, `end_date` | 8 | Academic calendar (4 years x 2 semesters) |
| `Subjects` | `subject_id` | `name`, `semester_id` (FK), `credits` | 20 | Course catalogue |
| `Marks` | `mark_id` | `student_id` (FK), `subject_id` (FK), `marks`, `grade`, `semester_id` (FK) | 50 | Grade records |
| `Timetable` | `timetable_id` | `semester_id` (FK), `day`, `time`, `subject_id` (FK), `room` | 20 | Class scheduling |

#### Extended Tables (SQLite variant only)

| Table | Primary Key | Key Columns | Row Count | Purpose |
|-------|------------|-------------|-----------|---------|
| `Department` | `department_id` | `code`, `name`, `head_of_department`, `established_year` | 6 | Department directory (CSE, AIML, ECE, IT, MECH, CIVIL) |
| `Faculty` | `faculty_id` | `name`, `email`, `department` (FK), `designation`, `subject_id` (FK) | 15 | Teaching staff linked to departments and subjects |
| `Assignment` | `assignment_id` | `title`, `subject_id` (FK), `semester_id` (FK), `type`, `max_marks`, `due_date` | 30 | Homework, labs, and projects |
| `Submission` | `submission_id` | `student_id` (FK), `assignment_id` (FK), `submitted_date`, `marks_obtained`, `status` | 80 | Student work submissions (on_time / late / missing) |
| `LibraryBook` | `book_id` | `title`, `author`, `isbn`, `department`, `copies_total`, `copies_available` | 25 | Library catalogue |
| `BookLoan` | `loan_id` | `student_id` (FK), `book_id` (FK), `borrow_date`, `due_date`, `return_date`, `status` | 40 | Loan tracking (active / returned / overdue) |
| `LabEquipment` | `equipment_id` | `name`, `department`, `lab_room`, `quantity`, `status` | 20 | Lab inventory (available / in_use / maintenance) |

### 4.2 Domain Constraints

- `Student.year`: `CHECK (year BETWEEN 1 AND 4)`
- `Student.semester`: `CHECK (semester BETWEEN 1 AND 8)`
- `Assignment.type`: `CHECK (type IN ('homework', 'project', 'lab'))`
- `Submission.status`: `CHECK (status IN ('on_time', 'late', 'missing'))`
- `BookLoan.status`: `CHECK (status IN ('active', 'returned', 'overdue'))`
- `LabEquipment.status`: `CHECK (status IN ('available', 'in_use', 'maintenance'))`

### 4.3 Database Initialisation

```bash
# SQLite (recommended for local development)
cd sql_validator_agent_sqlite
python init_db.py          # Creates academic.db from init_db.sql

# PostgreSQL
cd sql_validator_agent
createdb -U <user> academic_db
psql -U <user> -d academic_db -f init_db.sql
```

The SQLite `init_db.sql` is idempotent — it runs `DROP TABLE IF EXISTS` in reverse dependency order before recreating all tables.

---

## 5. System Architecture

### 5.1 Repository Structure

```
NexusValidator/
├── sql_validator_agent/                # PostgreSQL variant
│   ├── validator.py                    # SQLValidator class (4-layer pipeline)
│   ├── app.py                          # FastAPI REST API (port 8000)
│   ├── evaluate.py                     # Batch evaluation harness (10 test queries)
│   ├── init_db.sql                     # Schema + seed data (5 tables)
│   ├── test_validator.py               # Pytest suite (5 assertions)
│   └── requirements.txt                # fastapi, uvicorn, sqlparse, sqlalchemy, psycopg2-binary, pytest, requests
│
├── sql_validator_agent_sqlite/         # SQLite variant (primary development target)
│   ├── validator.py                    # SQLValidator class (identical logic)
│   ├── app.py                          # FastAPI REST API (port 8000)
│   ├── demo_frontend.py               # FastAPI web frontend with inlined HTML/CSS/JS SPA (port 8080)
│   ├── pipeline_demo.py               # CLI pipeline simulation (8 scenarios, rich output)
│   ├── init_db.py                      # Python database initialiser
│   ├── init_db.sql                     # Schema + seed data (12 tables, ~330 rows)
│   ├── test_validator.py               # Pytest suite (5 assertions)
│   └── requirements.txt                # fastapi, uvicorn, sqlparse, sqlalchemy, pytest, requests, rich
│
├── README.md                           # Quick-start guide
├── WIKI.md                             # Architecture documentation with Mermaid diagrams
├── PRD.md                              # This document
├── LICENSE                             # GNU GPL v3.0
└── .gitignore
```

### 5.2 Component Dependency Graph

```
                  ┌─────────────────────────────┐
                  │       Web Browser            │
                  │   http://localhost:8080       │
                  └──────────────┬────────────────┘
                                 │ HTTP (fetch)
                  ┌──────────────▼────────────────┐
                  │      demo_frontend.py          │
                  │   FastAPI + Inlined HTML SPA   │
                  │   Endpoints:                   │
                  │     GET  /                      │
                  │     GET  /api/schema            │
                  │     POST /api/validate          │
                  │     POST /api/validate_and_run  │
                  └──────────────┬────────────────┘
                                 │ Python import
                  ┌──────────────▼────────────────┐
                  │         validator.py            │
                  │        SQLValidator             │
                  │   validate_syntax()             │
                  │   validate_semantics()          │
                  │   validate_data_range()         │
                  │   validate_security()           │
                  └──────────┬──────────┬──────────┘
                   sqlparse  │          │  SQLAlchemy
                             │          │
                  ┌──────────▼──────────▼──────────┐
                  │       academic.db / PostgreSQL   │
                  │       (12 or 5 tables)           │
                  └─────────────────────────────────┘
```

`app.py` follows the same dependency path but runs independently on port 8000 and exposes `/validate` and `/validate_and_run` without a UI.

### 5.3 LLM Feedback Loop (Conceptual)

```
    User Prompt
         │
         ▼
   ┌───────────┐     SQL string     ┌────────────────┐
   │  LLM Agent │ ─────────────────► │  NexusValidator │
   └─────┬─────┘                     └───────┬────────┘
         │                                    │
         │   ◄── JSON feedback ───────────────┘
         │   (check name, pass/fail, message)
         │
         ▼
   If invalid: revise query and resubmit
   If valid:   execute against database
```

The pipeline demonstration (`pipeline_demo.py` and the Pipeline Simulation tab in the web frontend) walks through this loop with scripted scenarios showing how an LLM would receive feedback and self-correct across multiple attempts.

---

## 6. Features

### 6.1 REST API (`app.py` — port 8000)

| Endpoint | Method | Request Body | Response |
|----------|--------|-------------|----------|
| `/validate` | POST | `{"query": "<SQL>"}` | `{"valid": bool, "message": str, "results": [...]}` |
| `/validate_and_run` | POST | `{"query": "<SQL>"}` | Same as above, plus `"rows": [...]` on success |

The `/validate` endpoint returns an HTTP 400 with the failure details in the response body when validation fails. The `/validate_and_run` endpoint additionally executes valid queries and returns the result set as an array of row-objects.

### 6.2 Web Frontend (`demo_frontend.py` — port 8080)

A self-contained single-page application served as an inlined HTML/CSS/JS response from FastAPI. No external JavaScript frameworks or CDN dependencies.

**Tab 1 — Try Examples**
- Dropdown of 12 pre-built scenarios covering all four failure modes and six valid query patterns (simple SELECT, aggregation, multi-table JOIN, library queries, faculty queries, lab equipment queries).
- Each scenario displays a description, the SQL in a monospace block, and a "Validate & Run" button.
- Results render as PASS/FAIL badge rows with a data table for successful queries.

**Tab 2 — Custom Query**
- Free-form SQL textarea with a default placeholder query.
- Two action buttons: "Validate Only" (checks without executing) and "Validate & Run" (checks then executes).

**Tab 3 — Pipeline Simulation**
- Dropdown of 4 multi-step scenarios (syntax error correction, security block rewrite, wrong table + bad range double fix, injection cascade cleanup).
- "Run Pipeline" triggers an animated step-by-step reveal with 500ms delays between steps.
- Each step shows: the SQL attempt, live validation results, feedback messages (styled as warning boxes), and final execution with data tables.

**Sidebar — Schema Browser**
- Loaded from `/api/schema` on page load.
- Collapsible panel listing all tables with expandable column lists.
- Toggle button to show/hide.

**Visual Design**
- Dark theme: `#1a1a2e` background, `#16213e` cards, `#0f3460` borders, `#00d2ff` accent.
- Green (`#34d399`) PASS badges, red (`#f87171`) FAIL badges.
- Monospace SQL blocks, striped data tables, smooth CSS transitions and keyframe animations.

### 6.3 CLI Pipeline Demo (`pipeline_demo.py`)

Terminal-based simulation of 8 LLM feedback-loop scenarios with coloured output via the `rich` library (graceful plain-text fallback if `rich` is not installed). Scenarios include:

1. Valid first try (first-year CSE students)
2. Syntax error then correction
3. Data range violation then adjustment
4. Security block then pivot to safe query
5. Wrong table name then correction
6. Complex valid JOIN (late submissions)
7. Valid new-table query (lab equipment)
8. Multi-error cascade (injection + bad range)

### 6.4 Batch Evaluator (`evaluate.py` — PostgreSQL variant only)

Loops through 10 candidate queries against the running `/validate` endpoint and prints per-query results with a final valid/invalid tally. Intended for regression testing during development.

### 6.5 Test Suite (`test_validator.py`)

Five pytest assertions covering the critical paths:

| Test | Input | Expected |
|------|-------|----------|
| `test_valid_query` | Valid multi-table JOIN with year=1 | `is_valid = True` |
| `test_invalid_year` | `year = 5` | `is_valid = False` |
| `test_sql_injection` | `SELECT *; DROP TABLE Student;` | `is_valid = False` |
| `test_nonexistent_table` | `SELECT * FROM Nonexistent` | `is_valid = False` |
| `test_syntax_error` | `WHERE year = ` (incomplete) | `is_valid = False` |

---

## 7. Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.9+ | All application code |
| Web Framework | FastAPI | REST API and web frontend server |
| ASGI Server | Uvicorn | Production-capable async server |
| SQL Parsing | sqlparse | AST extraction for semantic analysis |
| ORM / DB Reflection | SQLAlchemy | Schema reflection, `EXPLAIN` execution, query execution |
| DB (option A) | PostgreSQL + psycopg2 | Production database backend |
| DB (option B) | SQLite | Zero-config local database |
| Data Validation | Pydantic | Request body validation (via FastAPI) |
| Testing | pytest | Unit test framework |
| CLI Formatting | rich | Coloured terminal output for pipeline demo |
| Frontend | Vanilla HTML/CSS/JS | Single-page application (no build step, no npm) |

---

## 8. Setup & Execution Reference

### 8.1 Prerequisites

- Python 3.9 or later
- `pip` package manager
- (PostgreSQL variant only) PostgreSQL server with `psql` CLI

### 8.2 SQLite Variant (Recommended)

```bash
cd sql_validator_agent_sqlite
pip install -r requirements.txt
python init_db.py
```

#### Run the web frontend
```bash
python demo_frontend.py
# Open http://localhost:8080
```

#### Run the REST API (headless)
```bash
python app.py
# API at http://localhost:8000
```

#### Run the CLI pipeline demo
```bash
python pipeline_demo.py
```

#### Run tests
```bash
python -m pytest test_validator.py -v
```

### 8.3 PostgreSQL Variant

```bash
cd sql_validator_agent
pip install -r requirements.txt
createdb -U <user> academic_db
psql -U <user> -d academic_db -f init_db.sql
```

Update the `DB_URI` in `app.py` and `test_validator.py` with your credentials, then:

```bash
python app.py                          # API at http://localhost:8000
python evaluate.py                     # Batch evaluation (requires running server)
python -m pytest test_validator.py -v  # Unit tests
```

---

## 9. API Reference

### POST `/validate`

Validates a SQL query without executing it.

**Request:**
```json
{ "query": "SELECT name FROM Student WHERE year = 1" }
```

**Success Response (200):**
```json
{
  "valid": true,
  "message": "Query is valid",
  "results": [
    { "check": "Syntax",     "valid": true, "message": "Syntax valid" },
    { "check": "Semantics",  "valid": true, "message": "Semantics valid" },
    { "check": "Data Range", "valid": true, "message": "Data range valid" },
    { "check": "Security",   "valid": true, "message": "Security valid" }
  ]
}
```

**Failure Response (400):**
```json
{
  "detail": {
    "valid": false,
    "results": [
      { "check": "Data Range", "valid": false, "message": "Invalid year value (must be 1-4)" }
    ]
  }
}
```

### POST `/validate_and_run`

Validates and, on success, executes the query.

**Success Response (200):**
```json
{
  "valid": true,
  "results": [ ... ],
  "columns": ["name", "department"],
  "rows": [
    { "name": "Alice", "department": "CSE" },
    { "name": "Laura", "department": "CSE" }
  ]
}
```

### GET `/api/schema` (web frontend only)

Returns the full database schema as a JSON object.

**Response:**
```json
{
  "Assignment": ["assignment_id", "title", "subject_id", ...],
  "BookLoan": ["loan_id", "student_id", "book_id", ...],
  "Student": ["student_id", "name", "email", "year", "semester", "department"],
  ...
}
```

---

## 10. Known Limitations & Scope Boundaries

1. **Semantic check granularity.** The current semantic validator confirms that at least one referenced table exists. It does not validate individual column names or alias resolution at the AST level; column-level errors surface only at the syntax/EXPLAIN layer.

2. **Data range checks are regex-based.** The validator inspects literal values in `WHERE year = <n>` and `IN (...)` patterns. It does not evaluate computed expressions, subqueries, or parameterised bindings.

3. **Security layer is heuristic.** The forbidden-keyword scan is a static substring match, not a full SQL injection analysis. It blocks common dangerous patterns but is not a substitute for parameterised queries in production.

4. **Read-only enforcement.** The security layer blocks `INSERT`, `UPDATE`, `DELETE`, and `DROP` by keyword matching. It does not use database-level permissions or read-only transactions.

5. **Single-database scope.** The validator reflects one database at startup. Cross-database or cross-schema queries are not supported.

6. **No authentication.** The REST API and web frontend have no access control. They are intended for local development and demonstration use.

---

## 11. Glossary

| Term | Definition |
|------|-----------|
| **Validation Layer** | One of the four sequential checks (Syntax, Semantics, Data Range, Security) applied to each query |
| **Early Exit** | The pipeline stops at the first failing layer and returns results up to that point |
| **Feedback Loop** | The iterative cycle where a validator's structured error output is fed back to an LLM for query correction |
| **Schema Reflection** | SQLAlchemy's runtime introspection of the database's tables, columns, and constraints |
| **Pipeline Scenario** | A scripted multi-step demonstration showing an LLM generating incorrect SQL, receiving feedback, and producing a corrected query |
| **SPA** | Single-Page Application; the web frontend is served as one HTML response with inlined CSS and JavaScript |

---

## 12. Contact & Contribution

- **Repository:** [github.com/SAQLAINAP/NexusValidator](https://github.com/SAQLAINAP/NexusValidator)
- **Issues:** File via GitHub Issues
- **License:** GNU General Public License v3.0 — see `LICENSE` for full terms
