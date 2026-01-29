import requests
from datetime import datetime
from pathlib import Path
import html

VENUE_ID = 270
API_URL = f"https://www.bilesuparadize.lv/api/venue/{VENUE_ID}/repertoire"

# SVARĪGI: rakstām tieši to failu, ko atver GitHub Pages
OUTPUT_HTML = Path("talsu_kc_report.html")

def fetch_events():
    r = requests.get(API_URL, timeout=30)
    r.raise_for_status()
    return r.json()

def get_title(ev):
    perf = ev.get("performance") or {}
    titles = perf.get("titles") or {}
    return titles.get("lv") or titles.get("en") or "—"

def get_url(ev):
    urls = ev.get("urls") or {}
    return urls.get("lv") or urls.get("en") or ""

def get_available_total(ev):
    total = 0
    for p in (ev.get("prices") or []):
        try:
            total += int(p.get("count", 0) or 0)
        except Exception:
            pass
    return total

def badge_class(free: int) -> str:
    if free <= 0:
        return "zero"
    if free < 50:
        return "low"
    if free < 200:
        return "mid"
    return "high"

def build_html(events):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = []
    for ev in events:
        dt_raw = ev.get("dateTime") or ""
        date = dt_raw[:10]
        time = dt_raw[11:16]
        title = get_title(ev)
        url = get_url(ev)
        free = get_available_total(ev)
        cls = badge_class(free)

        rows.append(f"""
          <tr data-title="{html.escape(title.lower())}" data-date="{html.escape(date)}" data-free="{free}">
            <td class="mono">{html.escape(date)}</td>
            <td class="mono">{html.escape(time)}</td>
            <td class="title">
              <a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(title)}</a>
            </td>
            <td class="free"><span class="badge {cls}">{free}</span></td>
            <td class="open"><a class="btn" href="{html.escape(url)}" target="_blank" rel="noopener">Atvērt</a></td>
          </tr>
        """)

    rows_html = "\n".join(rows) if rows else '<tr><td colspan="5" class="empty">Nav atrasts neviens pasākums.</td></tr>'

    return f"""<!doctype html>
<html lang="lv">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Talsu KC — biļešu atskaite</title>
  <meta name="color-scheme" content="dark light" />
  <style>
    :root {{
      --bg: #0b1020;
      --card: rgba(255,255,255,.06);
      --card2: rgba(255,255,255,.04);
      --text: #eaf0ff;
      --muted: rgba(234,240,255,.72);
      --line: rgba(255,255,255,.10);
      --shadow: 0 22px 70px rgba(0,0,0,.40);
      --link: #8fd0ff;

      --good: rgba(34,197,94,.20);
      --good-b: rgba(34,197,94,.55);
      --good-t: #b7f7cf;

      --mid: rgba(245,158,11,.22);
      --mid-b: rgba(245,158,11,.55);
      --mid-t: #ffe3b2;

      --low: rgba(239,68,68,.22);
      --low-b: rgba(239,68,68,.55);
      --low-t: #ffd0d0;

      --zero: rgba(148,163,184,.18);
      --zero-b: rgba(148,163,184,.45);
      --zero-t: #e2e8f0;
    }}

    @media (prefers-color-scheme: light) {{
      :root {{
        --bg: #f4f6fb;
        --card: rgba(10,20,40,.06);
        --card2: rgba(10,20,40,.04);
        --text: #0c1222;
        --muted: rgba(12,18,34,.72);
        --line: rgba(12,18,34,.12);
        --shadow: 0 22px 70px rgba(10,20,40,.12);
        --link: #0066cc;
      }}
    }}

    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background:
        radial-gradient(900px 500px at 18% 0%, rgba(99,102,241,.22), transparent 60%),
        radial-gradient(900px 500px at 85% 10%, rgba(14,165,233,.18), transparent 55%),
        var(--bg);
      color: var(--text);
    }}

    .wrap {{
      max-width: 1160px;
      margin: 26px auto;
      padding: 0 16px 40px;
    }}

    .top {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 14px;
      align-items: end;
      margin-bottom: 14px;
    }}

    h1 {{
      margin: 0;
      font-size: 20px;
      letter-spacing: .2px;
    }}

    .meta {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 13px;
    }}

    .right {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
      align-items: center;
    }}

    .pill {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 8px 10px;
      box-shadow: var(--shadow);
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}

    .search {{
      display: flex;
      gap: 8px;
      align-items: center;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 8px 10px;
      box-shadow: var(--shadow);
      min-width: 280px;
    }}
    .search input {{
      width: 100%;
      border: 0;
      outline: none;
      background: transparent;
      color: var(--text);
      font-size: 14px;
    }}
    .search input::placeholder {{
      color: var(--muted);
    }}

    .card {{
      background: var(--card2);
      border: 1px solid var(--line);
      border-radius: 14px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
    }}

    thead th {{
      position: sticky;
      top: 0;
      z-index: 5;
      text-align: left;
      font-size: 12px;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--muted);
      background: rgba(0,0,0,.20);
      backdrop-filter: blur(10px);
      border-bottom: 1px solid var(--line);
      padding: 12px 12px;
      cursor: pointer;
      user-select: none;
    }}

    tbody td {{
      border-bottom: 1px solid var(--line);
      padding: 12px 12px;
      vertical-align: middle;
      font-size: 14px;
    }}

    tbody tr:hover {{
      background: rgba(255,255,255,.04);
    }}

    .mono {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}

    .title a {{
      color: var(--text);
      text-decoration: none;
      font-weight: 650;
    }}
    .title a:hover {{
      text-decoration: underline;
    }}

    .badge {{
      display: inline-flex;
      min-width: 64px;
      justify-content: center;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid;
      font-weight: 800;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }}
    .badge.high {{ background: var(--good); border-color: var(--good-b); color: var(--good-t); }}
    .badge.mid  {{ background: var(--mid);  border-color: var(--mid-b);  color: var(--mid-t);  }}
    .badge.low  {{ background: var(--low);  border-color: var(--low-b);  color: var(--low-t);  }}
    .badge.zero {{ background: var(--zero); border-color: var(--zero-b); color: var(--zero-t); }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 8px 10px;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.06);
      color: var(--link);
      text-decoration: none;
      font-weight: 650;
      font-size: 13px;
    }}
    .btn:hover {{
      background: rgba(255,255,255,.10);
    }}

    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 28px 12px;
    }}

    @media (max-width: 720px) {{
      .top {{ grid-template-columns: 1fr; }}
      .right {{ justify-content: flex-start; }}
      thead th:nth-child(5), tbody td:nth-child(5) {{ display:none; }}
      .search {{ min-width: 0; width: 100%; }}
    }}
  </style>
</head>

<body>
  <div class="wrap">
    <div class="top">
      <div>
        <h1>Talsu Kultūras centrs — pasākumi & brīvās biļetes</h1>
        <div class="meta">Atjaunots: <strong>{html.escape(now)}</strong></div>
      </div>

      <div class="right">
        <div class="search">
          🔎 <input id="q" placeholder="Meklēt pasākumu…" autocomplete="off" />
        </div>
        <div class="pill">Venue ID: <strong>{VENUE_ID}</strong> &nbsp;•&nbsp; Pasākumi: <strong id="cnt">{len(events)}</strong></div>
      </div>
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th data-sort="date" style="width:120px">Datums</th>
            <th data-sort="time" style="width:90px">Laiks</th>
            <th data-sort="title">Pasākums</th>
            <th data-sort="free" style="width:140px">Brīvas</th>
            <th style="width:110px">Saite</th>
          </tr>
        </thead>
        <tbody id="tb">
          {rows_html}
        </tbody>
      </table>
    </div>
  </div>

  <script>
    const q = document.getElementById('q');
    const tb = document.getElementById('tb');
    const cnt = document.getElementById('cnt');
    const headers = Array.from(document.querySelectorAll('thead th[data-sort]'));
    let dir = 1;
    let sortKey = 'date';

    function rows() {{
      return Array.from(tb.querySelectorAll('tr'));
    }}

    function applyFilter() {{
      const term = (q.value || '').trim().toLowerCase();
      let visible = 0;
      rows().forEach(r => {{
        const title = r.getAttribute('data-title') || '';
        const show = !term || title.includes(term);
        r.style.display = show ? '' : 'none';
        if (show) visible++;
      }});
      cnt.textContent = visible;
    }}

    function getSortVal(r, key) {{
      if (key === 'free') return parseInt(r.getAttribute('data-free') || '0', 10);
      if (key === 'title') return (r.getAttribute('data-title') || '');
      if (key === 'time') return r.children[1].innerText.trim();
      return r.getAttribute('data-date') || '';
    }}

    function sortTable(key) {{
      sortKey = key;
      const rs = rows();
      rs.sort((a,b) => {{
        const va = getSortVal(a, key);
        const vb = getSortVal(b, key);
        if (va < vb) return -1 * dir;
        if (va > vb) return  1 * dir;
        return 0;
      }});
      rs.forEach(r => tb.appendChild(r));
    }}

    headers.forEach(h => {{
      h.addEventListener('click', () => {{
        const key = h.getAttribute('data-sort');
        if (sortKey === key) dir *= -1; else dir = 1;
        sortTable(key);
        applyFilter();
      }});
    }});

    q.addEventListener('input', applyFilter);

    sortTable('date');
    applyFilter();
  </script>
</body>
</html>
"""

def main():
    events = fetch_events()
    events = sorted(events, key=lambda e: e.get("dateTime", ""))
    OUTPUT_HTML.write_text(build_html(events), encoding="utf-8")
    print("HTML saglabāts:", OUTPUT_HTML)

if __name__ == "__main__":
    main()
