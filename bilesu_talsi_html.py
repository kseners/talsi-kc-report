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

def build_html(events):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = ""
    for ev in events:
        dt = (ev.get("dateTime") or "")[:16].replace("T"," ")
        title = get_title(ev)
        url = get_url(ev)
        free = get_available_total(ev)

        rows += f"""
        <tr>
        <td>{dt}</td>
        <td>{html.escape(title)}</td>
        <td>{free}</td>
        <td><a href='{url}' target='_blank'>Link</a></td>
        </tr>
        """

    return f"""
    <html>
    <body style="font-family:Arial">
    <h2>Talsu KC biļetes</h2>
    <p>Atjaunots: {now}</p>
    <table border="1" cellpadding="5">
    <tr><th>Datums</th><th>Pasākums</th><th>Brīvas</th><th>Saite</th></tr>
    {rows}
    </table>
    </body>
    </html>
    """

events = fetch_events()
html_text = build_html(events)
OUTPUT_HTML.write_text(html_text, encoding="utf-8")
