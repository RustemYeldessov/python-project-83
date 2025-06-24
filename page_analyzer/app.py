import os
import page_analyzer.db as db
import requests
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort)
from page_analyzer.page_checker import extract_page_data
from page_analyzer.url_utils import normalize_url, is_valid_url

try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    pass


app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'default-secret')
app.config["DATABASE_URL"] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls/')
def show_urls_page():
    conn = db.connect_database(app)
    urls_check = db.get_urls_with_last_check(conn)
    db.close(conn)
    return render_template('urls/list.html', urls_check=urls_check)


@app.route('/urls/<int:url_id>/')
def show_url_page(url_id):
    conn = db.connect_database(app)
    url = db.get_url(conn, url_id)
    if not url:
        abort(404)

    checks = db.get_url_checks(conn, url.id)
    db.close(conn)
    return render_template('urls/detail.html', url=url, checks=checks)


@app.post('/urls/')
def add_url():
    url = request.form.get('url')
    normal_url = normalize_url(url)

    if not is_valid_url(normal_url):
        flash('Некорректный URL', 'danger')
        return redirect(url_for('show_urls'))

    conn = db.connect_database(app)
    existed_url = db.check_url_exists(conn, normal_url)

    if existed_url:
        flash('Страница уже существует', 'info')
        url_id = existed_url.id
    else:
        url_id = db.insert_url(conn, normal_url)
        flash('Страница успешно добавлена', 'success')

    db.close(conn)
    return redirect(url_for('show_url_page', url_id=url_id))


@app.post('/urls/<int:url_id>/checks')
def check_url_page(url_id):
    conn = db.connect_database(app)
    url = db.get_url(conn, url_id)
    if url is None:
        conn.close()
        abort(404)

    try:
        response = requests.get(url.name)
        response.raise_for_status()
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        db.close(conn)
        return redirect(url_for('show_url_page', url_id=url_id))

    url_info = extract_page_data(response)
    flash('Страница успешно проверена', 'success')
    db.insert_check(conn, url_id, url_info)
    db.close(conn)

    return redirect(url_for('show_url_page', url_id=url_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(_):
    return render_template('errors/500.html'), 500
