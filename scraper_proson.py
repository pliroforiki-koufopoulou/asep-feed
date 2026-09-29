"""
scraper_proson.py - Scraper for proson.gr/ergasia/asep
Runs via GitHub Actions (daily)
Pushes results to data_proson.json in GitHub repo
"""

import json
import re
import os
import base64
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── Settings ─────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USER  = "pliroforiki-koufopoulou"
GITHUB_REPO  = "asep-feed"
GITHUB_FILE  = "data_proson.json"

BASE_URL     = "https://www.proson.gr"
LIST_URL     = BASE_URL + "/ergasia/asep"
MAX_ARTICLES = 30

CACHE_FILE   = Path(__file__).parent / "proson_cache.json"
OUTPUT_FILE  = Path(__file__).parent / "data_proson.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
}

# ── Greek month mapping ───────────────────────────────────
GREEK_MONTHS = {
    "ιαν": 1, "φεβ": 2, "μαρ": 3, "απρ": 4,
    "μαι": 5, "μαϊ": 5, "μάι": 5, "μάϊ": 5,
    "ιουν": 6, "ιούν": 6, "ιουλ": 7, "ιούλ": 7,
    "αυγ": 8, "αύγ": 8, "σεπ": 9, "σέπ": 9,
    "οκτ": 10, "νοε": 11, "νοέ": 11, "δεκ": 12, "δέκ": 12,
}


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(cache):
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                return r
            print(f"  HTTP {r.status_code} for {url}")
        except Exception as e:
            print(f"  Error: {e}")
        if attempt < retries - 1:
            time.sleep(2)
    return None


def parse_greek_datetime(text):
    """
    Parse dates like '27 Σεπ 2026 15:11', '27/09/2026 10:30',
    or ISO '2026-09-27T15:11:00'.
    Returns (date_str 'YYYY-MM-DD', time_str 'HH:MM') — either can be None.
    """
    if not text:
        return None, None

    date_str = None
    time_str = None

    # ── ISO 8601: YYYY-MM-DDTHH:MM or YYYY-MM-DD HH:MM (datetime attribute) ──
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})', text.strip())
    if m:
        y, mo, d, h, mi = m.groups()
        date_str = f"{y}-{mo}-{d}"
        time_str = f"{int(h):02d}:{mi}"
        return date_str, time_str

    # ── Time HH:MM — require valid hour (0-23), avoid matching seconds ────────
    tm = re.search(r'(?<!\d)(\d{1,2}):(\d{2})(?!\d)', text)
    if tm:
        h = int(tm.group(1))
        if 0 <= h <= 23:
            time_str = f"{h:02d}:{tm.group(2)}"

    # ── Numeric DD/MM/YYYY ────────────────────────────────────────────────────
    m = re.search(r'\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})\b', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            date_str = f"{y:04d}-{mo:02d}-{d:02d}"
            return date_str, time_str

    # ── Greek text: "27 Σεπ 2026" ─────────────────────────────────────────────
    m = re.search(r'\b(\d{1,2})\s+([Α-Ωα-ωΆ-Ώά-ώ]+)\s+(\d{4})\b', text, re.UNICODE)
    if m:
        d, month_word, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        for key, val in GREEK_MONTHS.items():
            if month_word.startswith(key):
                date_str = f"{y:04d}-{val:02d}-{d:02d}"
                return date_str, time_str

    return None, time_str


def parse_greek_date(text):
    """Convenience wrapper — returns only the date part."""
    date_str, _ = parse_greek_datetime(text)
    return date_str


def _valid_deadline(date_str):
    """Return date_str only if the year is plausibly a future/recent deadline (>= 2020)."""
    if not date_str:
        return None
    try:
        if int(date_str[:4]) >= 2020:
            return date_str
    except (ValueError, IndexError):
        pass
    return None


def extract_deadlines(article_text):
    """Extract deadline_start and deadline_end from article body text."""
    text = article_text

    # Pattern: αρχίζει / έναρξη
    m_start = re.search(
        r'(?:αρχ[ίι]ζει|εναρξη|εναρξ[ήη]|υποβολ[ήη]\s+αιτ[ήη]σεων[^.]*?απ[όο])[^\d]*'
        r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}|\d{1,2}\s+[Α-Ωα-ω]+\s+\d{4})',
        text, re.IGNORECASE | re.UNICODE,
    )
    m_end = re.search(
        r'(?:λ[ήη]γει|καταληκτικ[ήη]|λ[ήη]ξη|εως|έως|μέχρι)[^\d]*'
        r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}|\d{1,2}\s+[Α-Ωα-ω]+\s+\d{4})',
        text, re.IGNORECASE | re.UNICODE,
    )

    deadline_start = _valid_deadline(parse_greek_date(m_start.group(1)) if m_start else None)
    deadline_end   = _valid_deadline(parse_greek_date(m_end.group(1))   if m_end   else None)

    # Range: "από DD/MM/YYYY έως DD/MM/YYYY"
    if not (deadline_start and deadline_end):
        m_range = re.search(
            r'απ[όο]\s+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}|\d{1,2}\s+[Α-Ωα-ω]+\s+\d{4})'
            r'\s+(?:εως|έως|ως|μ[εέ]χρι)\s+'
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}|\d{1,2}\s+[Α-Ωα-ω]+\s+\d{4})',
            text, re.IGNORECASE | re.UNICODE,
        )
        if m_range:
            deadline_start = deadline_start or parse_greek_date(m_range.group(1))
            deadline_end   = deadline_end   or parse_greek_date(m_range.group(2))

    # Fallback: only "έως DD/MM/YYYY"
    if not deadline_end:
        m_only = re.search(
            r'(?:εως|έως|ως|μ[εέ]χρι)\s+'
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}|\d{1,2}\s+[Α-Ωα-ω]+\s+\d{4})',
            text, re.IGNORECASE | re.UNICODE,
        )
        if m_only:
            deadline_end = parse_greek_date(m_only.group(1))

    return deadline_start, deadline_end


def get_article_details(url, cache):
    """Fetch article and return (description, deadline_start, deadline_end)."""
    if url in cache:
        c = cache[url]
        return (
            c.get("description", ""),
            _valid_deadline(c.get("deadline_start")),
            _valid_deadline(c.get("deadline_end")),
        )

    r = fetch(url)
    if not r:
        return "", None, None

    soup = BeautifulSoup(r.text, "html.parser")

    # Description: first meaty paragraph
    description = ""
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if len(t) > 50:
            description = t[:250]
            break

    article_text = soup.get_text(" ", strip=True)
    deadline_start, deadline_end = extract_deadlines(article_text)

    cache[url] = {
        "description": description,
        "deadline_start": deadline_start,
        "deadline_end": deadline_end,
    }
    return description, deadline_start, deadline_end


def scrape_listing():
    """
    Scrape proson.gr/ergasia/asep.
    Article links have the format: /ergasia/asep/NNNNN_slug-text
    Structure: <a href="..."><time>DD Mon YYYY HH:MM</time><h3>Title</h3>...</a>
    """
    articles = []
    page = 1

    # Link pattern: /ergasia/asep/ followed by digits + underscore + slug
    LINK_RE = re.compile(r'/ergasia/asep/\d+_', re.IGNORECASE)

    while len(articles) < MAX_ARTICLES:
        url = LIST_URL if page == 1 else f"{LIST_URL}/page/{page}"
        print(f"Fetching listing page {page}: {url}")
        r = fetch(url)
        if not r:
            print("  Could not fetch, stopping.")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        found = []

        # Primary: <a> tags whose href matches the article pattern
        for a in soup.find_all("a", href=LINK_RE):
            href = a.get("href", "")
            if not href.startswith("http"):
                href = BASE_URL + href

            # Title: prefer <h2>/<h3>/<h4> inside the link, else link text
            title_tag = a.find(["h2", "h3", "h4"])
            title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
            # Clean up: remove leading date/time noise if title starts with digits
            title = re.sub(r'^\d{1,2}\s+\w+\s+\d{4}.*?\d{2}:\d{2}\s*', '', title).strip()
            if not title:
                continue

            # Date + time: <time> element inside the link
            pub_date = None
            pub_time = None
            time_tag = a.find("time")
            if time_tag:
                dt_attr = time_tag.get("datetime", "").strip()
                dt_text = time_tag.get_text(strip=True)
                # Try datetime attribute first (may be ISO), then fall back to text
                pub_date, pub_time = parse_greek_datetime(dt_attr)
                if not pub_date:
                    d2, t2 = parse_greek_datetime(dt_text)
                    pub_date = pub_date or d2
                    pub_time = pub_time or t2

            if not any(x["url"] == href for x in found):
                found.append({
                    "title": title,
                    "url": href,
                    "published_date": pub_date,
                    "published_time": pub_time,
                })

        if not found:
            print("  No articles found on this page, stopping.")
            break

        # De-duplicate against already collected articles
        existing_urls = {a["url"] for a in articles}
        new = [x for x in found if x["url"] not in existing_urls]
        articles.extend(new)
        print(f"  Found {len(found)} articles ({len(new)} new, total: {len(articles)})")

        # Check for next-page link
        next_link = soup.find("a", href=re.compile(r'/ergasia/asep/page/\d+', re.I))
        if not next_link:
            next_link = soup.find("a", class_=re.compile(r'next', re.I))
        if not next_link:
            break

        page += 1
        time.sleep(1)

    return articles[:MAX_ARTICLES]


def push_to_github(data):
    """Push data_proson.json to GitHub via Contents API."""
    if not GITHUB_TOKEN:
        print("No GITHUB_TOKEN, skipping push.")
        return False

    api_url = (
        f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
        f"/contents/{GITHUB_FILE}"
    )
    hdrs = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    sha = None
    r = requests.get(api_url, headers=hdrs, timeout=15)
    if r.status_code == 200:
        sha = r.json().get("sha")

    content = json.dumps(data, ensure_ascii=False, indent=2)
    payload = {
        "message": f"Update {GITHUB_FILE} ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "committer": {"name": "proson-scraper", "email": "bot@asep-feed.local"},
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(api_url, headers=hdrs, json=payload, timeout=30)
    if r.status_code in (200, 201):
        print(f"Pushed {GITHUB_FILE} to GitHub successfully.")
        return True
    else:
        print(f"GitHub push failed: {r.status_code} {r.text[:300]}")
        return False


def main():
    print("=" * 52)
    print(f"proson.gr ASEP Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 52)

    cache = load_cache()
    print(f"Cache loaded: {len(cache)} entries")

    stubs = scrape_listing()
    print(f"\nTotal articles from listing: {len(stubs)}")

    results = []
    for i, stub in enumerate(stubs, 1):
        print(f"  [{i}/{len(stubs)}] {stub['title'][:65]}")
        desc, dl_start, dl_end = get_article_details(stub["url"], cache)

        m = re.search(r'/(\d+)_', stub["url"])
        article_id = m.group(1) if m else str(i)

        results.append({
            "id": article_id,
            "title": stub["title"],
            "description": desc,
            "published_date": stub["published_date"],
            "published_time": stub.get("published_time"),
            "deadline_start": dl_start,
            "deadline_end": dl_end,
            "url": stub["url"],
            "source": "proson.gr",
        })
        time.sleep(0.5)

    save_cache(cache)
    print(f"\nCache saved: {len(cache)} entries")

    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(results),
        "articles": results,
    }

    OUTPUT_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Saved {OUTPUT_FILE} ({len(results)} articles)")

    push_to_github(output)
    print("\nDone!")


if __name__ == "__main__":
    main()
