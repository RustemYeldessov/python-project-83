import psycopg2
from psycopg2.extras import NamedTupleCursor
from functools import wraps


def connect_database(app):
    return psycopg2.connect(app.config['DATABASE_URL'])


def close(conn):
    conn.close()


def execute_in_database(with_commit: bool = False):
    def decorator(func: callable):
        @wraps(func)
        def inner(conn, *args, **kwargs):
            if not isinstance(conn, psycopg2.extensions.connection):
                raise ValueError('First argument must be psycopg2 connection')
            try:
                with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                    # Передаем cursor как позиционный аргумент
                    result = func(conn, cursor, *args, **kwargs)
                    if with_commit:
                        conn.commit()
                    return result
            except Exception as e:
                conn.rollback()
                raise e
        return inner
    return decorator


@execute_in_database(with_commit=True)
def insert_url(conn, cursor, url):
    cursor.execute(
        'INSERT INTO urls(name) VALUES (%s) RETURNING id;', (url,)
    )
    return cursor.fetchone().id


@execute_in_database()
def get_url(conn, cursor, url_id):
    cursor.execute(
        'SELECT * FROM urls WHERE id = %s', (url_id,)
    )
    return cursor.fetchone()


@execute_in_database()
def check_url_exists(conn, cursor, url):
    cursor.execute(
        'SELECT * FROM urls WHERE name = %s;', (url,)
    )
    return cursor.fetchone()  # Возвращаем одну запись или None


@execute_in_database(with_commit=True)
def insert_check(conn, cursor, url_id, url_info):
    cursor.execute(
        'INSERT INTO url_checks (url_id, status_code, h1, title, description) '
        'VALUES (%s, %s, %s, %s, %s) RETURNING id;',
        (url_id, url_info['status_code'], url_info['h1'],
         url_info['title'], url_info['description'])
    )
    return cursor.fetchone().id


@execute_in_database()
def get_url_checks(conn, cursor, url_id):
    cursor.execute(
        'SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC',
        (url_id,)
    )
    return cursor.fetchall()


@execute_in_database()
def get_urls_with_last_check(conn, cursor):
    cursor.execute(
        '''SELECT DISTINCT ON (urls.id)
           urls.id AS id,
           urls.name AS name,
           url_checks.created_at AS last_check_date,
           url_checks.status_code AS status_code
           FROM urls
           LEFT JOIN url_checks ON urls.id = url_checks.url_id
           ORDER BY urls.id DESC, url_checks.id DESC;'''
    )
    return cursor.fetchall()
