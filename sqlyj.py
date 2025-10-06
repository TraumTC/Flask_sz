from sqlalchemy import text
from exts import db


def execute_query(sql: str, params: dict | None = None):
    """Execute a SELECT query and return all rows.

    Args:
        sql: Raw SQL string (use named parameters like :id).
        params: Optional dict of parameters.
    Returns:
        List of rows (Row objects) from the query.
    """
    with db.engine.connect() as connection:
        result = connection.execute(text(sql), params or {})
        return result.fetchall()



def execute_non_query(sql: str, params: dict | None = None) -> int:
    """Execute INSERT/UPDATE/DELETE and return affected row count.

    Args:
        sql: DML SQL string.
        params: Optional dict of parameters.
    Returns:
        Number of rows affected.
    """
    with db.engine.begin() as connection:  # begin() provides a transaction
        result = connection.execute(text(sql), params or {})
        return result.rowcount

