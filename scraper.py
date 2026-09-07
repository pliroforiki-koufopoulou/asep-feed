"""
ΑΣΕΠ Feed Scraper - Cloud Edition v2 (Playwright)
===================================================
Fix: wait_for_selector("h3") για δυναμικό περιεχόμενο JS
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BASE_URL          = "https://info.asep.gr"
ANNOUNCEMENTS_URL = f"{BASE_URL}/announcements-list/7846"
CACHE_FILE        = Path("asep_cache.json")
OUTPUT_FILE       = Path("data.json")
MAX_PAGES         = 5
MAX_DETAIL_PAGES  = 50

MONTHS_EL = {
    'Ιανουαρίου':1,'Φεβρουαρίου':2,'Μαρτίου':3,'Απριλίου':4,
    'Μαΐου':5,'Μαίου':5,'Ιουνίου':6,'Ιουλίου':7,'Αυγούστου':8,
    'Σεπτεμβρίου':9,'Οκτωβρίου':10,'Νοεμβρίου':11,'Δεκεμβρίου':12,
}

SKIP_TITLES = [
    "ΚΕΝΤΡΙΚΗ ΥΠΗΡΕΣΙΑ","ΑΠΟΚΕΝΤΡΩΜΕΝΟ ΤΜΗΜΑ",
    "Main navigation","Γρήγορη Αναζήτηση","Ανακοινώσεις",
]


def parse_date_slash(text):
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', str(text))
    if m:
        d, mo, y = m.groups()
        return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"
    return None

def parse_date_greek(text):
    for m_el, m_num in MONTHS_EL.items():
        pattern = rf'(\d{{1,2}})\s+{re.escape(m_el)}\s+(\d{{4}})'
        m = re.search(pattern, str(text))
        if m:
            day, year = m.groups()
            return f"{year}-{str(m_num).zfill(2)}-{day.zfill(2)}"
    return None

def extract_tags(title):
    tags = []
    for tag in ["ΠΕ","ΤΕ","ΔΕ","ΥΕ","ΙΔΑΧ","ΙΔΟΧ","ΣΟΧ","ΣΜΕ","Μόνιμο","Αναπληρωτές"]:
        if tag.lower() in title.lower():
            tags.append(tag)
    return tags

def detect_status(a):
    dl = a.get("deadline_end")
    if not dl:
        return "active"
    try:
        d = (datetime.strptime(dl, "%Y-%m-%d") - datetime.now()).days
        if d < 0:  return "expired"
        if d <= 7: return "soon"
    except Exception:
        pass
    return "active"

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

def extract_deadlines_from_text(text):
    start = end = None
    m_s = re.search(r'(?:αρχίζει|ξεκινά)\s+στις\s+([\w\s]+?\d{4})', text, re.I)
    m_e = re.search(r'(?:λήγει|λήξει)\s+στις\s+([\w\s]+?\d{4})', text, re.I)
    if m_s: start = parse_date_greek(m_s.group(1))
    if m_e: end   = parse_date_greek(m_e.group(1))

    if not start or not end:
        m2 = re.search(
            r'από\s+(\d{1,2}/\d{1,2}/\d{4})\s+(?:έως|μέχρι|ως)\s+(\d{1,2}/\d{1,2}/\d{4})',
            text, re.I
        )
        if m2:
            start = parse_date_slash(m2.group(1))
            end   = parse_date_slash(m2.group(2))

    if not end:
        m3 = re.search(r'(?:έως|μέχρι|ως)\s+(\d{1,2}/\d{1,2}/\d{4})', text, re.I)
        if m3: end = parse_date_slash(m3.group(1))

    if not end:
        m4 = re.search(
            r'(?:λήγει|μέχρι|καταληκτική)\s+.*?(\d{1,2}\s+\w+\s+\d{4})',
            text, re.I
        )
        if m4: end = parse_date_greek(m4.group(1))

    return start, end


def scrape_listing_page(page, url):
    """Scrape one listing page, waiting for JS content."""
    from bs4 import BeautifulSoup

    items = []
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # KEY FIX: wait for h3 elements that contain announcement titles
        # We wait for an h3 that contains "/" (like "3Κ/2026")
        try:
            page.wait_for_selector("h3", timeout=10000)
            # Extra wait for dynamic content
            time.sleep(2)
        except PWTimeout:
            print(f"    Timeout waiting for h3 — page may be empty")

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Debug: count all h3s
        all_h3 = soup.find_all("h3")
        print(f"    Found {len(all_h3)} h3 elements total")

        for h3 in all_h3:
            title = h3.get_text(strip=True)
            if len(title) < 5:
                continue
            if any(s in title for s in SKIP_TITLES):
                continue

            # Must look like an announcement (contains / or Greek text)
            if len(title) < 8:
                continue

            link = ""
            next_a = h3.find_next("a", href=re.compile(r"/node/\d+"))
            if next_a:
                href = next_a.get("href", "")
                link = (BASE_URL + href) if not href.startswith("http") else href

            date_str = None
            try:
                date_str = parse_date_slash(
                    h3.parent.parent.get_text(" ", strip=True)
                )
            except Exception:
                pass

            items.append({
                "id":             f"asep-{abs(hash(title + (date_str or '')))}",
                "title":          title,
                "announced_date": date_str,
                "deadline_start": None,
                "deadline_end":   None,
                "tags":           extract_tags(title),
                "url":            link,
            })

        has_next = bool(soup.find("a", href=re.compile(r"page=\d+")))
        return items, has_next

    except Exception as e:
        print(f"    Error: {e}")
        return items, False


def run():
    cache = load_cache()
    items = []

    with sync_playwright() as p:
        print("Launching Chromium...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-setuid-sandbox",
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="el-GR",
            extra_http_headers={
                "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
            }
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
        """)

        page = context.new_page()

        # Visit homepage first for cookies
        print("Visiting homepage...")
        try:
            page.goto(BASE_URL, wait_until="networkidle", timeout=25000)
            time.sleep(2)
            print(f"  Homepage title: {page.title()}")
        except Exception as e:
            print(f"  Homepage warning: {e}")

        # Scrape listing pages
        print(f"\n[1/2] Scraping listing pages...")
        for pg in range(MAX_PAGES):
            url = ANNOUNCEMENTS_URL if pg == 0 else f"{ANNOUNCEMENTS_URL}?page={pg}"
            print(f"  Page {pg+1}: {url}")
            page_items, has_next = scrape_listing_page(page, url)
            items.extend(page_items)
            print(f"    Accepted: {len(page_items)} | Total: {len(items)}")
            if not has_next or len(page_items) == 0:
                if pg == 0 and len(page_items) == 0:
                    # Debug: print page title and URL
                    print(f"    Page title: {page.title()}")
                    print(f"    Current URL: {page.url}")
                break
            time.sleep(1.5)

        # Deduplicate
        seen = set()
        unique = []
        for a in items:
            key = a["title"].strip().lower()[:80]
            if key not in seen:
                seen.add(key)
                unique.append(a)
        items = unique
        print(f"\n  Total unique items: {len(items)}")

        # Fetch deadline details
        print(f"\n[2/2] Fetching deadlines for {min(len(items), MAX_DETAIL_PAGES)} items...")
        cached_hits = 0
        fetched = 0

        for i, a in enumerate(items[:MAX_DETAIL_PAGES]):
            if not a["url"]:
                continue

            if a["url"] in cache:
                a["deadline_start"] = cache[a["url"]].get("deadline_start")
                a["deadline_end"]   = cache[a["url"]].get("deadline_end")
                cached_hits += 1
                continue

            try:
                page.goto(a["url"], wait_until="domcontentloaded", timeout=20000)
                page.wait_for_selector("body", timeout=5000)
                time.sleep(0.8)
                text = page.inner_text("body")
                ds, de = extract_deadlines_from_text(text)
                a["deadline_start"] = ds
                a["deadline_end"]   = de
                cache[a["url"]] = {"deadline_start": ds, "deadline_end": de}
                fetched += 1
                if (i+1) % 10 == 0:
                    print(f"  {i+1}/{min(len(items),MAX_DETAIL_PAGES)} "
                          f"(cache:{cached_hits} fetched:{fetched})")
            except Exception as e:
                print(f"  Error {a['url']}: {e}")

        browser.close()

    save_cache(cache)
    print(f"  Cache: {len(cache)} entries")

    def sort_key(a):
        order = {"active":0,"soon":1,"expired":2}
        st = detect_status(a)
        dt = a.get("announced_date") or "0000-00-00"
        try:
            ts = datetime.strptime(dt, "%Y-%m-%d").timestamp()
        except Exception:
            ts = 0
        return (order.get(st,3), -ts)

    items.sort(key=sort_key)

    active  = sum(1 for a in items if detect_status(a) == "active")
    soon    = sum(1 for a in items if detect_status(a) == "soon")
    expired = sum(1 for a in items if detect_status(a) == "expired")
    with_dl = sum(1 for a in items if a.get("deadline_end"))
    with_rng= sum(1 for a in items if a.get("deadline_start") and a.get("deadline_end"))

    print(f"\nΑποτελέσματα:")
    print(f"  Σύνολο: {len(items)} | Ενεργές: {active} | Λήγουν: {soon} | Ληγμένες: {expired}")
    print(f"  Με προθεσμία: {with_dl} | Με εύρος: {with_rng}")

    data = {
        "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total": len(items),
        "announcements": items,
    }

    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Αποθηκεύτηκε → {OUTPUT_FILE}")


if __name__ == "__main__":
    print("=" * 52)
    print("ΑΣΕΠ Scraper — Cloud Edition v2 (Playwright)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 52)
    run()
    print("\nΟλοκληρώθηκε!")
