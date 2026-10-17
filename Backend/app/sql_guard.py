"""AST validation complements restricted database roles; it is not a SQL sandbox."""

import sqlglot
from sqlglot import exp

from app.errors import AppError
from app.fixtures import SOURCE_TABLES

SAFE_FUNCTIONS = {
    "SUM",
    "COUNT",
    "AVG",
    "MIN",
    "MAX",
    "ROUND",
    "ABS",
    "COALESCE",
    "NULLIF",
    "CAST",
    "TRY_CAST",
    "SAFE_CAST",
    "LOWER",
    "UPPER",
    "TRIM",
    "LTRIM",
    "RTRIM",
    "CONCAT",
    "SUBSTRING",
    "LENGTH",
    "CHAR_LENGTH",
    "DATE",
    "DATE_TRUNC",
    "TIMESTAMP_TRUNC",
    "DATE_DIFF",
    "DATE_ADD",
    "DATE_SUB",
    "EXTRACT",
    "YEAR",
    "MONTH",
    "DAY",
    "CURRENT_DATE",
    "CURRENT_TIMESTAMP",
    "TO_CHAR",
    "FORMAT_DATE",
    "STRFTIME",
    "ROW_NUMBER",
    "RANK",
    "DENSE_RANK",
    "LAG",
    "LEAD",
    "IF",
    "IFNULL",
    "GREATEST",
    "LEAST",
    "STDDEV",
    "VARIANCE",
    "PERCENT_RANK",
    "SAFE_DIVIDE",
    "CASE",
    "INT64",
    "FLOAT64",
    "DECIMAL",
    "ANY_VALUE",
}
FORBIDDEN_NODES = {
    "Insert",
    "Update",
    "Delete",
    "Merge",
    "Create",
    "Drop",
    "Alter",
    "Command",
    "Copy",
    "Export",
    "Transaction",
    "Commit",
    "Rollback",
    "Grant",
    "Revoke",
    "Into",
    "Lock",
    "Execute",
    "Use",
    "Set",
    "Pragma",
    "Attach",
    "Detach",
}


def validate_sql(
    sql: str, source: str, project: str, dataset: str, *, tables=None, postgres_schema="retail"
) -> str:
    dialect = "bigquery" if source == "bigquery" else "postgres"
    if len(sql) > 12_000:
        raise AppError("Query is too large.", code="unsafe_sql")
    try:
        statements = sqlglot.parse(sql, read=dialect)
    except sqlglot.errors.ParseError as exc:
        raise AppError("Generated SQL could not be parsed.", code="invalid_sql") from exc
    if len(statements) != 1 or not isinstance(statements[0], exp.Query):
        raise AppError("Only one read-only SELECT query is allowed.", code="unsafe_sql")
    tree = statements[0]
    ctes = {cte.alias for cte in tree.find_all(exp.CTE)}
    physical_tables = 0
    for node in tree.walk():
        if type(node).__name__ in FORBIDDEN_NODES:
            raise AppError("Query contains a forbidden operation.", code="unsafe_sql")
        if isinstance(node, exp.Dot) and isinstance(node.expression, exp.Func):
            raise AppError("Schema-qualified or remote function calls are not allowed.", code="unsafe_sql")
        # SQLGlot models logical connectors as Func subclasses too. Their
        # children still pass through this walk and the function allowlist.
        if isinstance(node, exp.Func) and not isinstance(node, (exp.And, exp.Or)):
            name = node.name.upper() if isinstance(node, exp.Anonymous) else node.sql_name().upper()
            # SQLGlot normalizes approved FORMAT_DATE / TO_CHAR to TimeToStr.
            # Match its typed node, never an anonymous UDF of the same name.
            if isinstance(node, exp.TimeToStr):
                name = "FORMAT_DATE"
            elif isinstance(node, exp.TsOrDsToDate):
                name = "DATE"
            if name not in SAFE_FUNCTIONS:
                raise AppError(f"Function {name} is not approved for demo queries.", code="unsafe_sql")
        if isinstance(node, exp.Table):
            if not isinstance(node.this, exp.Identifier):
                raise AppError("Table-valued functions are not allowed.", code="unsafe_sql")
            name = node.name
            if name in ctes and not node.db and not node.catalog:
                continue
            if name not in (tables or SOURCE_TABLES)[source]:
                raise AppError("Query references a table outside the demo sources.", code="unsafe_sql")
            if source == "bigquery":
                if node.db and node.db != dataset or node.catalog and node.catalog != project:
                    raise AppError("Query references a dataset outside the demo.", code="unsafe_sql")
                node.set("db", exp.to_identifier(dataset))
                node.set("catalog", exp.to_identifier(project, quoted=True))
            else:
                if node.catalog or node.db not in ("", postgres_schema):
                    raise AppError("Query references a schema outside the demo.", code="unsafe_sql")
                node.set("db", exp.to_identifier(postgres_schema))
            physical_tables += 1
    if not physical_tables:
        raise AppError("An analysis query must read a demo table.", code="unsafe_sql")
    return tree.sql(dialect=dialect)
