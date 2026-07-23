// Headless demo capture: drives the live Counterproof demo with Playwright,
// records the session, and encodes a README-sized GIF with ffmpeg.
//
// Re-run when the UI changes:
//   node scripts/capture-demo.mjs
//
// Env overrides:
//   DEMO_URL   target URL (default: production)
//   GIF_FPS    frames per second (default: 12)
//   GIF_WIDTH  output width in px (default: 960)
//
// Requires: playwright (dev dep) + `pnpm exec playwright install chromium`, and ffmpeg on PATH.

import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const REPO_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const OUT_DIR = join(REPO_ROOT, "docs");
const OUT_GIF = join(OUT_DIR, "counterproof-demo.gif");

const DEMO_URL = process.env.DEMO_URL ?? "https://counterproof-web.vercel.app";
const DEMO_API_URL = process.env.DEMO_API_URL ?? "https://counterproof-api.fly.dev";
const FPS = Number(process.env.GIF_FPS ?? "12");
const WIDTH = Number(process.env.GIF_WIDTH ?? "960");

// Recording viewport. The app centers a column on a dark canvas; we record a
// touch wider than the column and crop to it, so the frame is app-only.
const VIEW_W = 1200;
const VIEW_H = 820;
const CROP_W = 1000;
const CROP_X = Math.round((VIEW_W - CROP_W) / 2);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function record(videoDir) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: VIEW_W, height: VIEW_H },
    deviceScaleFactor: 2,
    recordVideo: { dir: videoDir, size: { width: VIEW_W, height: VIEW_H } },
  });
  const page = await context.newPage();

  // Warm-up: the page pings /health on load, but hit it directly first so the
  // scale-to-zero API is awake and the capture never opens on a cold start.
  try {
    await page.request.get(`${DEMO_API_URL}/health`);
  } catch {
    // ignore; the on-load warm-up still fires
  }

  await page.goto(DEMO_URL, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: "Run Counterproof" }).waitFor();

  // Beat 1: land.
  await sleep(3500);

  // Beat 2: load the tampered sample.
  await page.getByRole("button", { name: "Load tampered sample" }).click();
  await sleep(2500);

  // Beat 3: run.
  await page.getByRole("button", { name: "Run Counterproof" }).click();

  // Beat 4: hold on the verdict (the page auto-scrolls it into view). Money shot.
  await page.getByText("Discrepancy found.").waitFor({ timeout: 20000 });
  await sleep(6000);

  // Beat 5: scroll to the evidence and hold so both cited lines are readable.
  await page.evaluate(() => {
    document
      .querySelector('section[aria-label="Evidence"]')
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  await sleep(7500);

  // Beat 6: stop. No scrolling into extracted fields or the audit trail.
  await sleep(800);

  await context.close();
  await browser.close();

  const file = readdirSync(videoDir).find((f) => f.endsWith(".webm"));
  if (!file) throw new Error("no video produced");
  return join(videoDir, file);
}

function encodeGif(webm) {
  if (!existsSync(OUT_DIR)) mkdirSync(OUT_DIR, { recursive: true });
  const palette = join(dirname(webm), "palette.png");
  const filters = `fps=${FPS},crop=${CROP_W}:${VIEW_H}:${CROP_X}:0,scale=${WIDTH}:-1:flags=lanczos`;

  execFileSync("ffmpeg", ["-y", "-i", webm, "-vf", `${filters},palettegen=stats_mode=diff`, palette], {
    stdio: "inherit",
  });
  execFileSync(
    "ffmpeg",
    [
      "-y",
      "-i",
      webm,
      "-i",
      palette,
      "-lavfi",
      `${filters}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle`,
      OUT_GIF,
    ],
    { stdio: "inherit" },
  );
}

async function main() {
  const videoDir = mkdtempSync(join(tmpdir(), "counterproof-demo-"));
  try {
    const webm = await record(videoDir);
    encodeGif(webm);
    const sizeMb = statSync(OUT_GIF).size / (1024 * 1024);
    console.log(`\nWrote ${OUT_GIF} (${sizeMb.toFixed(2)} MB) at ${WIDTH}px / ${FPS}fps`);
    if (sizeMb > 5) {
      console.warn("WARNING: GIF exceeds 5 MB; lower GIF_FPS or GIF_WIDTH and re-run.");
    }
  } finally {
    rmSync(videoDir, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
