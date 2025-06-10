from bs4 import BeautifulSoup


def extract_page_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1 = soup.h1.get_text(strip=True) if soup.h1 else ''
    title = soup.title.get_text(strip=True) if soup.title else ''
    description = ''
    meta = soup.find('meta', attrs={'name': 'description'})
    if meta and meta.has_attr('content'):
        description = meta['content'].strip()
    return title, h1, description
