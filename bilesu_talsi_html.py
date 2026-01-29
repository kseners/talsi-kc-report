import requests
from datetime import datetime
from pathlib import Path
import html

VENUE_ID = 270
API_URL = f"https://www.bilesuparadize.lv/api/venue/{VENUE_ID}/repertoire"
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
        except:
            pass
    return total

def badge_class(free):
    if free == 0:
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
        <tr data-title="{html.escape(title.lower())}" data-free="{free}">
            <td class="mono">{date}</td>
            <td class="mono">{time}</td>
            <td class="title">
                <a href="{url}" target="_blank">{html.escape(title)}</a>
            </td>
            <td><span class="badge {cls}">{free}</span></td>
            <td><a class="btn" href="{url}" target="_blank">Atvērt</a></td>
        </tr>
        """)

    rows_html = "\n".join(rows)

    return f"""
<!doctype html>
<html lang="lv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Talsu KC biļetes</title>

<style>
body {{
    margin:0;
    font-family:system-ui;
    background:#0f172a;
    color:white;
}}

.wrap {{
    max-width:1100px;
    margin:40px auto;
    padding:20px;
}}

h1 {{margin:0}}

.meta {{opacity:.7;margin-bottom:20px}}

input {{
    padding:10px;
    width:300px;
    border-radius:8px;
    border:none;
}}

table {{
    width:100%;
    border-collapse:collapse;
    background:#111827;
    border-radius:10px;
    overflow:hidden;
}}

th,td {{
    padding:12px;
    border-bottom:1px solid #1f2937;
}}

th {{
    background:#1f2937;
    cursor:pointer;
}}

tr:hover {{
    background:#1f2937;
}}

.badge {{
    padding:6px 12px;
    border-radius:20px;
    font-weight:bold;
}}

.high {{background:#14532d}}
.mid {{background:#854d0e}}
.low {{background:#7f1d1d}}
.zero {{background:#374151}}

.btn {{
    background:#2563eb;
    padding:8px 12px;
    border-radius:6px;
    text-decoration:none;
    color:white;
}}

.mono {{
    opacity:.7;
    font-family:monospace;
}}
</style>
</head>

<body>

<div class="wrap">

<h1>Talsu KC pasākumi</h1>
<div class="meta">Atjaunots: {now}</div>

<input id="search" placeholder="Meklēt pasākumu...">

<br><br>

<table id="tbl">
<thead>
<tr>
<th>Datums</th>
<th>Laiks</th>
<th>Pasākums</th>
<th>Brīvas</th>
<th></th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>

</div>

<script>
const search=document.getElementById("search");
search.addEventListener("input",()=>{
    let v=search.value.toLowerCase();
    document.querySelectorAll("tbody tr").forEach(r=>{
        r.style.display=r.dataset.title.includes(v)?"":"none";
    });
});
</script>

</body>
</html>
"""

events = fetch_events()
events = sorted(events, key=lambda e: e.get("dateTime",""))
OUTPUT_HTML.write_text(build_html(events), encoding="utf-8")
