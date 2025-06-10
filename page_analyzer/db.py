from psycopg import errors as pg_errors

try:
    cursor.execute(query, params)
except pg_errors.UniqueViolation:
    flash('URL уже существует', 'warning')