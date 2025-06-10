import os
import requests
from flask import Flask, redirect, url_for, flash
from dotenv import load_dotenv
from psycopg import connect
from datetime import datetime
from bs4 import BeautifulSoup

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
connection = connect(os.getenv('DATABASE_URL'), autocommit=True)


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT name FROM urls WHERE id = %s', (url_id,))
        url_data = cursor.fetchone()

        if not url_data:
            flash('URL не найден', 'danger')
            return redirect(url_for('show_url', url_id=url_id))

        url = url_data[0]

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            status_code = response.status_code
            soup = BeautifulSoup(response.text, 'html.parser')

            h1 = soup.h1.get_text(strip=True) if soup.h1 else ''
            title = soup.title.string.strip() if soup.title else ''
            description_tag = soup.find('meta', attrs={'name': 'description'})
            if description_tag and 'content' in description_tag.attrs:
                description = description_tag['content'].strip()
            else:
                description = ''

        except requests.RequestException:
            flash('Произошла ошибка при проверке сайта', 'danger')
            return redirect(url_for('show_url', url_id=url_id))

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute(
            '''
            INSERT INTO url_checks (
                url_id, status_code, h1, title, description, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (url_id, status_code, h1, title, description, created_at)
        )
        connection.commit()

    flash('Проверка успешно выполнена', 'success')
    return redirect(url_for('show_url', url_id=url_id))
