import { chromium } from "playwright-extra";
import StealthPlugin from "puppeteer-extra-plugin-stealth";
import { fileURLToPath } from "node:url";
import path from "node:path";

const API_URL = "https://www.bilesuparadize.lv/api/venue/270/event";

type LocalizedString = {
  lv?: string | null;
  en?: string | null;
  ru?: string | null;
};

type RawPriceGroup = {
  count?: number | null;
};

type RawEvent = {
  id?: number;
  performance_titles?: LocalizedString | null;
  date_time?: string | null;
  small_image_url?: LocalizedString | null;
  poster_image_url?: LocalizedString | null;
  price_groups?: RawPriceGroup[] | null;
  address?: string | null;
  city?: string | null;
};

export type Event = {
  id: number;
  title: string;
  startDateTime: string;
  imageUrl: string | null;
  remainingTickets: number;
  address: string | null;
  city: string | null;
};

const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36";

const pickLocalized = (value?: LocalizedString | null): string | null => {
  const candidate =
    value?.lv?.trim() || value?.en?.trim() || value?.ru?.trim() || "";
  return candidate.length > 0 ? candidate : null;
};

const sumRemainingTickets = (groups?: RawPriceGroup[] | null): number => {
  if (!Array.isArray(groups)) {
    return 0;
  }
  return groups.reduce((total, group) => {
    const count = group.count ?? 0;
    return total + (Number.isFinite(count) ? count : 0);
  }, 0);
};

const mapEvent = (raw: RawEvent): Event | null => {
  const id = raw.id;
  const title = pickLocalized(raw.performance_titles);
  const startDateTime = raw.date_time ?? null;
  if (!id || !title || !startDateTime) {
    return null;
  }

  const imageUrl =
    pickLocalized(raw.small_image_url) ||
    pickLocalized(raw.poster_image_url) ||
    null;

  return {
    id,
    title,
    startDateTime,
    imageUrl,
    remainingTickets: sumRemainingTickets(raw.price_groups),
    address: raw.address ?? null,
    city: raw.city ?? null,
  };
};

export const fetchEvents = async (): Promise<Event[]> => {
  chromium.use(StealthPlugin());
  const browser = await chromium.launch({ headless: true });
  try {
    const context = await browser.newContext({
      locale: "lv-LV",
      userAgent: USER_AGENT,
      viewport: { width: 1280, height: 720 },
    });
    const page = await context.newPage();
    const response = await page.goto(API_URL, {
      waitUntil: "networkidle",
      timeout: 60_000,
    });

    if (!response) {
      throw new Error("No response from API endpoint.");
    }
    if (!response.ok()) {
      throw new Error(`API responded with ${response.status()}.`);
    }

    const json = (await response.json()) as unknown;
    if (!Array.isArray(json)) {
      throw new Error("Unexpected API response format.");
    }

    const events = json
      .map((item) => mapEvent(item as RawEvent))
      .filter((event): event is Event => Boolean(event))
      .sort((a, b) => a.startDateTime.localeCompare(b.startDateTime));

    return events;
  } finally {
    await browser.close();
  }
};

const runIfMain = async () => {
  const currentFile = fileURLToPath(import.meta.url);
  const invokedFile = process.argv[1]
    ? path.resolve(process.argv[1])
    : null;
  if (invokedFile && currentFile === invokedFile) {
    const events = await fetchEvents();
    console.log(JSON.stringify(events, null, 2));
  }
};

runIfMain().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
