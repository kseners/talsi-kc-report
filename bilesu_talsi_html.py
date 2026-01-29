import requests
from datetime import datetime
from pathlib import Path
import html

VENUE_ID = 270
API_URL = f"https://www.bilesuparadize.lv/api/venue/{VENUE_ID}/repertoire"

# GitHub Pages: galvenajai adresei vajag index.html
OUTPUT_INDEX = Path("index.html")
OUTPUT_ALT = Path("talsu_kc_report.html")  # optional

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

def get_available_total(ev) -> int:
    total = 0
    for p in (ev.get("prices") or []):
        try:
            total += int(p.get("count", 0) or 0)
        except Exception:
            pass
    return total

def _int_or_none(x):
    try:
        if x is None:
            return None
        return int(x)
    except Exception:
        return None

def get_capacity_total(ev):
    """
    Mēģina atrast kopējo sēdvietu skaitu no API (ja tāds vispār tiek dots).
    Dažādos API izvadēs lauku nosaukumi var atšķirties, tāpēc pārbaudām vairākus.
    Ja nevar noteikt, atgriež None.
    """
    keys = [
        "capacity", "total", "totalCount", "maxCount", "allCount", "initialCount",
        "limit", "quantity", "seats", "places"
    ]

    cap = 0
    found_any = False
    for p in (ev.get("prices") or []):
        for k in keys:
            v = _int_or_none(p.get(k))
            if v is not None and v > 0:
                cap += v
                found_any = True
                break

    if found_any and cap > 0:
        return cap

    # dažreiz ir augstākā līmeņa lauks
    for k in ["capacity", "total", "totalCount", "maxCount"]:
        v = _int_or_none(ev.get(k))
        if v is not None and v > 0:
            return v

    return None

def get_image(ev):
    """
    Ja API dod bildi/posteri, izmantojam. Ja nē, atgriež None (rādīsies fallback).
    """
    perf = ev.get("performance") or {}
    # biežākie varianti
    for path in [
        ("image",),
        ("poster",),
        ("posterUrl",),
        ("cover",),
        ("img",),
        ("images", "poster"),
        ("images", "cover"),
        ("images", "large"),
        ("images", "medium"),
        ("images", "small"),
    ]:
        obj = perf
        ok = True
        for k in path:
            if isinstance(obj, dict) and k in obj:
                obj = obj[k]
            else:
                ok = False
                break
        if ok and isinstance(obj, str) and obj.startswith("http"):
            return obj
    return None

def fmt_dt(ev):
    dt_raw = ev.get("dateTime") or ""
    date = dt_raw[:10]
    time = dt_raw[11:16]
    return date, time

def bucket(free: int):
    if free <= 0:
        return ("zero", "Nav")
    if free < 50:
        return ("low", "Maz")
    if free < 200:
        return ("mid", "Vidēji")
    return ("high", "Daudz")

def build_html(events):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    cards = []
    for ev in events:
        date, time = fmt_dt(ev)
        title = get_title(ev)
        url = get_url(ev)
        free = get_available_total(ev)
        cap = get_capacity_total(ev)  # None, ja nav zināms
        img = get_image(ev)

        cls, label = bucket(free)

        # progress %
        pct = None
        if cap and cap > 0:
            sold = max(0, cap - free)
            pct = max(0, min(100, int(round((sold / cap) * 100))))

        safe_title = html.escape(title)
        safe_url = html.escape(url)
        safe_date = html.escape(date)
        safe_time = html.escape(time)

        img_html = ""
        if img:
            img_html = f"""<div class="thumb" style="background-image:url('{html.escape(img)}')"></div>"""
        else:
            # fallback: gradient thumb ar datumu
            img_html = f"""<div class="thumb thumb--fallback">
                <div class="thumbDate">
                  <div class="d">{safe_date[8:10]}</div>
                  <div class="m">{safe_date[5:7]}</div>
                </div>
              </div>"""

        progress_html = ""
        if pct is not None:
            progress_html = f"""
              <div class="progress">
                <div class="bar"><span style="width:{pct}%"></span></div>
                <div class="nums">{free}/{cap} brīvas</div>
              </div>
            """

        cards.append(f"""
          <article class="card">
            {img_html}
            <div class="body">
              <div class="topline">
                <div class="dt"><span class="date">{safe_date}</span> <span class="time">{safe_time}</span></div>
                <span class="pill {cls}">{free} • {label}</span>
              </div>

              <h3 class="title">{safe_title}</h3>

              {progress_html}

              <div class="actions">
                <a class="btn" href="{safe_url}" target="_blank" rel="noopener">Atvērt</a>
              </div>
            </div>
          </article>
        """)

    cards_html = "\n".join(cards) if cards else "<div class='empty'>Nav atrasts neviens pasākums.</div>"

    return f"""<!doctype html>
<html lang="lv">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Talsu Kultūras centrs — biļešu atskaite</title>
  <style>
    :root {{
      --bg1:#f4f6fb;
      --bg2:#eaf1ff;
      --ink:#0b1324;
      --muted: rgba(11,19,36,.70);
      --card:#ffffff;
      --line: rgba(11,19,36,.10);
      --shadow: 0 18px 45px rgba(11,19,36,.10);
      --btn:#1d4ed8;
      --btn2:#0f2f98;

      --good:#22c55e;
      --mid:#f59e0b;
      --low:#ef4444;
      --zero:#94a3b8;
    }}

    *{{box-sizing:border-box}}
    body {{
      margin:0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(800px 500px at 15% 0%, rgba(59,130,246,.22), transparent 60%),
        radial-gradient(900px 520px at 90% 10%, rgba(14,165,233,.18), transparent 55%),
        linear-gradient(180deg, var(--bg2), var(--bg1));
    }}

    .wrap {{
      max-width: 1080px;
      margin: 22px auto;
      padding: 0 14px 42px;
    }}

    header {{
      display:flex;
      align-items:flex-end;
      justify-content:space-between;
      gap:14px;
      margin-bottom: 14px;
    }}

    h1 {{
      margin:0;
      font-size: 20px;
      letter-spacing:.2px;
    }}
    .sub {{
      margin-top:6px;
      color: var(--muted);
      font-size: 13px;
    }}

    .metaPill {{
      background: rgba(255,255,255,.65);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      box-shadow: var(--shadow);
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}

    .grid {{
      display:grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}

    .card {{
      display:grid;
      grid-template-columns: 170px 1fr;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow:hidden;
      box-shadow: var(--shadow);
    }}

    .thumb {{
      background-size: cover;
      background-position: center;
      min-height: 150px;
    }}

    .thumb--fallback {{
      background:
        linear-gradient(135deg, rgba(29,78,216,.20), rgba(14,165,233,.18)),
        linear-gradient(180deg, #0b2a66, #0b1324);
      position:relative;
    }}
    .thumbDate {{
      position:absolute;
      left:14px;
      bottom:14px;
      color:white;
      text-shadow: 0 6px 18px rgba(0,0,0,.35);
      line-height:1;
    }}
    .thumbDate .d {{
      font-size: 44px;
      font-weight: 900;
      letter-spacing: -.02em;
    }}
    .thumbDate .m {{
      font-size: 16px;
      opacity:.92;
      font-weight: 800;
      letter-spacing: .12em;
    }}

    .body {{
      padding: 14px 14px 12px;
      display:flex;
      flex-direction:column;
      gap:10px;
      min-width:0;
    }}

    .topline {{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
      flex-wrap:wrap;
    }}

    .dt {{
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}
    .dt .time {{ margin-left: 10px; }}

    .title {{
      margin:0;
      font-size: 16px;
      line-height: 1.25;
      font-weight: 800;
      word-break: break-word;
    }}

    .pill {{
      display:inline-flex;
      align-items:center;
      gap:8px;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 13px;
      font-weight: 800;
      color: #0b1324;
      background: rgba(11,19,36,.06);
      border: 1px solid var(--line);
      white-space: nowrap;
    }}
    .pill.high {{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.14); }}
    .pill.mid  {{ border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.14); }}
    .pill.low  {{ border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.14); }}
    .pill.zero {{ border-color: rgba(148,163,184,.45); background: rgba(148,163,184,.18); }}

    .progress {{
      display:flex;
      align-items:center;
      gap:10px;
      flex-wrap:wrap;
    }}
    .bar {{
      flex: 1;
      min-width: 160px;
      height: 10px;
      background: rgba(11,19,36,.08);
      border: 1px solid rgba(11,19,36,.10);
      border-radius: 999px;
      overflow:hidden;
    }}
    .bar span {{
      display:block;
      height:100%;
      background: linear-gradient(90deg, rgba(34,197,94,.95), rgba(59,130,246,.95));
      border-radius: 999px;
    }}
    .nums {{
      font-size: 13px;
      color: var(--muted);
      font-weight: 700;
      white-space: nowrap;
    }}

    .actions {{
      display:flex;
      justify-content:flex-end;
      margin-top:auto;
    }}
    .btn {{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      padding: 10px 14px;
      border-radius: 12px;
      color: white;
      text-decoration:none;
      font-weight: 800;
      background: linear-gradient(180deg, var(--btn), var(--btn2));
      box-shadow: 0 14px 30px rgba(29,78,216,.18);
    }}
    .btn:hover {{ filter: brightness(1.05); }}

    .empty {{
      padding: 18px;
      color: var(--muted);
      background: rgba(255,255,255,.65);
      border: 1px solid var(--line);
      border-radius: 16px;
    }}

    /* MOBILE: viss redzams, nekas netiek nogriezts */
    @media (max-width: 860px) {{
      header {{ flex-direction: column; align-items:flex-start; }}
      .metaPill {{ width: 100%; }}
      .grid {{ grid-template-columns: 1fr; }}
      .card {{ grid-template-columns: 120px 1fr; }}
      .thumb {{ min-height: 120px; }}
      .thumbDate .d {{ font-size: 36px; }}
      .title {{ font-size: 15px; }}
      .bar {{ min-width: 140px; }}
    }}

    @media (max-width: 420px) {{
      .card {{ grid-template-columns: 1fr; }}
      .thumb {{ min-height: 150px; }}
      .actions {{ justify-content: stretch; }}
      .btn {{ width: 100%; }}
      .dt {{ white-space: normal; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>Talsu Kultūras centrs — pasākumi & brīvās biļetes</h1>
        <div class="sub">Atjaunots: <strong>{html.escape(now)}</strong></div>
      </div>
      <div class="metaPill">Venue ID: <strong>{VENUE_ID}</strong> &nbsp;•&nbsp; Pasākumi: <strong>{len(events)}</strong></div>
    </header>

    <section class="grid">
      {cards_html}
    </section>
  </div>
</body>
</html>
"""

def main():
    events = fetch_events()
    events = sorted(events, key=lambda e: e.get("dateTime", ""))

    html_text = build_html(events)

    OUTPUT_INDEX.write_text(html_text, encoding="utf-8")
    OUTPUT_ALT.write_text(html_text, encoding="utf-8")

    print("Saved:", OUTPUT_INDEX)
    print("Saved:", OUTPUT_ALT)

if __name__ == "__main__":
    main()
