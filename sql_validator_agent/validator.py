import re

import sqlparse
from sqlalchemy import MetaData, create_engine, inspect, text


class SQLValidator:
    def __init__(self, db_uri: str):
        self.engine = create_engine(db_uri)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.inspector = inspect(self.engine)

    def validate_syntax(self, query: str):
        """Use PostgreSQL to actually parse the query via EXPLAIN."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"EXPLAIN {query}"))
            return True, "Syntax valid"
        except Exception as e:
            return False, f"Syntax error: {str(e)}"

    def validate_semantics(self, query: str):
        """Check that at least one referenced table exists in the schema."""
        try:
            parsed = sqlparse.parse(query)
            if not parsed:
                return False, "Unable to parse query"
            stmt = parsed[0]
        except Exception as e:
            return False, f"Semantic parse error: {str(e)}"

        tables = set()
        for token in stmt.tokens:
            if isinstance(token, sqlparse.sql.IdentifierList):
                for identifier in token.get_identifiers():
                    tables.add(identifier.get_real_name())
            elif isinstance(token, sqlparse.sql.Identifier):
                tables.add(token.get_real_name())

        tables = [t for t in tables if t in self.metadata.tables]
        if not tables:
            return False, "No valid tables referenced"
        return True, "Semantics valid"

    def validate_data_range(self, query: str):
        """Validate year (1-4) and semester (1-8) values in WHERE clauses."""
        year_pattern = r"(?:year\s*=\s*(\d+)|year\s+IN\s+\(([^)]+)\))"
        semester_pattern = r"(?:semester\s*=\s*(\d+)|semester\s+IN\s+\(([^)]+)\))"
        year_match = re.search(year_pattern, query, re.IGNORECASE)
        semester_match = re.search(semester_pattern, query, re.IGNORECASE)

        if year_match:
            years = year_match.group(2) or year_match.group(1)
            years = [int(y.strip()) for y in years.split(",")]
            if any(y not in {1, 2, 3, 4} for y in years):
                return False, "Invalid year value (must be 1-4)"

        if semester_match:
            semesters = semester_match.group(2) or semester_match.group(1)
            semesters = [int(s.strip()) for s in semesters.split(",")]
            if any(s not in {1, 2, 3, 4, 5, 6, 7, 8} for s in semesters):
                return False, "Invalid semester value (must be 1-8)"

        return True, "Data range valid"

    def validate_security(self, query: str):
        """Naive SQL injection / dangerous statement check."""
        forbidden_keywords = ["drop", "delete", "insert", "update", "union", "exec", "--", ";"]
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in forbidden_keywords):
            return False, "Forbidden SQL keyword detected"
        return True, "Security valid"

    def validate(self, query: str):
        checks = [
            ("Syntax", self.validate_syntax(query)),
            ("Semantics", self.validate_semantics(query)),
            ("Data Range", self.validate_data_range(query)),
            ("Security", self.validate_security(query)),
        ]
        results = []
        for name, (valid, message) in checks:
            results.append({"check": name, "valid": valid, "message": message})
            if not valid:
                return False, results
        return True, results
