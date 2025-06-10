from psycopg import errors as pg_errors
from flask import flash


def execute_query(connection, query, params=None):
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor
    except pg_errors.UniqueViolation:
        flash('URL уже существует', 'danger')
        return None
    except pg_errors.Error as e:
        flash(f'Ошибка базы данных: {e}', 'danger')
        return None
