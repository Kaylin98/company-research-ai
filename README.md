# Company Research AI

A small AI-powered tool that scrapes a company's website and generates a
concise interview-prep summary: what they do, tech stack, recent news, and
culture — so you can walk into an interview sounding like you've been
following the company for years, instead of frantically skimming their
"About Us" page in the parking lot.

Built to solve a real problem — quickly researching a company before a job
interview — while getting hands-on with AI-powered web scraping, LLM
prompting, and Streamlit.

## How it works

1. **Scrapes the homepage** using [Playwright](https://playwright.dev/python/)
   (a headless browser), so it works on JavaScript-rendered sites that plain
   `requests` can't handle.
2. **Filters links with an LLM** — sends the raw list of links to a
   Llama model (via [Groq](https://groq.com)), which picks out the useful
   ones (About, Careers, Blog) and ignores noise (social media, legal pages,
   anchors).
3. **Scrapes the selected pages** for their text content, reusing a single
   browser session for speed.
4. **Summarizes with an LLM** — sends the combined page content to Llama,
   which produces a structured markdown summary.

Results are cached per-URL in the Streamlit session, so researching the same
company twice doesn't repeat the scrape or re-call the API.

## Demo

A short demo video is on my portfolio: [kaylin-maharaj.co.za](https://kaylin-maharaj.co.za)

## Tech stack

- Python
- [Playwright](https://playwright.dev/python/) — headless browser scraping
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
- [Groq API](https://groq.com) (Llama 3.3) — link selection + summarization
- [Streamlit](https://streamlit.io) — UI

## Setup

```bash
git clone https://github.com/Kaylin98/company-research-ai.git
cd company-research-ai

uv venv
.venv\Scripts\activate   # on macOS/Linux: source .venv/bin/activate

uv pip install -r requirements.txt
playwright install chromium   # downloads the headless browser binary

cp .env.example .env
# then edit .env and add your own Groq API key (free at console.groq.com)
```

## Run it

```bash
streamlit run app.py
```

Enter a company's homepage URL and click "Research this company."

## Project structure

```
scraper.py       # Playwright-based page/link fetching
summarizer.py     # LLM prompts: link filtering + summary generation
app.py            # Streamlit UI
requirements.txt
.env.example
```

## Notes & known limitations

- API keys are never committed — they live in a local `.env` file excluded
  via `.gitignore`. If hosted, keys are set as platform secrets instead.
- Some sites (e.g. openai.com) block automated browsers with services like
  Cloudflare — turns out an AI company is quite good at detecting robots.
  This is a personal/portfolio project, not built to bypass bot-detection.
- Currently no automated tests — each module has a manual test block
  (`if __name__ == "__main__":`) for quick standalone checks.
- Possible future improvements: parallelize page scraping (currently
  sequential), trim shared nav/footer boilerplate before summarizing.
