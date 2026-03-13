"""
demo_frontend.py — FastAPI Web Frontend for NexusValidator

Three tabs:
  1. Try Examples  — pre-built scenarios with validation results
  2. Custom Query  — free-form SQL input with Validate / Validate & Run
  3. Pipeline Simulation — step-by-step feedback-loop walkthrough

Sidebar: collapsible database schema browser (all 12 tables with columns).

Usage:
    python demo_frontend.py
    # Open http://localhost:8080
"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import inspect, text

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

if not DB_PATH.exists():
    print(f"ERROR: Database not found at {DB_PATH}")
    print("Run `python init_db.py` first.")
    sys.exit(1)

validator = SQLValidator(DB_URI)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="NexusValidator Demo")


class QueryRequest(BaseModel):
    query: str


@app.get("/api/schema")
def get_schema():
    """Return {table: [col, ...]} for sidebar browser."""
    insp = inspect(validator.engine)
    schema = {}
    for table in sorted(insp.get_table_names()):
        cols = [c["name"] for c in insp.get_columns(table)]
        schema[table] = cols
    return schema


@app.post("/api/validate")
def api_validate(req: QueryRequest):
    is_valid, results = validator.validate(req.query)
    return {"valid": is_valid, "results": results}


@app.post("/api/validate_and_run")
def api_validate_and_run(req: QueryRequest):
    is_valid, results = validator.validate(req.query)
    if not is_valid:
        return {"valid": False, "results": results, "rows": []}

    try:
        with validator.engine.connect() as conn:
            result = conn.execute(text(req.query))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        results.append({"check": "Execution", "valid": False, "message": str(e)})
        return {"valid": False, "results": results, "rows": []}

    return {"valid": True, "results": results, "rows": rows, "columns": columns}


# ---------------------------------------------------------------------------
# Inlined HTML / CSS / JS frontend
# ---------------------------------------------------------------------------
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NexusValidator Demo</title>
<style>
/* ---- reset & base ---- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #1a1a2e;
  color: #e0e0e0;
  min-height: 100vh;
  display: flex;
}

/* ---- sidebar ---- */
.sidebar {
  width: 280px;
  min-width: 280px;
  background: #16213e;
  border-right: 1px solid #0f3460;
  padding: 20px 16px;
  overflow-y: auto;
  transition: margin-left .3s;
  position: relative;
}
.sidebar.collapsed { margin-left: -280px; }
.sidebar h2 { font-size: 15px; color: #00d2ff; margin-bottom: 6px; letter-spacing: .5px; }
.sidebar .table-count { font-size: 12px; color: #888; margin-bottom: 14px; }
.schema-table { margin-bottom: 6px; }
.schema-table summary {
  cursor: pointer;
  font-size: 13px;
  padding: 6px 8px;
  border-radius: 6px;
  background: #1a1a2e;
  transition: background .2s;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 6px;
}
.schema-table summary:hover { background: #0f3460; }
.schema-table summary::before { content: '\25B6'; font-size: 9px; color: #00d2ff; transition: transform .2s; }
.schema-table[open] summary::before { transform: rotate(90deg); }
.schema-table .col-list { padding: 4px 0 4px 24px; }
.schema-table .col-list div {
  font-size: 12px;
  color: #aaa;
  padding: 2px 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

/* ---- toggle button ---- */
.sidebar-toggle {
  position: fixed;
  left: 280px;
  top: 12px;
  z-index: 100;
  background: #0f3460;
  border: 1px solid #00d2ff;
  color: #00d2ff;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: left .3s;
}
.sidebar-toggle.shifted { left: 12px; }

/* ---- main ---- */
.main {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  max-height: 100vh;
}

/* ---- header ---- */
.header h1 { font-size: 26px; color: #fff; margin-bottom: 4px; }
.header h1 span { color: #00d2ff; }
.header p { font-size: 13px; color: #888; margin-bottom: 20px; }

/* ---- tabs ---- */
.tabs { display: flex; gap: 0; margin-bottom: 24px; border-bottom: 2px solid #0f3460; }
.tab-btn {
  background: transparent;
  border: none;
  color: #888;
  font-size: 14px;
  padding: 10px 20px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color .2s, border-color .2s;
}
.tab-btn:hover { color: #ccc; }
.tab-btn.active { color: #00d2ff; border-bottom-color: #00d2ff; }

.tab-content { display: none; }
.tab-content.active { display: block; }

/* ---- cards ---- */
.card {
  background: #16213e;
  border: 1px solid #0f3460;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 16px;
}

/* ---- selects, textareas, buttons ---- */
select, textarea {
  width: 100%;
  background: #1a1a2e;
  border: 1px solid #0f3460;
  color: #e0e0e0;
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  outline: none;
  transition: border-color .2s;
}
select:focus, textarea:focus { border-color: #00d2ff; }
textarea { resize: vertical; min-height: 100px; }
label { font-size: 13px; color: #aaa; display: block; margin-bottom: 6px; }

.btn-row { display: flex; gap: 10px; margin-top: 12px; }
button.btn {
  padding: 10px 22px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity .2s, transform .05s;
}
button.btn:active { transform: scale(.97); }
button.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn-primary { background: #00d2ff; color: #1a1a2e; }
.btn-secondary { background: #0f3460; color: #e0e0e0; }
.btn-primary:hover:not(:disabled) { opacity: .85; }
.btn-secondary:hover:not(:disabled) { opacity: .85; }

/* ---- sql block ---- */
.sql-block {
  background: #0d1b2a;
  border: 1px solid #0f3460;
  border-radius: 6px;
  padding: 12px 14px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: #76c7f0;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 8px 0;
}

/* ---- description ---- */
.description {
  font-size: 13px;
  color: #aaa;
  background: #0d1b2a;
  border-left: 3px solid #00d2ff;
  padding: 8px 12px;
  border-radius: 0 6px 6px 0;
  margin: 8px 0;
}

/* ---- badges ---- */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}
.badge-pass { background: #064e3b; color: #34d399; }
.badge-fail { background: #7f1d1d; color: #f87171; }

/* ---- checks list ---- */
.checks { margin: 12px 0; }
.check-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid #0f346044;
}
.check-item:last-child { border-bottom: none; }

/* ---- overall verdict ---- */
.verdict {
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  margin: 10px 0;
}
.verdict-pass { background: #064e3b55; border: 1px solid #34d399; color: #34d399; }
.verdict-fail { background: #7f1d1d55; border: 1px solid #f87171; color: #f87171; }

/* ---- data table ---- */
.data-table-wrap { overflow-x: auto; margin: 12px 0; }
table.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
table.data-table th {
  background: #0f3460;
  color: #00d2ff;
  padding: 8px 12px;
  text-align: left;
  font-weight: 600;
  white-space: nowrap;
}
table.data-table td {
  padding: 7px 12px;
  border-bottom: 1px solid #0f346044;
  white-space: nowrap;
}
table.data-table tr:nth-child(even) td { background: #1a1a2e44; }
table.data-table tr:hover td { background: #0f346033; }

/* ---- pipeline ---- */
.pipeline-step {
  opacity: 0;
  transform: translateY(12px);
  animation: fadeUp .4s forwards;
  margin-bottom: 14px;
}
@keyframes fadeUp {
  to { opacity: 1; transform: translateY(0); }
}
.step-label {
  font-size: 13px;
  font-weight: 600;
  color: #00d2ff;
  margin-bottom: 6px;
}
.feedback-box {
  background: #332800;
  border: 1px solid #fbbf24;
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 13px;
  color: #fbbf24;
}

/* ---- spinner ---- */
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #0f3460;
  border-top-color: #00d2ff;
  border-radius: 50%;
  animation: spin .6s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ---- prompt label ---- */
.prompt-label {
  font-size: 14px;
  color: #ccc;
  margin: 10px 0 6px;
}
.prompt-label em { color: #fbbf24; font-style: italic; }

/* ---- scrollbar ---- */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #16213e; }
::-webkit-scrollbar-thumb { background: #0f3460; border-radius: 3px; }
</style>
</head>
<body>

<!-- Sidebar -->
<aside class="sidebar" id="sidebar">
  <h2>DATABASE SCHEMA</h2>
  <div class="table-count" id="tableCount"></div>
  <div id="schemaList"></div>
</aside>

<button class="sidebar-toggle" id="sidebarToggle" title="Toggle schema sidebar">&#9776;</button>

<!-- Main -->
<div class="main">
  <div class="header">
    <h1><span>Nexus</span>Validator Demo</h1>
    <p>4-layer SQL validation: Syntax &rarr; Semantics &rarr; Data Range &rarr; Security</p>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab-btn active" data-tab="examples">Try Examples</button>
    <button class="tab-btn" data-tab="custom">Custom Query</button>
    <button class="tab-btn" data-tab="pipeline">Pipeline Simulation</button>
  </div>

  <!-- Tab 1: Try Examples -->
  <div class="tab-content active" id="tab-examples">
    <div class="card">
      <label>Choose a scenario:</label>
      <select id="exampleSelect"></select>
      <div class="description" id="exampleDesc"></div>
      <div class="sql-block" id="exampleSql"></div>
      <div class="btn-row">
        <button class="btn btn-primary" id="exampleRunBtn">Validate &amp; Run</button>
      </div>
    </div>
    <div id="exampleResults"></div>
  </div>

  <!-- Tab 2: Custom Query -->
  <div class="tab-content" id="tab-custom">
    <div class="card">
      <label>SQL Query:</label>
      <textarea id="customSql">SELECT name, department FROM Student WHERE year = 2</textarea>
      <div class="btn-row">
        <button class="btn btn-secondary" id="customValidateBtn">Validate Only</button>
        <button class="btn btn-primary" id="customRunBtn">Validate &amp; Run</button>
      </div>
    </div>
    <div id="customResults"></div>
  </div>

  <!-- Tab 3: Pipeline Simulation -->
  <div class="tab-content" id="tab-pipeline">
    <div class="card">
      <label>Choose a pipeline scenario:</label>
      <select id="pipelineSelect"></select>
      <div class="btn-row">
        <button class="btn btn-primary" id="pipelineRunBtn">Run Pipeline</button>
      </div>
    </div>
    <div id="pipelineResults"></div>
  </div>
</div>

<script>
// ======================= DATA =======================
const EXAMPLES = [
  {
    label: "Valid: First-year CSE students",
    sql: "SELECT name, email, semester FROM Student WHERE year = 1 AND department = 'CSE'",
    description: "Simple SELECT with valid year range and existing table."
  },
  {
    label: "Valid: Average marks per subject (semester 1)",
    sql: "SELECT subject_id, AVG(marks) AS avg_marks FROM Marks WHERE semester_id = 1 GROUP BY subject_id",
    description: "Aggregation query \u2014 passes all checks."
  },
  {
    label: "Valid: Late submissions with student names",
    sql: "SELECT s.name, a.title, sub.submitted_date, a.due_date FROM Submission sub JOIN Student s ON s.student_id = sub.student_id JOIN Assignment a ON a.assignment_id = sub.assignment_id WHERE sub.status = 'late'",
    description: "3-table JOIN across new tables \u2014 valid query."
  },
  {
    label: "Valid: Available ECE lab equipment",
    sql: "SELECT name, lab_room, quantity FROM LabEquipment WHERE department = 'ECE' AND status = 'available'",
    description: "Query on the new LabEquipment table."
  },
  {
    label: "Valid: Overdue book loans",
    sql: "SELECT s.name, lb.title, bl.due_date FROM BookLoan bl JOIN Student s ON s.student_id = bl.student_id JOIN LibraryBook lb ON lb.book_id = bl.book_id WHERE bl.status = 'overdue'",
    description: "JOIN across BookLoan, Student, LibraryBook."
  },
  {
    label: "Valid: Faculty list with subjects",
    sql: "SELECT f.name, f.designation, f.department, sub.name AS subject FROM Faculty f JOIN Subjects sub ON f.subject_id = sub.subject_id",
    description: "Faculty and their assigned subjects."
  },
  {
    label: "FAIL \u2014 Syntax: Missing FROM clause",
    sql: "SELECT subject_id, AVG(marks) WHERE semester_id = 1 GROUP BY subject_id",
    description: "Missing FROM \u2014 will fail syntax check."
  },
  {
    label: "FAIL \u2014 Semantics: Non-existent table 'Books'",
    sql: "SELECT title, author FROM Books WHERE department = 'CSE'",
    description: "Table 'Books' doesn't exist (it's LibraryBook)."
  },
  {
    label: "FAIL \u2014 Data Range: year = 6",
    sql: "SELECT name, department FROM Student WHERE year = 6",
    description: "Year must be 1\u20134; 6 is out of range."
  },
  {
    label: "FAIL \u2014 Security: DELETE statement",
    sql: "DELETE FROM Student WHERE student_id = 99",
    description: "DELETE is a forbidden keyword."
  },
  {
    label: "FAIL \u2014 Security: SQL injection attempt",
    sql: "SELECT * FROM Student WHERE year = 1; DROP TABLE Student",
    description: "Injection attempt with ';' and 'DROP'."
  },
  {
    label: "Valid: Department details",
    sql: "SELECT code, name, head_of_department FROM Department",
    description: "Simple query on the Department table."
  }
];

const PIPELINE_SCENARIOS = [
  {
    title: "Syntax Error \u2192 Feedback \u2192 Correction",
    prompt: "Get average marks per subject",
    steps: [
      { label: "LLM generates SQL (attempt 1)", sql: "SELECT subject_id, AVG(marks) WHERE semester_id = 1 GROUP BY subject_id", expect_fail: true },
      { label: "Feedback sent to LLM", feedback: "Syntax error: missing FROM clause. The table is 'Marks'. Please add FROM Marks." },
      { label: "LLM generates corrected SQL (attempt 2)", sql: "SELECT subject_id, AVG(marks) AS avg_marks FROM Marks WHERE semester_id = 1 GROUP BY subject_id", expect_fail: false }
    ]
  },
  {
    title: "Security Block \u2192 Safe Rewrite",
    prompt: "Delete all records for student 99",
    steps: [
      { label: "LLM generates SQL (attempt 1)", sql: "DELETE FROM Student WHERE student_id = 99", expect_fail: true },
      { label: "Feedback sent to LLM", feedback: "Security check failed \u2014 DELETE is forbidden. Only SELECT queries are allowed. Rephrase as a SELECT." },
      { label: "LLM generates safe SQL (attempt 2)", sql: "SELECT COUNT(*) AS record_count FROM Student WHERE student_id = 99", expect_fail: false }
    ]
  },
  {
    title: "Wrong Table + Bad Range \u2192 Double Fix",
    prompt: "Show books borrowed by year-6 students",
    steps: [
      { label: "LLM generates SQL (attempt 1)", sql: "SELECT * FROM Books b JOIN Student s ON s.student_id = b.student_id WHERE s.year = 6", expect_fail: true },
      { label: "Feedback sent to LLM", feedback: "Semantics: table 'Books' doesn't exist (use 'BookLoan' joined with 'LibraryBook'). Data Range: year must be 1\u20144." },
      { label: "LLM generates corrected SQL (attempt 2)", sql: "SELECT s.name, lb.title, bl.borrow_date FROM BookLoan bl JOIN Student s ON s.student_id = bl.student_id JOIN LibraryBook lb ON lb.book_id = bl.book_id WHERE s.year = 4", expect_fail: false }
    ]
  },
  {
    title: "Injection Cascade \u2192 Clean Query",
    prompt: "Show students; DROP TABLE Student",
    steps: [
      { label: "LLM generates SQL (attempt 1)", sql: "SELECT * FROM Student WHERE year = 10; DROP TABLE Student", expect_fail: true },
      { label: "Feedback sent to LLM", feedback: "Security: ';' and 'DROP' detected. Data Range: year 10 is invalid (1\u20144). Rewrite as clean SELECT." },
      { label: "LLM generates clean SQL (attempt 2)", sql: "SELECT name, department FROM Student WHERE year = 4", expect_fail: false }
    ]
  }
];

// ======================= HELPERS =======================
function renderChecks(results) {
  return results.map(r => {
    const cls = r.valid ? 'badge-pass' : 'badge-fail';
    const icon = r.valid ? '\u2714' : '\u2718';
    return `<div class="check-item"><span class="badge ${cls}">${icon} ${r.valid ? 'PASS' : 'FAIL'}</span><span><strong>${r.check}:</strong> ${r.message}</span></div>`;
  }).join('');
}

function renderTable(columns, rows) {
  if (!rows || rows.length === 0) return '<p style="color:#888;font-size:13px;margin-top:8px;">No rows returned.</p>';
  const cols = columns || Object.keys(rows[0]);
  let html = '<div class="data-table-wrap"><table class="data-table"><thead><tr>';
  cols.forEach(c => html += `<th>${c}</th>`);
  html += '</tr></thead><tbody>';
  rows.forEach(row => {
    html += '<tr>';
    cols.forEach(c => html += `<td>${row[c] !== null && row[c] !== undefined ? row[c] : ''}</td>`);
    html += '</tr>';
  });
  html += '</tbody></table></div>';
  return html;
}

function renderVerdict(valid) {
  if (valid) return '<div class="verdict verdict-pass">\u2714 Query passed all checks.</div>';
  return '<div class="verdict verdict-fail">\u2718 Query blocked by validator.</div>';
}

async function apiCall(endpoint, body) {
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}

// ======================= SIDEBAR =======================
async function loadSchema() {
  const res = await fetch('/api/schema');
  const schema = await res.json();
  const tables = Object.keys(schema);
  document.getElementById('tableCount').textContent = tables.length + ' tables';
  const list = document.getElementById('schemaList');
  list.innerHTML = tables.map(t => {
    const cols = schema[t].map(c => `<div>${c}</div>`).join('');
    return `<details class="schema-table"><summary><strong>${t}</strong> <span style="color:#666;font-size:11px;">(${schema[t].length})</span></summary><div class="col-list">${cols}</div></details>`;
  }).join('');
}

// sidebar toggle
document.getElementById('sidebarToggle').addEventListener('click', () => {
  document.getElementById('sidebar').classList.toggle('collapsed');
  document.getElementById('sidebarToggle').classList.toggle('shifted');
});

// ======================= TABS =======================
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// ======================= TAB 1: EXAMPLES =======================
const exSelect = document.getElementById('exampleSelect');
const exDesc = document.getElementById('exampleDesc');
const exSql = document.getElementById('exampleSql');
const exResults = document.getElementById('exampleResults');

EXAMPLES.forEach((ex, i) => {
  const opt = document.createElement('option');
  opt.value = i;
  opt.textContent = ex.label;
  exSelect.appendChild(opt);
});

function updateExampleDisplay() {
  const ex = EXAMPLES[exSelect.value];
  exDesc.textContent = ex.description;
  exSql.textContent = ex.sql;
  exResults.innerHTML = '';
}
exSelect.addEventListener('change', updateExampleDisplay);
updateExampleDisplay();

document.getElementById('exampleRunBtn').addEventListener('click', async () => {
  const ex = EXAMPLES[exSelect.value];
  const btn = document.getElementById('exampleRunBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Running\u2026';
  exResults.innerHTML = '';

  const data = await apiCall('/api/validate_and_run', { query: ex.sql });

  btn.disabled = false;
  btn.textContent = 'Validate & Run';

  let html = '<div class="card"><div class="checks">' + renderChecks(data.results) + '</div>';
  html += renderVerdict(data.valid);
  if (data.valid && data.rows && data.rows.length > 0) {
    html += renderTable(data.columns, data.rows);
  }
  html += '</div>';
  exResults.innerHTML = html;
});

// ======================= TAB 2: CUSTOM =======================
const customSql = document.getElementById('customSql');
const customResults = document.getElementById('customResults');

async function runCustom(executeAfter) {
  const sql = customSql.value.trim();
  if (!sql) { customResults.innerHTML = '<div class="verdict verdict-fail">Please enter a SQL query.</div>'; return; }

  const endpoint = executeAfter ? '/api/validate_and_run' : '/api/validate';
  const btnId = executeAfter ? 'customRunBtn' : 'customValidateBtn';
  const btn = document.getElementById(btnId);
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Running\u2026';
  customResults.innerHTML = '';

  const data = await apiCall(endpoint, { query: sql });

  btn.disabled = false;
  btn.textContent = executeAfter ? 'Validate & Run' : 'Validate Only';

  let html = '<div class="card"><div class="checks">' + renderChecks(data.results) + '</div>';
  html += renderVerdict(data.valid);
  if (data.valid && data.rows && data.rows.length > 0) {
    html += renderTable(data.columns, data.rows);
  }
  html += '</div>';
  customResults.innerHTML = html;
}

document.getElementById('customValidateBtn').addEventListener('click', () => runCustom(false));
document.getElementById('customRunBtn').addEventListener('click', () => runCustom(true));

// ======================= TAB 3: PIPELINE =======================
const pipSelect = document.getElementById('pipelineSelect');
const pipResults = document.getElementById('pipelineResults');

PIPELINE_SCENARIOS.forEach((s, i) => {
  const opt = document.createElement('option');
  opt.value = i;
  opt.textContent = s.title;
  pipSelect.appendChild(opt);
});

document.getElementById('pipelineRunBtn').addEventListener('click', async () => {
  const scenario = PIPELINE_SCENARIOS[pipSelect.value];
  const btn = document.getElementById('pipelineRunBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Running\u2026';
  pipResults.innerHTML = '';

  // Show prompt
  pipResults.innerHTML = `<div class="prompt-label">User Prompt: <em>"${scenario.prompt}"</em></div>`;

  for (let i = 0; i < scenario.steps.length; i++) {
    const step = scenario.steps[i];
    await new Promise(r => setTimeout(r, 500)); // Animate delay

    let stepHtml = `<div class="pipeline-step" style="animation-delay: ${i * 0.1}s">`;
    stepHtml += `<div class="step-label">${step.label}</div>`;

    if (step.feedback) {
      stepHtml += `<div class="feedback-box">\u26A0 ${step.feedback}</div>`;
    } else {
      stepHtml += `<div class="sql-block">${step.sql}</div>`;

      // Actually validate
      const data = await apiCall('/api/validate_and_run', { query: step.sql });
      stepHtml += '<div class="checks">' + renderChecks(data.results) + '</div>';
      stepHtml += renderVerdict(data.valid);

      if (data.valid && data.rows && data.rows.length > 0) {
        stepHtml += renderTable(data.columns, data.rows);
      }
    }

    stepHtml += '</div>';
    pipResults.innerHTML += stepHtml;
  }

  btn.disabled = false;
  btn.textContent = 'Run Pipeline';
});

// ======================= INIT =======================
loadSchema();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE


# ---------------------------------------------------------------------------
# Run with: python demo_frontend.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
