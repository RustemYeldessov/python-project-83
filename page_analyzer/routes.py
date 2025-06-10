import os
from flask import Flask, render_template, redirect, url_for, flash, request
from validators import url as validate_url
from urllib.parse import urlparse
from datetime import datetime
from psycopg import connect

app = Flask(__name__)
connection = connect(os.getenv('DATABASE_URL'), autocommit=True)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def add_url():
    user_input = request.form.get('url', '').strip()

    if not validate_url(user_input) or len(user_input) > 255:
        flash('Некорректный URL', 'danger')
        return redirect(url_for('index'))

    parsed_url = urlparse(user_input)
    normalized_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
    created_at = datetime.now()

    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id FROM urls WHERE name = %s',
            (normalized_url,)
        )
        existing = cursor.fetchone()
        if existing:
            flash('Страница уже существует', 'info')
            return redirect(url_for('show_url', id=existing[0]))

        cursor.execute(
            'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
            (normalized_url, created_at)
        )
        new_id = cursor.fetchone()[0]

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('show_url', id=new_id))


@app.route('/urls')
def list_urls():
    with connection.cursor() as cursor:
        cursor.execute(
            '''
            SELECT
                urls.id,
                urls.name,
                MAX(url_checks.created_at) AS last_check,
                MAX(url_checks.status_code) AS last_status
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id
            ORDER BY urls.id DESC;
            '''
        )
        urls = cursor.fetchall()

    urls_data = [
        {
            'id': row[0],
            'name': row[1],
            'last_check': row[2],
            'last_status': row[3]
        } for row in urls
    ]

    return render_template('urls.html', urls=urls_data)


@app.route('/urls/<int:id>')
def show_url(id):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, name, created_at FROM urls WHERE id = %s',
            (id,)
        )
        url = cursor.fetchone()
        if url is None:
            return 'URL не найден', 404

        cursor.execute(
            '''
            SELECT
                id,
                status_code,
                h1,
                title,
                description,
                created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC;
            ''',
            (id,)
        )

        checks = cursor.fetchall()

    return render_template('url_detail.html', url=url, checks=checks)
