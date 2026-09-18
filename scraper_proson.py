"""
scraper_proson.py - Scraper for proson.gr/ergasia/asep
Runs via GitHub Actions (Mon/Wed/Fri)
Pushes results to data_proson.json in GitHub repo
"""

import json
import re
import os
import base64
import time
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── Settings ─────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USER  = "pliroforiki-koufopoulou"
GITHUB_REPO  = "asep-feed"
GITHUB_FILE  = "data_proson.json"

BASE_URL   = "https://www.proson.gr"
LIST_URL   = BASE_URL + "/ergasia/asep"
MAX_ARTICLES = 30

CACHE_FILE  = Path(__file__).parent / "proson_cache.json"
OUTPUT_FILE = Path(__file__).parent / "data_proson.json"

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
    "ιανουαριου": 1, "ιανουαριου": 1, "φεβρουαριου": 2,
    "μαρτιου": 3, "απριλιου": 4, "μαιου": 5, "ιουνιου": 6,
    "ιουλιου": 7, "αυγουστου": 8, "σεπτεμβριου": 9,
    "οκτωβριου": 10, "νοεμβριου": 11, "δεκεμβριου": 12,
    # short forms
    "ιαν": 1, "φεβ": 2, "μαρ": 3, "απρ": 4, "μαι": 5, "μαϊ": 5,
    "ιουν": 6, "ιουλ": 7, "αυγ": 8, "σεπ": 9, "οκτ": 10,
    "νοε": 11, "δεκ": 12,
}


def load_cache():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                return r
            print(f"  HTTP {r.status_code} for {url}")
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
        if attempt < retries - 1:
            time.sleep(2)
    return None


def parse_greek_date(text):
    """
    Parse a Greek date like '15 Σεπτεμβριου 2026' or '15/09/2026'.
    Returns 'YYYY-MM-DD' or None.
    """
    # Try numeric DD/MM/YYYY or DD-MM-YYYY
    m = re.search(r'\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})\b', text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= mo <= 12 and 1 <= d <= 31:
            return f"{y:04d}-{mo:02d}-{d:02d}"

    # Try Greek text: DD Μήνας YYYY
    m = re.search(
        r'\b(\d{1,2})\s+([Α-Ωα-ωΆ-Ώά-ώ]+)\s+(\d{4})\b',
        text,
        re.UNICODE,
    )
    if m:
        d, month_word, y = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        # strip accents for matching
        normalized = month_word
        for key, val in GREEK_MONTHS.items():
            if normalized.startswith(key[:4]):
                return f"{y:04d}-{val:02d}-{d:02d}"
    return None


def extract_deadlines(article_text):
    """
    Search article text for deadline dates.
    Returns (deadline_start, deadline_end) as 'YYYY-MM-DD' strings or None.
    """
    text = article_text

    # Pattern: "αρχίζει ... DD/MM/YYYY ... λήγει ... DD/MM/YYYY"
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

    deadline_start = parse_greek_date(m_start.group(1)) if m_start else None
    deadline_end   = parse_greek_date(m_end.group(1))   if m_end   else None

    # Pattern: "από DD/MM/YYYY έως DD/MM/YYYY" (range in one phrase)
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

    # Fallback: "έως DD/MM/YYYY" only
    if not deadline_end:
        m_only_end = re.search(
            r'(?:εως|έως|ως|μ[εέ]χρι)\s+'
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{4}|\d{1,2}\s+[Α-Ωα-ω]+\s+\d{4})',
            text, re.IGNORECASE | re.UNICODE,
        )
        if m_only_end:
            deadline_end = parse_greek_date(m_only_end.group(1))

    return deadline_start, deadline_end


def get_article_details(url, cache):
    """Fetch article page and return (description, deadline_start, deadline_end)."""
    if url in cache:
        c = cache[url]
        return c.get("description", ""), c.get("deadline_start"), c.get("deadline_end")

    r = fetch(url)
    if not r:
        return "", None, None

    soup = BeautifulSoup(r.text, "html.parser")

    # Extract description (first ~200 chars of article body)
    description = ""
    body = soup.find("div", class_=re.compile(r"article|entry|content|post", re.I))
    if body:
        paragraphs = body.find_all("p")
        for p in paragraphs:
            t = p.get_text(strip=True)
            if len(t) > 40:
                description = t[:250]
                break

    # Extract all visible text for deadline search
    article_text = soup.get_text(" ", strip=True)
    deadline_start, deadline_end = extract_deadlines(article_text)

    result = {
        "description": description,
        "deadline_start": deadline_start,
        "deadline_end": deadline_end,
    }
    cache[url] = result
    return description, deadline_start, deadline_end


def scrape_listing():
    """Scrape proson.gr/ergasia/asep listing pages, return list of article stubs."""
    articles = []
    page = 1

    while len(articles) < MAX_ARTICLES:
        if page == 1:
            url = LIST_URL
        else:
            url = f"{LIST_URL}/page/{page}"

        print(f"Fetching listing page {page}: {url}")
        r = fetch(url)
        if not r:
            print(f"  Could not fetch page {page}, stopping.")
            break

        soup = BeautifulSoup(r.text, "html.parser")

        # Find article links — proson.gr uses <article> or <h2>/<h3> with links
        found = []

        # Try standard article elements first
        for tag in soup.find_all(["article", "div"], class_=re.compile(r"post|article|item|entry", re.I)):
            a = tag.find("a", href=re.compile(r"/ergasia/asep/\d+", re.I))
            if not a:
                continue
            href = a.get("href", "")
            if not href.startswith("http"):
                href = BASE_URL + href

            # title
            title_tag = tag.find(["h2", "h3", "h4"])
            title = title_tag.get_text(strip=True) if title_tag else a.get_text(strip=True)
            if not title:
                continue

            # date
            pub_date = None
            time_tag = tag.find("time")
            if time_tag:
                pub_date = time_tag.get("datetime", time_tag.get_text(strip=True))
                if pub_date and "T" in pub_date:
                    pub_date = pub_date[:10]
                elif pub_date:
                    pub_date = parse_greek_date(pub_date) or pub_date[:10]

            if not any(x["url"] == href for x in found):
                found.append({"title": title, "url": href, "published_date": pub_date})

        # Fallback: any link matching /ergasia/asep/\d+
        if not found:
            for a in soup.find_all("a", href=re.compile(r"/ergasia/asep/\d+", re.I)):
                href = a.get("href", "")
                if not href.startswith("http"):
                    href = BASE_URL + href
                title = a.get_text(strip=True)
                if title and not any(x["url"] == href for x in found):
                    found.append({"title": title, "url": href, "published_date": None})

        if not found:
            print(f"  No articles found on page {page}, stopping.")
            break

        articles.extend(found)
        print(f"  Found {len(found)} articles (total so far: {len(articles)})")

        # Check for next page link
        next_link = soup.find("a", string=re.compile(r"επ[οό]μενη|next|>", re.I))
        if not next_link:
            # Also check for numbered pagination
            next_link = soup.find("a", class_=re.compile(r"next", re.I))
        if not next_link:
            break

        page += 1
        time.sleep(1)

    return articles[:MAX_ARTICLES]


def push_to_github(data):
    """Push data_proson.json to GitHub via API."""
    if not GITHUB_TOKEN:
        print("No GITHUB_TOKEN found, skipping push.")
        return False

    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    # Get current SHA if file exists
    sha = None
    r = requests.get(api_url, headers=headers, timeout=15)
    if r.status_code == 200:
        sha = r.json().get("sha")

    content = json.dumps(data, ensure_ascii=False, indent=2)
    payload = {
        "message": f"Update data_proson.json ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "committer": {"name": "proson-scraper", "email": "bot@asep-feed.local"},
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(api_url, headers=headers, json=payload, timeout=30)
    if r.status_code in (200, 201):
        print(f"Pushed {GITHUB_FILE} to GitHub successfully.")
        return True
    else:
        print(f"GitHub push failed: {r.status_code} {r.text[:300]}")
        return False


def main():
    print("=" * 50)
    print(f"proson.gr ASEP Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    cache = load_cache()
    print(f"Cache loaded: {len(cache)} entries")

    # Step 1: Get article list from listing pages
    stubs = scrape_listing()
    print(f"\nTotal articles from listing: {len(stubs)}")

    # Step 2: Visit each article for details
    results = []
    for i, stub in enumerate(stubs, 1):
        print(f"  [{i}/{len(stubs)}] {stub['title'][:60]}")
        desc, dl_start, dl_end = get_article_details(stub["url"], cache)

        # Build article ID from URL
        m = re.search(r"/(\d+)(?:[/?#]|$)", stub["url"])
        article_id = m.group(1) if m else str(i)

        results.append({
            "id": article_id,
            "title": stub["title"],
            "description": desc,
            "published_date": stub["published_date"],
            "deadline_start": dl_start,
            "deadline_end": dl_end,
            "url": stub["url"],
            "source": "proson.gr",
        })
        time.sleep(0.5)

    # Save cache
    save_cache(cache)
    print(f"\nCache saved: {len(cache)} entries")

    # Build output
    output = {
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total": len(results),
        "articles": results,
    }

    # Save locally
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {OUTPUT_FILE} ({len(results)} articles)")

    # Push to GitHub
    push_to_github(output)

    print("\nDone!")


if __name__ == "__main__":
    main()
