from urllib.parse import urlparse
from validators import url as validate_url
from flask import flash


def is_vadid_url(url: str) -> bool:
    if not url:
        flash('URL не может быть пустым', 'danger')
        return False
    if len(url) > 255:
        flash('URL превышает 255 символов', 'danger')
        return False
    if not validate_url(url):
        flash('Некорректный URL', 'danger')
        return False
    return True


def normilize_url(url: str) -> str:
    parser_url = urlparse(url)
    return f"{parser_url.scheme}://{parser_url.netloc}"
