import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fetchEvents, type Event } from "./fetchEvents.js";

const OUTPUT_DIR = "dist";
const ASSET_DIR = path.join(OUTPUT_DIR, "assets");

const formatDate = (value: string): string => {
  const date = new Date(value.replace(" ", "T"));
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("lv-LV", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Europe/Riga",
  }).format(date);
};

const formatUpdated = (date: Date): string => {
  return new Intl.DateTimeFormat("lv-LV", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Europe/Riga",
  }).format(date);
};

const escapeHtml = (value: string): string =>
  value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

const renderEventCard = (event: Event): string => {
  const ticketLabel =
    event.remainingTickets > 0
      ? `${event.remainingTickets} pieejamas biļetes`
      : "Izpārdots";
  const ticketClass =
    event.remainingTickets > 0 ? "ticket-count" : "ticket-count sold-out";
  const link = `https://www.bilesuparadize.lv/lv/event/${event.id}`;
  const locationParts = [event.address, event.city].filter(Boolean).join(", ");
  const imageBlock = event.imageUrl
    ? `<img src="${event.imageUrl}" alt="${escapeHtml(
        event.title
      )}" loading="lazy" />`
    : `<div class="image-fallback" aria-hidden="true"></div>`;

  return `
    <article class="card">
      <div class="card-media">
        ${imageBlock}
      </div>
      <div class="card-body">
        <div class="card-header">
          <h2>${escapeHtml(event.title)}</h2>
          <span class="${ticketClass}">${ticketLabel}</span>
        </div>
        <p class="event-date">${formatDate(event.startDateTime)}</p>
        ${
          locationParts
            ? `<p class="event-location">${escapeHtml(locationParts)}</p>`
            : ""
        }
        <div class="card-actions">
          <a class="btn" href="${link}" target="_blank" rel="noreferrer">
            Pirkt biļetes
          </a>
        </div>
      </div>
    </article>
  `;
};

const renderHtml = (events: Event[], updatedAt: Date): string => {
  const cards =
    events.length > 0
      ? events.map(renderEventCard).join("\n")
      : `
        <div class="empty-state">
          <h2>Pašlaik nav pieejamu pasākumu</h2>
          <p>Atjauniniet lapu vēlāk, lai redzētu jaunumus.</p>
        </div>
      `;

  return `<!doctype html>
<html lang="lv">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Talsu Kultūras Centrs | Pasākumi</title>
    <meta
      name="description"
      content="Aktuālie pasākumi Talsu Kultūras Centrā ar atlikušajām biļetēm un pirkšanas saitēm."
    />
    <link rel="stylesheet" href="assets/styles.css" />
  </head>
  <body>
    <header class="hero">
      <div class="container">
        <p class="venue-label">Talsu Kultūras centrs</p>
        <h1>Aktuālie pasākumi</h1>
        <p class="hero-subtitle">
          Skatiet, cik biļetes vēl ir pieejamas, un dodieties uz pirkšanu.
        </p>
        <p class="updated-at">Atjaunots: ${formatUpdated(updatedAt)}</p>
      </div>
    </header>
    <main class="container">
      <section class="events-grid">
        ${cards}
      </section>
    </main>
    <footer class="footer">
      <div class="container">
        <p>Biļešu pārdošana: bilesuparadize.lv</p>
      </div>
    </footer>
  </body>
</html>`;
};

const styles = `
:root {
  color-scheme: light;
  --bg: #f6f7fb;
  --card: #ffffff;
  --text: #1a1d29;
  --muted: #5f6473;
  --accent: #3b5ccc;
  --accent-dark: #2d46a1;
  --success: #1f8b4c;
  --danger: #cc2a2a;
  --border: #e4e6ef;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: "Inter", "Segoe UI", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

img {
  max-width: 100%;
  display: block;
}

.container {
  width: min(1100px, 92vw);
  margin: 0 auto;
}

.hero {
  background: linear-gradient(135deg, #2f3c7e, #4f6ddf);
  color: #ffffff;
  padding: 3.5rem 0 3rem;
}

.venue-label {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.75rem;
  margin: 0 0 0.8rem;
}

.hero h1 {
  font-size: clamp(2rem, 3vw + 1rem, 3rem);
  margin: 0 0 0.6rem;
}

.hero-subtitle {
  margin: 0 0 1.5rem;
  color: rgba(255, 255, 255, 0.85);
  max-width: 40rem;
}

.updated-at {
  margin: 0;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
}

.events-grid {
  display: grid;
  gap: 1.5rem;
  margin: -2.5rem auto 3rem;
}

.card {
  display: grid;
  grid-template-columns: 1fr;
  background: var(--card);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(25, 32, 72, 0.08);
  border: 1px solid var(--border);
}

.card-media {
  background: #d9deef;
  aspect-ratio: 16 / 9;
}

.card-media img {
  height: 100%;
  width: 100%;
  object-fit: cover;
}

.image-fallback {
  height: 100%;
  width: 100%;
  background: linear-gradient(135deg, #cfd6f5, #eef1fb);
}

.card-body {
  padding: 1.5rem;
  display: grid;
  gap: 0.75rem;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-header h2 {
  margin: 0;
  font-size: 1.35rem;
}

.ticket-count {
  display: inline-flex;
  align-self: flex-start;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  background: rgba(31, 139, 76, 0.12);
  color: var(--success);
  font-weight: 600;
  font-size: 0.9rem;
}

.ticket-count.sold-out {
  background: rgba(204, 42, 42, 0.12);
  color: var(--danger);
}

.event-date,
.event-location {
  margin: 0;
  color: var(--muted);
}

.card-actions {
  margin-top: 0.5rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem 1.4rem;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
  background: var(--accent);
  color: white;
  transition: transform 0.2s ease, background 0.2s ease;
}

.btn:hover {
  background: var(--accent-dark);
  transform: translateY(-1px);
}

.empty-state {
  background: var(--card);
  border-radius: 16px;
  padding: 2.5rem;
  text-align: center;
  border: 1px dashed var(--border);
  color: var(--muted);
}

.footer {
  padding: 2rem 0 3rem;
  color: var(--muted);
  font-size: 0.9rem;
}

@media (min-width: 768px) {
  .events-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .card {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 1024px) {
  .events-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
`;

const generateSite = async () => {
  const events = await fetchEvents();
  const updatedAt = new Date();
  await mkdir(ASSET_DIR, { recursive: true });
  await writeFile(path.join(OUTPUT_DIR, "index.html"), renderHtml(events, updatedAt), "utf8");
  await writeFile(path.join(ASSET_DIR, "styles.css"), styles.trim(), "utf8");
};

generateSite().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
