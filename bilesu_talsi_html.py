import requests
from datetime import datetime
from pathlib import Path
import html

VENUE_ID = 270
API_URL = f"https://www.bilesuparadize.lv/api/venue/{VENUE_ID}/repertoire"

# GitHub Pages: lai / atveras automātiski
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
        except Exception:
            pass
    return total


def badge_meta(free: int):
    """
    Kontrastainas krāsas ar tumšu tekstu (labi redzamas).
    Sliekšņus vari mainīt, ja vajag.
    """
    if free <= 0:
        return ("nav", "Nav", "#F3F4F6", "#111827", "#D1D5DB")  # gaišs
    if free < 50:
        return ("low", "Maz", "#FEE2E2", "#7F1D1D", "#FCA5A5")  # sarkans
    if free < 200:
        return ("mid", "Vidēji", "#FEF3C7", "#78350F", "#FCD34D")  # dzeltens
    return ("high", "Daudz", "#DCFCE7", "#14532D", "#86EFAC")  # zaļš


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

        key, label, bg, fg, border = badge_meta(free)

        rows.append(f"""
          <tr>
            <td class="mono">{html.escape(date)}</td>
            <td class="mono">{html.escape(time)}</td>
            <td class="title">
              <a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(title)}</a>
              <div class="sub">{label}</div>
            </td>
            <td class="free">
              <span class="badge" data-key="{key}" style="background:{bg}; color:{fg}; border-color:{border};">
                {free}
              </span>
            </td>
            <td class="open">
              <a class="btn" href="{html.escape(url)}" target="_blank" rel="noopener">Atvērt</a>
            </td>
          </tr>
        """)

    rows_html = "\n".join(rows) if rows else '<tr><td colspan="5" class="empty">Nav atrasts neviens pasākums.</td></tr>'

    return f"""<!doctype html>
<html lang="lv">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Talsu KC — biļešu atskaite</title>
  <style>
    :root {{
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #475569;
      --line: #e5e7eb;
      --shadow: 0 18px 50px rgba(15, 23, 42, .10);
      --link: #0b63ce;
    }}

    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background:
        radial-gradient(900px 500px at 10% 0%, rgba(59,130,246,.12), transparent 60%),
        radial-gradient(900px 500px at 90% 10%, rgba(16,185,129,.10), transparent 55%),
        var(--bg);
      color: var(--text);
    }}

    .wrap {{
      max-width: 1160px;
      margin: 26px auto;
      padding: 0 16px 40px;
    }}

    .top {{
      display: flex;
      gap: 12px;
      align-items: flex-end;
      justify-content: space-between;
      flex-wrap: wrap;
      margin-bottom: 14px;
    }}

    h1 {{
      margin: 0;
      font-size: 22px;
      letter-spacing: .2px;
    }}

    .meta {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 13px;
    }}

    .pill {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 10px 12px;
      box-shadow: var(--shadow);
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}

    .card {{
      background: var(--card);
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
      text-align: left;
      font-size: 12px;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--muted);
      background: #f1f5f9;
      border-bottom: 1px solid var(--line);
      padding: 12px 12px;
      position: sticky;
      top: 0;
      z-index: 2;
    }}

    tbody td {{
      border-bottom: 1px solid var(--line);
      padding: 12px 12px;
      vertical-align: middle;
      font-size: 14px;
    }}

    tbody tr:nth-child(even) {{
      background: #fafafa;
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
      font-weight: 700;
    }}
    .title a:hover {{
      text-decoration: underline;
      color: var(--link);
    }}

    .sub {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
    }}

    .badge {{
      display: inline-flex;
      min-width: 74px;
      justify-content: center;
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid;
      font-weight: 900;
      font-size: 14px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      box-shadow: 0 6px 16px rgba(15,23,42,.08);
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 9px 12px;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: #ffffff;
      color: var(--link);
      text-decoration: none;
      font-weight: 700;
      font-size: 13px;
    }}
    .btn:hover {{
      background: #f1f5f9;
    }}

    .legend {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 12px 0 0;
      color: var(--muted);
      font-size: 13px;
      align-items: center;
    }}
    .legend .mini {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 10px;
      box-shadow: 0 10px 24px rgba(15,23,42,.06);
    }}

    .empty {{
      color: var(--muted);
      text-align: center;
      padding: 28px 12px;
    }}

    .footer {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 12px;
    }}

    @media (max-width: 760px) {{
      thead th:nth-child(5), tbody td:nth-child(5) {{ display:none; }}
      .badge {{ min-width: 64px; padding: 7px 10px; }}
      h1 {{ font-size: 20px; }}
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

      <div class="pill">
        Venue ID: <strong>{VENUE_ID}</strong>
        <span style="opacity:.45"> • </span>
        Pasākumi: <strong>{len(events)}</strong>
      </div>
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th style="width:120px">Datums</th>
            <th style="width:90px">Laiks</th>
            <th>Pasākums</th>
            <th style="width:160px">Brīvas</th>
            <th style="width:110px">Saite</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>

    <div class="legend">
      <span class="mini"><strong style="color:#14532D;">200+</strong> daudz brīvu</span>
      <span class="mini"><strong style="color:#78350F;">50–199</strong> vidēji</span>
      <span class="mini"><strong style="color:#7F1D1D;">0–49</strong> maz</span>
      <span class="mini"><strong style="color:#111827;">0</strong> nav</span>
    </div>

  </div>
</body>
</html>
"""


def main():
    events = fetch_events()
    events = sorted(events, key=lambda e: e.get("dateTime", ""))

    html_text = build_html(events)
    OUTPUT_HTML.write_text(html_text, encoding="utf-8")

    print("OK. HTML saglabāts:", OUTPUT_HTML.resolve())
    print("Atrasti pasākumi:", len(events))


if __name__ == "__main__":
    main()
