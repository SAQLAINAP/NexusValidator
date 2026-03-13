# Nexus SQL Validator

**Nexus SQL Validator** is an intelligent microservice suite built to validate and score SQL queries against complex academic schema requirements. This repository contains the building blocks for an autonomous validation feedback loop designed to empower large language models (LLMs) to natively debug and hone their SQL generations.

---

## 🚀 Overview

The validation framework runs a given SQL query through a gauntlet of four separate tests:

1. **Syntax Checking**: Uses the backend database's native `EXPLAIN` to catch parsing errors.
2. **Schema Semantics**: Parses the query's AST to guarantee that all referenced tables and aliases exist within the live target database.
3. **Business Logic & Data Ranges**: Enforces custom constraints (e.g., student years must fall between 1 and 4, semesters between 1 and 8).
4. **Security & Heuristics**: Applies static analysis to block obvious SQL injections (`DROP`, `--`, `1=1`), ensuring the validation environment remains safe from destructive queries.

---

## 📁 Repository Structure

The code is divided into two distinct backend flavors. Both operate with identical validation flows but cater to different deployment needs:

- **[`/sql_validator_agent`](./sql_validator_agent/)**
  The robust **PostgreSQL** version. Ideal if you are integrating the validator into an existing, heavy-duty production stack.
  
- **[`/sql_validator_agent_sqlite`](./sql_validator_agent_sqlite/)**
  The lightweight **SQLite** version. Operates completely in-memory or via local `.db` files. Perfect for local testing, CI/CD pipelines, or environments where installing PostgreSQL is overkill.
  
- **[`WIKI.md`](./WIKI.md)**
  Comprehensive documentation on how to configure your databases, initialize the schema, execute the REST APIs, and hook the validator into larger generation pipelines (complete with sequence diagrams).

---

## ⚡ Quick Start

### 1. Choose your engine
Navigate to the directory of your preferred backend:

```bash
# For PostgreSQL
cd sql_validator_agent

# For SQLite
cd sql_validator_agent_sqlite
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the schema & run
Follow the specific instructions inside the subfolder's `README.md` or the root `WIKI.md` to feed the `init_db.sql` schema into your database, then start the FastAPI service:

```bash
python app.py
```

### 4. Validate
The API will be available at `http://localhost:8000/validate`. You can submit queries and evaluate exactly why they passed or fail:

```json
{
  "query": "SELECT * FROM Student WHERE year = 1 AND semester = 1"
}
```

*For an in-depth dive into the architecture and API responses, see the [WIKI](WIKI.md).*
