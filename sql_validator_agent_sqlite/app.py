from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from validator import SQLValidator


DB_URI = "sqlite:///academic.db"  # SQLite database file in this folder

app = FastAPI()
validator = SQLValidator(DB_URI)


class QueryRequest(BaseModel):
    query: str


@app.post("/validate")
def validate_query(request: QueryRequest):
    is_valid, results = validator.validate(request.query)
    if is_valid:
        return {"valid": True, "message": "Query is valid", "results": results}
    raise HTTPException(
        status_code=400,
        detail={"valid": False, "results": results},
    )


@app.post("/validate_and_run")
def validate_and_run_query(request: QueryRequest):
    is_valid, results = validator.validate(request.query)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail={"valid": False, "results": results},
        )

    try:
        with validator.engine.connect() as conn:
            result = conn.execute(text(request.query))
            columns = result.keys()
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        exec_error = {
            "check": "Execution",
            "valid": False,
            "message": str(e),
        }
        raise HTTPException(
            status_code=400,
            detail={"valid": False, "results": results + [exec_error]},
        )

    return {
        "valid": True,
        "message": "Query is valid",
        "results": results,
        "rows": rows,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
