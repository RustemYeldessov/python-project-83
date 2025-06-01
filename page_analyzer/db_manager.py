# import psycopg2
# from psycopg2.extras import NamedTupleCursor
# from functools import wraps
#
#
# def connect_db(app):
#     return psycopg2.connect(app.config['DATABASE_URL'])
#
#
# def close_conn():
#     conn.close()