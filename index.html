<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ΑΣΕΠ — Ανακοινώσεις</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Serif:wght@400;600&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --ink:      #0D1B2A;
  --ink-mid:  #3D5166;
  --ink-soft: #7B93A8;
  --rule:     #D6DEE6;
  --bg:       #F0F4F7;
  --white:    #FFFFFF;
  --active:   #0057A8;
  --active-bg:#E6EFF8;
  --expired:  #94A3B0;
  --expired-bg:#EDF0F3;
  --warn:     #B34A00;
  --warn-bg:  #FEF0E6;
  --green:    #1A6B3C;
  --green-bg: #E6F4ED;
}

body {
  font-family: 'IBM Plex Sans', sans-serif;
  background: var(--bg);
  color: var(--ink);
  min-height: 100vh;
  font-size: 15px;
  line-height: 1.5;
}

/* ── Header ── */
header {
  background: var(--ink);
  color: var(--white);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  position: sticky;
  top: 0;
  z-index: 50;
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-mark {
  width: 40px; height: 40px;
  background: var(--active);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'IBM Plex Serif', serif;
  font-size: 18px; font-weight: 600;
  color: white; flex-shrink: 0;
}

.logo-text { line-height: 1.2; }
.logo-title {
  font-family: 'IBM Plex Serif', serif;
  font-size: 1.15rem; font-weight: 600;
}
.logo-sub { font-size: 0.72rem; opacity: 0.55; letter-spacing: 0.04em; }

.header-right {
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}

.last-updated {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.5);
}

.refresh-btn {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: white;
  padding: 7px 16px;
  border-radius: 6px;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.82rem;
  cursor: pointer;
  transition: background 0.15s;
  display: flex; align-items: center; gap: 6px;
}
.refresh-btn:hover { background: rgba(255,255,255,0.18); }
.refresh-btn .spin { display: inline-block; }
.refresh-btn.loading .spin { animation: rotate 0.8s linear infinite; }
@keyframes rotate { to { transform: rotate(360deg); } }

/* ── Stats bar ── */
.stats-bar {
  background: var(--white);
  border-bottom: 1px solid var(--rule);
  padding: 14px 32px;
  display: flex;
  gap: 28px;
  align-items: center;
  flex-wrap: wrap;
}

.stat {
  display: flex; align-items: center; gap: 8px;
}
.stat-pill {
  width: 8px; height: 8px; border-radius: 50%;
}
.stat-pill.active  { background: var(--active); }
.stat-pill.expired { background: var(--expired); }
.stat-pill.soon    { background: var(--warn); }

.stat-num {
  font-family: 'IBM Plex Serif', serif;
  font-size: 1.15rem; font-weight: 600;
}
.stat-lbl { font-size: 0.75rem; color: var(--ink-soft); }

.stat-divider { width: 1px; height: 28px; background: var(--rule); }

/* ── Main ── */
main {
  max-width: 1120px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}

/* ── Controls ── */
.controls {
  display: flex;
  gap: 10px;
  margin-bottom: 22px;
  flex-wrap: wrap;
  align-items: center;
}

.tab-group {
  display: flex;
  background: var(--white);
  border: 1px solid var(--rule);
  border-radius: 8px;
  overflow: hidden;
}
.tab {
  padding: 8px 18px;
  border: none;
  background: none;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.84rem;
  font-weight: 500;
  color: var(--ink-soft);
  cursor: pointer;
  border-right: 1px solid var(--rule);
  transition: all 0.12s;
}
.tab:last-child { border-right: none; }
.tab:hover { color: var(--ink); background: var(--bg); }
.tab.active { background: var(--ink); color: white; }

.search-wrap {
  flex: 1; min-width: 200px;
  position: relative;
}
.search-wrap svg {
  position: absolute; left: 11px; top: 50%;
  transform: translateY(-50%);
  color: var(--ink-soft);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 9px 14px 9px 36px;
  border: 1px solid var(--rule);
  border-radius: 8px;
  background: var(--white);
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.88rem;
  color: var(--ink);
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: var(--active); }

/* ── Grid ── */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

/* ── Card ── */
.card {
  background: var(--white);
  border: 1px solid var(--rule);
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.15s, transform 0.15s;
}
.card:hover {
  box-shadow: 0 4px 20px rgba(13,27,42,0.09);
  transform: translateY(-2px);
}

.card-top {
  padding: 16px 18px 12px;
  border-bottom: 1px solid var(--rule);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}
.status-badge.active  { background: var(--active-bg);  color: var(--active); }
.status-badge.expired { background: var(--expired-bg); color: var(--expired); }
.status-badge.soon    { background: var(--warn-bg);    color: var(--warn); }
.status-badge::before {
  content: ''; width: 6px; height: 6px; border-radius: 50%;
  background: currentColor; display: inline-block;
}

.card-body {
  padding: 14px 18px;
  flex: 1;
}

.card-title {
  font-family: 'IBM Plex Serif', serif;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.45;
  color: var(--ink);
  margin-bottom: 12px;
}

.card-dates {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.date-block { flex: 1; min-width: 100px; }
.date-lbl {
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--ink-soft);
  margin-bottom: 2px;
  font-weight: 600;
}
.date-val {
  font-size: 0.86rem;
  font-weight: 500;
  color: var(--ink);
}
.date-val.range {
  display: flex; flex-direction: column; gap: 1px;
}
.date-val.range span { font-weight: 400; color: var(--ink-mid); }
.date-val.range span.end { font-weight: 600; color: var(--ink); }
.date-val.expiring { color: var(--warn); }

.tags {
  display: flex; flex-wrap: wrap; gap: 5px;
  margin-top: 12px;
}
.tag {
  background: var(--bg);
  color: var(--ink-mid);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.card-footer {
  padding: 10px 18px;
  border-top: 1px solid var(--rule);
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.deadline-track {
  flex: 1;
  height: 3px;
  background: var(--rule);
  border-radius: 2px;
  overflow: hidden;
}
.deadline-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s ease;
}
.deadline-fill.ok      { background: var(--green); }
.deadline-fill.warning { background: var(--warn); }
.deadline-fill.done    { background: var(--expired); }

.more-btn {
  background: var(--ink);
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: background 0.15s;
  white-space: nowrap;
}
.more-btn:hover { background: var(--active); }

/* ── Empty / Loading ── */
.empty {
  grid-column: 1/-1;
  text-align: center;
  padding: 80px 20px;
  color: var(--ink-soft);
}
.empty-icon { font-size: 2.5rem; margin-bottom: 12px; }
.empty h3 { font-family: 'IBM Plex Serif', serif; font-size: 1.2rem; color: var(--ink); margin-bottom: 6px; }

.loading {
  grid-column: 1/-1;
  text-align: center;
  padding: 80px 20px;
}
.spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--rule);
  border-top-color: var(--active);
  border-radius: 50%;
  animation: rotate 0.7s linear infinite;
  margin: 0 auto 14px;
}

/* ── Footer ── */
footer {
  text-align: center;
  padding: 24px;
  font-size: 0.78rem;
  color: var(--ink-soft);
  border-top: 1px solid var(--rule);
  margin-top: 20px;
}
footer a { color: var(--active); text-decoration: none; }

@media (max-width: 600px) {
  header { padding: 16px; }
  main { padding: 16px 14px 40px; }
  .stats-bar { padding: 12px 16px; gap: 16px; }
  .grid { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-mark">Α</div>
    <div class="logo-text">
      <div class="logo-title">ΑΣΕΠ Ανακοινώσεις</div>
      <div class="logo-sub">Αυτόματη παρακολούθηση προκηρύξεων</div>
    </div>
  </div>
  <div class="header-right">
    <span class="last-updated" id="lastUpdated">Φόρτωση…</span>
    <button class="refresh-btn" id="refreshBtn" onclick="loadData(true)">
      <span class="spin">↻</span> Ανανέωση
    </button>
  </div>
</header>

<div class="stats-bar">
  <div class="stat">
    <div class="stat-pill active"></div>
    <div>
      <div class="stat-num" id="statActive">—</div>
      <div class="stat-lbl">Ενεργές</div>
    </div>
  </div>
  <div class="stat-divider"></div>
  <div class="stat">
    <div class="stat-pill soon"></div>
    <div>
      <div class="stat-num" id="statSoon">—</div>
      <div class="stat-lbl">Λήγουν σύντομα</div>
    </div>
  </div>
  <div class="stat-divider"></div>
  <div class="stat">
    <div class="stat-pill expired"></div>
    <div>
      <div class="stat-num" id="statExpired">—</div>
      <div class="stat-lbl">Ληγμένες</div>
    </div>
  </div>
  <div class="stat-divider"></div>
  <div class="stat">
    <div>
      <div class="stat-num" id="statTotal">—</div>
      <div class="stat-lbl">Σύνολο</div>
    </div>
  </div>
</div>

<main>
  <div class="controls">
    <div class="tab-group">
      <button class="tab active" onclick="setFilter('active', this)">Ενεργές</button>
      <button class="tab" onclick="setFilter('soon', this)">Λήγουν σύντομα</button>
      <button class="tab" onclick="setFilter('expired', this)">Ληγμένες</button>
      <button class="tab" onclick="setFilter('all', this)">Όλες</button>
    </div>
    <div class="search-wrap">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <input class="search-input" type="text" id="searchInput"
             placeholder="Αναζήτηση ανακοίνωσης…" oninput="render()">
    </div>
  </div>

  <div class="grid" id="grid">
    <div class="loading"><div class="spinner"></div><p>Φόρτωση…</p></div>
  </div>
</main>

<footer>
  Δεδομένα από <a href="https://info.asep.gr/announcements-list/7846" target="_blank">info.asep.gr</a>
</footer>

<script>
const DATA_URL = './data.json';
let allData = [];
let currentFilter = 'active';

const MONTHS_EL = {
  'Ιανουαρίου':1,'Φεβρουαρίου':2,'Μαρτίου':3,'Απριλίου':4,
  'Μαΐου':5,'Ιουνίου':6,'Ιουλίου':7,'Αυγούστου':8,
  'Σεπτεμβρίου':9,'Οκτωβρίου':10,'Νοεμβρίου':11,'Δεκεμβρίου':12,
  'Ιαν':1,'Φεβ':2,'Μαρ':3,'Απρ':4,'Μαΐ':5,'Ιουν':6,
  'Ιουλ':7,'Αυγ':8,'Σεπτ':9,'Οκτ':10,'Νοε':11,'Δεκ':12,
};

const SHORT_MONTHS = ['','Ιαν','Φεβ','Μαρ','Απρ','Μαΐ','Ιουν','Ιουλ','Αυγ','Σεπτ','Οκτ','Νοε','Δεκ'];

function fmtDate(iso) {
  if (!iso) return '—';
  const [y,m,d] = iso.split('-');
  return `${parseInt(d)} ${SHORT_MONTHS[parseInt(m)]} ${y}`;
}

function daysLeft(iso) {
  if (!iso) return null;
  const diff = new Date(iso) - new Date();
  return Math.round(diff / 86400000);
}

function deadlineStatus(a) {
  // Uses deadline_end if available, else announced_date as fallback
  const dl = a.deadline_end || null;
  if (!dl) return 'active';
  const d = daysLeft(dl);
  if (d < 0) return 'expired';
  if (d <= 7) return 'soon';
  return 'active';
}

function progressPct(a) {
  const start = a.deadline_start || a.announced_date;
  const end   = a.deadline_end;
  if (!start || !end) return 0;
  const total = new Date(end) - new Date(start);
  const elapsed = new Date() - new Date(start);
  if (total <= 0) return 100;
  return Math.min(100, Math.max(0, (elapsed / total) * 100));
}

async function loadData(showSpin = false) {
  const btn = document.getElementById('refreshBtn');
  if (showSpin) btn.classList.add('loading');
  try {
    const r = await fetch(DATA_URL + '?t=' + Date.now());
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const json = await r.json();
    allData = json.announcements || [];
    document.getElementById('lastUpdated').textContent =
      'Ενημ. ' + (json.last_updated || '—');
    updateStats();
    render();
  } catch(e) {
    document.getElementById('grid').innerHTML = `
      <div class="empty">
        <div class="empty-icon">📭</div>
        <h3>Δεν φορτώθηκαν δεδομένα</h3>
        <p>Τρέξε τον scraper για να ενημερωθεί το dashboard.</p>
      </div>`;
  } finally {
    btn.classList.remove('loading');
  }
}

function updateStats() {
  const statuses = allData.map(deadlineStatus);
  document.getElementById('statActive').textContent  = statuses.filter(s=>s==='active').length;
  document.getElementById('statSoon').textContent    = statuses.filter(s=>s==='soon').length;
  document.getElementById('statExpired').textContent = statuses.filter(s=>s==='expired').length;
  document.getElementById('statTotal').textContent   = allData.length;
}

function setFilter(f, el) {
  currentFilter = f;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  render();
}

function render() {
  const q = document.getElementById('searchInput').value.toLowerCase().trim();
  const filtered = allData.filter(a => {
    const st = deadlineStatus(a);
    const statusOk = currentFilter === 'all' || st === currentFilter;
    const searchOk = !q || a.title.toLowerCase().includes(q);
    return statusOk && searchOk;
  });

  const grid = document.getElementById('grid');
  if (filtered.length === 0) {
    grid.innerHTML = `<div class="empty">
      <div class="empty-icon">🔍</div>
      <h3>Δεν βρέθηκαν αποτελέσματα</h3>
      <p>Δοκίμασε διαφορετικά φίλτρα ή αναζήτηση.</p>
    </div>`;
    return;
  }

  grid.innerHTML = filtered.map(a => {
    const st  = deadlineStatus(a);
    const pct = progressPct(a);
    const dl  = daysLeft(a.deadline_end);
    const fillCls = st === 'expired' ? 'done' : st === 'soon' ? 'warning' : 'ok';

    const statusLabel = { active: 'Ενεργή', expired: 'Ληγμένη', soon: 'Λήγει σύντομα' }[st];

    // Deadline display
    let deadlineHtml = '';
    if (a.deadline_start && a.deadline_end) {
      const expiring = st === 'soon' ? ' expiring' : '';
      deadlineHtml = `<div class="date-block">
        <div class="date-lbl">Προθεσμία υποβολής</div>
        <div class="date-val range${expiring}">
          <span>${fmtDate(a.deadline_start)}</span>
          <span class="end">έως ${fmtDate(a.deadline_end)}${dl !== null && dl >= 0 ? ` (${dl} μέρες)` : ''}</span>
        </div>
      </div>`;
    } else if (a.deadline_end) {
      const expiring = st === 'soon' ? ' expiring' : '';
      deadlineHtml = `<div class="date-block">
        <div class="date-lbl">Καταληκτική</div>
        <div class="date-val${expiring}">${fmtDate(a.deadline_end)}${dl !== null && dl >= 0 ? ` (${dl} μέρες)` : ''}</div>
      </div>`;
    }

    const tags = (a.tags || []).filter(t => t !== 'ΑΣΕΠ').map(t =>
      `<span class="tag">${t}</span>`).join('');

    return `<div class="card">
      <div class="card-top">
        <span class="status-badge ${st}">${statusLabel}</span>
      </div>
      <div class="card-body">
        <div class="card-title">${a.title}</div>
        <div class="card-dates">
          <div class="date-block">
            <div class="date-lbl">Ανακοίνωση</div>
            <div class="date-val">${fmtDate(a.announced_date)}</div>
          </div>
          ${deadlineHtml}
        </div>
        ${tags ? `<div class="tags">${tags}</div>` : ''}
      </div>
      <div class="card-footer">
        <div class="deadline-track">
          <div class="deadline-fill ${fillCls}" style="width:${pct}%"></div>
        </div>
        ${a.url ? `<a class="more-btn" href="${a.url}" target="_blank">Περισσότερα ↗</a>` : ''}
      </div>
    </div>`;
  }).join('');
}

loadData();
</script>
</body>
</html>
