"""
ΑΣΕΠ Feed Scraper — Τελική Έκδοση
====================================
Τρέχει ΤΟΠΙΚΑ στον υπολογιστή (C:\ASEP\)
- Scrapes: info.asep.gr/announcements-list/7846
- Διαβάζει εύρος προθεσμίας από κάθε ανακοίνωση
- Κρατάει cache (asep_cache.json) για ταχύτητα
- Στέλνει data.json στο GitHub

ΡΥΘΜΙΣΗ: βάλε το GitHub token σου παρακάτω
"""

import json, re, time, base64
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

# ── Ρύθμισε εδώ ─────────────────────────────────
GITHUB_TOKEN = "ΒΑΛΕ_ΤΟ_TOKEN_ΣΟΥ_ΕΔΩ"
GITHUB_USER  = "pliroforiki-koufopoulou"
GITHUB_REPO  = "asep-feed"
GITHUB_FILE  = "data.json"
# ────────────────────────────────────────────────

BASE_URL          = "https://info.asep.gr"
ANNOUNCEMENTS_URL = f"{BASE_URL}/announcements-list/7846"
CACHE_FILE        = Path("asep_cache.json")
OUTPUT_FILE       = Path("data.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

MONTHS_EL = {
    'Ιανουαρίου':1,'Φεβρουαρίου':2,'Μαρτίου':3,'Απριλίου':4,
    'Μαΐου':5,'Μαίου':5,'Ιουνίου':6,'Ιουλίου':7,'Αυγούστου':8,
    'Σεπτεμβρίου':9,'Οκτωβρίου':10,'Νοεμβρίου':11,'Δεκεμβρίου':12,
}

SKIP_TITLES = [
    "ΚΕΝΤΡΙΚΗ ΥΠΗΡΕΣΙΑ", "ΑΠΟΚΕΝΤΡΩΜΕΝΟ ΤΜΗΜΑ",
    "Main navigation", "Γρήγορη Αναζήτηση",
]


# ── Helpers ─────────────────────────────────────

def parse_date_slash(text):
    """28/04/2026 → 2026-04-28"""
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', str(text))
    if m:
        d, mo, y = m.groups()
        return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"
    return None

def parse_date_greek(text):
    """'17 Σεπτεμβρίου 2026' → '2026-09-17'"""
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


# ── Deadline extraction ──────────────────────────

def extract_deadlines(session, url, cache):
    """Επίσκεψη σελίδας ανακοίνωσης → εξαγωγή εύρους προθεσμίας."""
    if url in cache:
        return cache[url].get("deadline_start"), cache[url].get("deadline_end")

    try:
        r = session.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None, None
        text = r.text
        start = end = None

        # Pattern 1: αρχίζει στις X ... λήγει στις Y
        m_s = re.search(r'αρχίζει\s+στις\s+([\w\s]+?\d{4})', text, re.I)
        m_e = re.search(r'λήγει\s+στις\s+([\w\s]+?\d{4})', text, re.I)
        if m_s: start = parse_date_greek(m_s.group(1))
        if m_e: end   = parse_date_greek(m_e.group(1))

        # Pattern 2: από DD/MM/YYYY έως DD/MM/YYYY
        if not start or not end:
            m2 = re.search(
                r'από\s+(\d{1,2}/\d{1,2}/\d{4})\s+(?:έως|μέχρι|ως)\s+(\d{1,2}/\d{1,2}/\d{4})',
                text, re.I
            )
            if m2:
                start = parse_date_slash(m2.group(1))
                end   = parse_date_slash(m2.group(2))

        # Pattern 3: έως DD/MM/YYYY
        if not end:
            m3 = re.search(r'(?:έως|μέχρι|ως)\s+(\d{1,2}/\d{1,2}/\d{4})', text, re.I)
            if m3: end = parse_date_slash(m3.group(1))

        # Pattern 4: λήγει ... Greek date
        if not end:
            m4 = re.search(
                r'(?:λήγει|μέχρι|καταληκτική)\s+.*?(\d{1,2}\s+\w+\s+\d{4})',
                text, re.I
            )
            if m4: end = parse_date_greek(m4.group(1))

        cache[url] = {"deadline_start": start, "deadline_end": end}
        time.sleep(0.4)
        return start, end

    except Exception as e:
        print(f"      Σφάλμα: {e}")
        return None, None


# ── Listing page scraper ─────────────────────────

def scrape_page(session, url):
    items = []
    try:
        r = session.get(
            url,
            headers={**HEADERS, "Referer": BASE_URL + "/"},
            timeout=20
        )
        print(f"  HTTP {r.status_code}")
        if r.status_code != 200:
            return items, False

        soup = BeautifulSoup(r.text, "html.parser")

        for h3 in soup.find_all("h3"):
            title = h3.get_text(strip=True)
            if len(title) < 5 or any(s in title for s in SKIP_TITLES):
                continue

            # Link
            link = ""
            next_a = h3.find_next("a", href=re.compile(r"/node/\d+"))
            if next_a:
                href = next_a.get("href", "")
                link = (BASE_URL + href) if not href.startswith("http") else href

            # Ημερομηνία ανακοίνωσης (στο grandparent)
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
        print(f"  Σφάλμα: {e}")
        return items, False


# ── GitHub push ──────────────────────────────────

def push_to_github(data):
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    hdr = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    sha = None
    try:
        r = requests.get(api_url, headers=hdr, timeout=10)
        if r.status_code == 200:
            sha = r.json().get("sha")
            print(f"  Τρέχον SHA: {sha[:8]}...")
    except Exception as e:
        print(f"  Προειδοποίηση: {e}")

    content_b64 = base64.b64encode(
        json.dumps(data, ensure_ascii=False, indent=2).encode()
    ).decode()

    payload = {
        "message": f"Update: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "content": content_b64,
        "branch": "main",
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(api_url, headers=hdr, json=payload, timeout=20)
    if r.status_code in [200, 201]:
        print(f"  Επιτυχής αποστολή στο GitHub! (status {r.status_code})")
        return True
    else:
        print(f"  Αποτυχία GitHub push: {r.status_code}")
        return False


# ── Main ─────────────────────────────────────────

def main():
    print("=" * 52)
    print("ΑΣΕΠ Feed Scraper — Τελική Έκδοση")
    print(f"Έναρξη: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 52)

    cache = load_cache()
    items = []
    session = requests.Session()

    # Cookies από homepage
    try:
        print("Λήψη cookies...")
        session.get(BASE_URL, headers=HEADERS, timeout=15)
        time.sleep(1)
    except Exception as e:
        print(f"  Προειδοποίηση: {e}")

    # Βήμα 1: Λίστα ανακοινώσεων
    print("\n[1/3] Συλλογή ανακοινώσεων...")
    for pg in range(5):
        url = ANNOUNCEMENTS_URL if pg == 0 else f"{ANNOUNCEMENTS_URL}?page={pg}"
        print(f"  Σελίδα {pg+1}: {url}")
        page_items, has_next = scrape_page(session, url)
        items.extend(page_items)
        print(f"    {len(page_items)} ανακοινώσεις | Σύνολο: {len(items)}")
        if not has_next or len(page_items) == 0:
            break
        time.sleep(1.5)

    # Αφαίρεση διπλοτύπων
    seen = set()
    unique = []
    for a in items:
        key = a["title"].strip().lower()[:80]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    items = unique
    print(f"\n  Μοναδικές ανακοινώσεις: {len(items)}")

    # Βήμα 2: Εύρος προθεσμίας
    print(f"\n[2/3] Ανάκτηση προθεσμιών ({len(items)} σελίδες)...")
    cached_hits = fetched = 0
    for i, a in enumerate(items):
        if not a["url"]:
            continue
        already = a["url"] in cache
        ds, de = extract_deadlines(session, a["url"], cache)
        a["deadline_start"] = ds
        a["deadline_end"]   = de
        if already:
            cached_hits += 1
        else:
            fetched += 1
        if (i+1) % 10 == 0:
            print(f"  {i+1}/{len(items)} (cache: {cached_hits}, νέες: {fetched})")

    save_cache(cache)
    print(f"  Cache αποθηκεύτηκε ({len(cache)} εγγραφές)")

    # Ταξινόμηση
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

    # Στατιστικά
    active  = sum(1 for a in items if detect_status(a) == "active")
    soon    = sum(1 for a in items if detect_status(a) == "soon")
    expired = sum(1 for a in items if detect_status(a) == "expired")
    with_dl = sum(1 for a in items if a.get("deadline_end"))
    with_rng= sum(1 for a in items if a.get("deadline_start") and a.get("deadline_end"))

    data = {
        "last_updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "total": len(items),
        "announcements": items,
    }

    print(f"\nΑποτελέσματα:")
    print(f"  Σύνολο: {len(items)} | Ενεργές: {active} | Λήγουν: {soon} | Ληγμένες: {expired}")
    print(f"  Με προθεσμία: {with_dl} | Με εύρος: {with_rng}")

    # Αποθήκευση τοπικά
    OUTPUT_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Αποθηκεύτηκε τοπικά → {OUTPUT_FILE}")

    # Βήμα 3: Αποστολή στο GitHub
    print("\n[3/3] Αποστολή στο GitHub...")
    if GITHUB_TOKEN == "ΒΑΛΕ_ΤΟ_TOKEN_ΣΟΥ_ΕΔΩ":
        print("  ΣΦΑΛΜΑ: Το GitHub token δεν έχει οριστεί!")
        print("  Άνοιξε το αρχείο με Notepad και βάλε το token σου.")
    else:
        push_to_github(data)

    print(f"\nΟλοκληρώθηκε: {datetime.now().strftime('%H:%M')}")


if __name__ == "__main__":
    main()
