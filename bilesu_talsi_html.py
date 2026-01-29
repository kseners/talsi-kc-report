import requests
from datetime import datetime
from pathlib import Path
import html

VENUE_ID = 270
API_URL = f"https://www.bilesuparadize.lv/api/venue/{VENUE_ID}/repertoire"

# 👇 ģenerējam tieši index.html
OUTPUT_HTML = Path("index.html")


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


def badge_class(n):
    if n == 0:
        return "zero", "Nav"
    if n < 50:
        return "low", "Maz"
    if n < 200:
        return "mid", "Vidēji"
    return "high", "Daudz"


def build_html(events):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = ""

    for ev in events:
        dt = (ev.get("dateTime") or "")[:16]
        date = dt.split("T")[0]
        time = dt.split("T")[1] if "T" in dt else ""

        title = html.escape(get_title(ev))
        url = get_url(ev)
        free = get_available_total(ev)

        cls, label = badge_class(free)

        rows += f"""
        <div class="card">
            <div class="date">{date} {time}</div>
            <div class="title">{title}</div>

            <div class="bottom">
                <div class="badge {cls}">
                    {free}
                    <span>{label}</span>
                </div>
                <a href="{url}" target="_blank">Atvērt</a>
            </div>
        </div>
        """

    return f"""
<!doctype html>
<html lang="lv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Talsu KC biļetes</title>

<style>
body {{
    margin:0;
    font-family:system-ui;
    background:#0f172a;
    color:white;
}}

.header {{
    padding:20px;
    text-align:center;
}}

.header h1 {{
    margin:0;
    font-size:22px;
}}

.header p {{
    opacity:.7;
    margin:6px 0 0;
}}

.container {{
    max-width:800px;
    margin:auto;
    padding:10px;
}}

.card {{
    background:#1e293b;
    border-radius:14px;
    padding:16px;
    margin-bottom:12px;
}}

.date {{
    font-size:13px;
    opacity:.7;
}}

.title {{
    font-size:18px;
    font-weight:600;
    margin:6px 0 12px;
}}

.bottom {{
    display:flex;
    justify-content:space-between;
    align-items:center;
}}

.badge {{
    font-size:28px;
    font-weight:800;
    padding:10px 18px;
    border-radius:30px;
    display:flex;
    flex-direction:column;
    align-items:center;
}}

.badge span {{
    font-size:12px;
    font-weight:500;
    opacity:.8;
}}

.high {{background:#14532d; color:#86efac;}}
.mid {{background:#78350f; color:#fde68a;}}
.low {{background:#7f1d1d; color:#fecaca;}}
.zero {{background:#374151; color:#e5e7eb;}}

a {{
    background:#2563eb;
    padding:10px 16px;
    border-radius:10px;
    color:white;
    text-decoration:none;
}}

a:hover {{opacity:.85}}
</style>
</head>

<body>

<div class="header">
    <h1>Talsu Kultūras centrs</h1>
    <p>Atjaunots: {now}</p>
</div>

<div class="container">
{rows}
</div>

</body>
</html>
"""


events = fetch_events()
OUTPUT_HTML.write_text(build_html(events), encoding="utf-8")
