from urllib.parse import urlparse
from validators import url as validate_url


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    if len(url) > 255:
        return False
    if not validate_url(url):
        return False
    return True


def normalize_url(url: str) -> str:
    parser_url = urlparse(url)
    return f"{parser_url.scheme}://{parser_url.netloc}"
