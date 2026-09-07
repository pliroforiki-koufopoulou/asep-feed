"""
ΑΣΕΠ Feed Scraper - Cloud Edition (Playwright)
================================================
Χρησιμοποιεί Playwright (headless Chrome) για να παρακάμψει
το bot protection του info.asep.gr.

Τρέχει μέσω GitHub Actions - δεν χρειάζεται τοπικός υπολογιστής.
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
MAX_DETAIL_PAGES  = 50   # max ανακοινώσεις για detail fetch

MONTHS_EL = {
    'Ιανουαρίου':1,'Φεβρουαρίου':2,'Μαρτίου':3,'Απριλίου':4,
    'Μαΐου':5,'Μαίου':5,'Ιουνίου':6,'Ιουλίου':7,'Αυγούστου':8,
    'Σεπτεμβρίου':9,'Οκτωβρίου':10,'Νοεμβρίου':11,'Δεκεμβρίου':12,
}

SKIP_TITLES = [
    "ΚΕΝΤΡΙΚΗ ΥΠΗΡΕΣΙΑ","ΑΠΟΚΕΝΤΡΩΜΕΝΟ ΤΜΗΜΑ",
    "Main navigation","Γρήγορη Αναζήτηση",
]


# ── Date helpers ──────────────────────────────────

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


# ── Deadline extraction from page text ───────────

def extract_deadlines_from_text(text):
    start = end = None

    # Pattern: αρχίζει/ξεκινά ... λήγει/λήξει
    m_s = re.search(r'(?:αρχίζει|ξεκινά)\s+στις\s+([\w\s]+?\d{4})', text, re.I)
    m_e = re.search(r'(?:λήγει|λήξει)\s+στις\s+([\w\s]+?\d{4})',     text, re.I)
    if m_s: start = parse_date_greek(m_s.group(1))
    if m_e: end   = parse_date_greek(m_e.group(1))

    # Pattern: από DD/MM/YYYY ... έως DD/MM/YYYY
    if not start or not end:
        m2 = re.search(
            r'από\s+(\d{1,2}/\d{1,2}/\d{4})\s+(?:έως|μέχρι|ως)\s+(\d{1,2}/\d{1,2}/\d{4})',
            text, re.I
        )
        if m2:
            start = parse_date_slash(m2.group(1))
            end   = parse_date_slash(m2.group(2))

    # Pattern: έως / μέχρι DD/MM/YYYY
    if not end:
        m3 = re.search(r'(?:έως|μέχρι|ως)\s+(\d{1,2}/\d{1,2}/\d{4})', text, re.I)
        if m3: end = parse_date_slash(m3.group(1))

    # Pattern: λήγει ... greek month date
    if not end:
        m4 = re.search(
            r'(?:λήγει|μέχρι|καταληκτική)\s+.*?(\d{1,2}\s+\w+\s+\d{4})',
            text, re.I
        )
        if m4: end = parse_date_greek(m4.group(1))

    return start, end


# ── Main scraper ──────────────────────────────────

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
        )

        # Mask automation signals
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)

        page = context.new_page()

        # ── Step 1: Visit homepage first (get cookies) ──
        print(f"Visiting homepage...")
        try:
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=20000)
            time.sleep(2)
        except Exception as e:
            print(f"  Homepage warning: {e}")

        # ── Step 2: Scrape listing pages ──
        print(f"\n[1/2] Scraping listing pages...")
        for pg in range(MAX_PAGES):
            url = ANNOUNCEMENTS_URL if pg == 0 else f"{ANNOUNCEMENTS_URL}?page={pg}"
            print(f"  Page {pg+1}: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=25000)
                time.sleep(1.5)

                html = page.content()
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")

                page_items = []
                for h3 in soup.find_all("h3"):
                    title = h3.get_text(strip=True)
                    if len(title) < 5 or any(s in title for s in SKIP_TITLES):
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

                    page_items.append({
                        "id":             f"asep-{abs(hash(title + (date_str or '')))}",
                        "title":          title,
                        "announced_date": date_str,
                        "deadline_start": None,
                        "deadline_end":   None,
                        "tags":           extract_tags(title),
                        "url":            link,
                    })

                items.extend(page_items)
                print(f"    {len(page_items)} items | total {len(items)}")

                has_next = bool(soup.find("a", href=re.compile(r"page=\d+")))
                if not has_next or len(page_items) == 0:
                    break

            except PWTimeout:
                print(f"  Timeout on page {pg+1} — stopping")
                break
            except Exception as e:
                print(f"  Error: {e}")
                break

        # Deduplicate
        seen = set()
        unique = []
        for a in items:
            key = a["title"].strip().lower()[:80]
            if key not in seen:
                seen.add(key)
                unique.append(a)
        items = unique

        # ── Step 3: Fetch deadline details ──
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
                time.sleep(0.8)
                text = page.inner_text("body")
                ds, de = extract_deadlines_from_text(text)
                a["deadline_start"] = ds
                a["deadline_end"]   = de
                cache[a["url"]] = {"deadline_start": ds, "deadline_end": de}
                fetched += 1

                if (i+1) % 10 == 0:
                    print(f"  {i+1}/{min(len(items), MAX_DETAIL_PAGES)} "
                          f"(cache: {cached_hits}, fetched: {fetched})")
            except Exception as e:
                print(f"  Error fetching {a['url']}: {e}")

        browser.close()

    save_cache(cache)
    print(f"  Cache: {len(cache)} entries saved")

    # Sort
    def sort_key(a):
        order = {"active":0,"soon":1,"expired":2}
        st = detect_status(a)
        dt = a.get("announced_date") or "0000-00-00"
        try:
            ts = datetime.strptime(dt, "%Y-%m-%d").timestamp()
        except Exception:
            ts = 0
        return (order.get(st, 3), -ts)

    items.sort(key=sort_key)

    # Stats
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
    print("ΑΣΕΠ Scraper — Cloud Edition (Playwright)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 52)
    run()
    print("\nΟλοκληρώθηκε!")
