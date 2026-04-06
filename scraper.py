"""
Web scraper for extracting content from client's digital assets.

Strategy:
  1. Try fast requests+BeautifulSoup first.
  2. If the page looks JS-rendered (very little visible text), fall back to
     Playwright (headless Chromium) which executes JavaScript before reading.
  3. Handles: regular sites, SPA/React/Wix/Elementor, Dapei Zahav listings.
"""

import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 15
CRAWL_DELAY = 0.5

# If fewer than this many characters are found via requests, assume JS-rendered
JS_THRESHOLD = 300


def _is_js_rendered(text: str) -> bool:
    """Heuristic: very short text after stripping usually means JS rendered the real content."""
    return len(text.strip()) < JS_THRESHOLD


def _clean_soup(soup: BeautifulSoup) -> str:
    """Remove noise tags and return clean joined text."""
    for tag in soup(["script", "style", "noscript", "iframe", "nav", "footer", "head"]):
        tag.decompose()
    lines = [l for l in soup.get_text(separator="\n", strip=True).splitlines() if l.strip()]
    return "\n".join(lines)


def _fetch_with_requests(url: str) -> tuple[str, str]:
    """
    Fetch a page with requests.
    Returns (clean_text, raw_html). Returns ("", "") on error.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        raw_html = resp.text
        soup = BeautifulSoup(raw_html, "lxml")
        return _clean_soup(soup), raw_html
    except Exception as e:
        return f"[Error fetching {url}: {e}]", ""


def _fetch_with_playwright(url: str) -> tuple[str, str]:
    """
    Fetch a page using headless Chromium via Playwright.
    Waits for network idle so JS has time to render.
    Returns (clean_text, raw_html).
    """
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(extra_http_headers={"Accept-Language": "he-IL,he;q=0.9"})
            page.goto(url, wait_until="networkidle", timeout=30000)
            # Extra wait for lazy-loaded content
            page.wait_for_timeout(1500)
            raw_html = page.content()
            browser.close()

        soup = BeautifulSoup(raw_html, "lxml")
        return _clean_soup(soup), raw_html
    except Exception as e:
        return f"[Playwright error for {url}: {e}]", ""


def _fetch_page(url: str) -> tuple[str, str]:
    """
    Smart fetch: tries requests first, falls back to Playwright if JS-rendered.
    Returns (clean_text, raw_html).
    """
    text, html = _fetch_with_requests(url)

    if _is_js_rendered(text):
        print(f"  [scraper] JS-rendered detected at {url} — switching to Playwright")
        text, html = _fetch_with_playwright(url)

    return text, html


def _collect_internal_links(base_url: str, raw_html: str, max_links: int = 15) -> list[str]:
    """Collect internal links from a page's raw HTML."""
    if not raw_html:
        return []
    soup = BeautifulSoup(raw_html, "lxml")
    base_domain = urlparse(base_url).netloc
    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        parsed = urlparse(href)
        if parsed.netloc == base_domain and parsed.scheme in ("http", "https"):
            clean = parsed._replace(fragment="").geturl()
            links.add(clean)
            if len(links) >= max_links:
                break
    return list(links)


def scrape_website(base_url: str, max_pages: int = 5) -> dict:
    """
    Crawl up to max_pages of a website starting from base_url.
    Auto-detects JS-rendered sites and uses Playwright for those.
    Returns {'base_url': str, 'pages': [{'url': str, 'content': str}]}
    """
    visited = set()
    to_visit = [base_url]
    pages = []

    while to_visit and len(pages) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        text, raw_html = _fetch_page(url)
        pages.append({"url": url, "content": text})

        if len(pages) < max_pages:
            new_links = _collect_internal_links(url, raw_html)
            for link in new_links:
                if link not in visited:
                    to_visit.append(link)

        time.sleep(CRAWL_DELAY)

    return {"base_url": base_url, "pages": pages}


def scrape_dapei_zahav(listing_url: str) -> dict:
    """
    Scrape a Dapei Zahav business listing.
    Dapei Zahav uses server-side rendering so requests is usually enough,
    but falls back to Playwright automatically if needed.
    """
    text, _ = _fetch_page(listing_url)
    return {"url": listing_url, "content": text}


def combine_scraped_content(website_data: dict, dapei_zahav_data: dict) -> str:
    """Combine all scraped content into a single text block for AI processing."""
    parts = []

    parts.append("=== WEBSITE CONTENT ===")
    for i, page in enumerate(website_data.get("pages", []), 1):
        parts.append(f"\n--- Page {i}: {page['url']} ---")
        parts.append(page["content"] or "[No content]")

    parts.append("\n=== DAPEI ZAHAV LISTING ===")
    parts.append(f"URL: {dapei_zahav_data.get('url', 'N/A')}")
    parts.append(dapei_zahav_data.get("content") or "[No content]")

    return "\n".join(parts)
