from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def _render_page(url):
    """Load a URL in a headless browser and return the fully-rendered HTML."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()
    return html


def fetch_website_contents(url, char_limit=3000):
    """Return the title + visible text of a page, truncated to char_limit."""
    html = _render_page(url)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string if soup.title else "No title found"

    if soup.body:
        for tag in soup.body(["script", "style", "img", "input", "svg"]):
            tag.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    return (title + "\n\n" + text)[:char_limit]


def fetch_website_links(url):
    """Return a de-duplicated list of absolute links found on a page."""
    html = _render_page(url)
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


# --- Manual test - run directly with: python scraper.py ---
if __name__ == "__main__":
    links = fetch_website_links("https://kaylin-maharaj.co.za")
    for link in links:
        print(link)