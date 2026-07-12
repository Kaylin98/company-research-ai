import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from scraper import browser_session, fetch_website_links, fetch_website_contents

load_dotenv()
GROQ_MODEL = "llama-3.3-70b-versatile"
api_key = os.getenv("GROQ_API_KEY")
openAI = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

def select_relevant_links(links):
    """Ask GPT to pick the links worth scraping (About/Careers/Blog etc.)."""
    system_prompt = (
        "You are given a list of links found on a company's homepage. "
        "Select only the links useful for researching the company before "
        "a job interview — things like About, Careers, Team, Blog, News, "
        "or Product pages. Ignore social media, legal pages, PDFs, and "
        "anything unrelated. Respond with ONLY a JSON array of URLs, "
        "nothing else. Pick at most 4."
    )

    response = openAI.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "\n".join(links)},
        ],
    )

    raw = _clean_json_response(response.choices[0].message.content)
    return json.loads(raw)


def _clean_json_response(raw):
    """Strip markdown code fencing GPT sometimes adds around JSON."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").replace("json", "", 1).strip()
    return raw


def gather_page_contents(browser, links):
    """Scrape each link's text content, keyed by URL, using one shared browser."""
    pages = {}
    for link in links:
        pages[link] = fetch_website_contents(browser, link)
    return pages


def summarize_company(company_url, pages):
    """Turn scraped page content into a structured markdown company summary."""
    combined = ""
    for url, text in pages.items():
        combined += f"PAGE: {url}\n{text}\n\n---\n\n"

    system_prompt = (
        "You are helping a software engineer prepare for a job interview. "
        "Based on the scraped page content provided, write a concise "
        "markdown summary of the company with these sections:\n"
        "## What They Do\n"
        "## Tech Stack (if mentioned or inferable)\n"
        "## Recent News\n"
        "## Culture / Values\n\n"
        "Be factual — only state things supported by the content. "
        "If a section has no supporting info, say 'Not enough information found.'"
    )

    response = openAI.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Company URL: {company_url}\n\n{combined}"},
        ],
    )

    return response.choices[0].message.content


def research_company(homepage_url):
    """Run the full pipeline: fetch links, filter, scrape, summarize."""
    try:
        with browser_session() as browser:
            links = fetch_website_links(browser, homepage_url)
            selected = select_relevant_links(links)

            if homepage_url not in selected:
                selected.append(homepage_url)

            pages = gather_page_contents(browser, selected)
    except Exception as e:
        return (
            f"Couldn't research {homepage_url}. It may be blocking automated "
            f"access, or the URL may be invalid.\n\nDetails: {e}"
        )

    return summarize_company(homepage_url, pages)


# --- Manual test — run directly with: python summarizer.py ---
if __name__ == "__main__":
    print(research_company("https://entelect.co.za/"))