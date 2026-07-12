from contextlib import contextmanager
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin


@contextmanager
def browser_session():
    """Launch one browser and reuse it for multiple page fetches."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def _render_page(browser, url):
    """Load a URL in the given browser and return the fully-rendered HTML."""
    page = browser.new_page()
    page.goto(url)
    html = page.content()
    page.close()
    return html


def fetch_website_contents(browser, url, char_limit=3000):
    """Return the title + visible text of a page, truncated to char_limit."""
    html = _render_page(browser, url)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string if soup.title else "No title found"

    if soup.body:
        for tag in soup.body(["script", "style", "img", "input", "svg"]):
            tag.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    return (title + "\n\n" + text)[:char_limit]


def fetch_website_links(browser, url):
    """Return a de-duplicated list of absolute links found on a page."""
    html = _render_page(browser, url)
    soup = BeautifulSoup(html, "html.parser")

    links = []
    seen = set()
    skip_prefixes = ("#", "mailto:", "tel:")

    for a in soup.find_all("a"):
        href = a.get("href")
        if not href or href.startswith(skip_prefixes):
            continue

        absolute_url = urljoin(url, href)
        if absolute_url not in seen:
            seen.add(absolute_url)
            links.append(absolute_url)

    return links


# --- Manual test — run directly with: python scraper.py ---
if __name__ == "__main__":
    with browser_session() as browser:
        links = fetch_website_links(browser, "https://kaylin-maharaj.co.za")
        for link in links:
            print(link)