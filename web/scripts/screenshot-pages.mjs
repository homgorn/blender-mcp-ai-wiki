/**
 * Screenshot every built page and check it.
 *
 *   node scripts/screenshot-pages.mjs [distDir] [outDir]
 *
 * Serves dist over HTTP (file:// breaks absolute-path resolution), then for each
 * page takes a screenshot at 390 / 768 / 1440 and asserts:
 *   - exactly one <h1>
 *   - no horizontal overflow
 *   - a visible <nav> with an aria-label and real links (mobile)
 *   - lang on <html>
 *   - no console errors, no failed requests
 *
 * Output directories: <outDir>/{mobile,tablet,desktop}/<path-joined-with-__>.png
 */
import { createServer } from "node:http";
import { existsSync, readdirSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { extname, join, relative } from "node:path";
import { createRequire } from "node:module";

const DIST = process.argv[2] || join(process.cwd(), "dist");
const OUT = process.argv[3] || join(process.env.TEMP || "/tmp", "shots");
const PORT = Number(process.env.PORT || 4321);

const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png",
  ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8", ".xml": "application/xml",
  ".webmanifest": "application/manifest+json", ".md": "text/markdown; charset=utf-8",
};

const server = createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]);
  if (p.endsWith("/")) p += "index.html";
  const f = join(DIST, p);
  const send = (file) => {
    res.writeHead(200, { "content-type": MIME[extname(file)] || "application/octet-stream" });
    res.end(readFileSync(file));
  };
  if (existsSync(f) && extname(f)) return send(f);
  if (existsSync(f + ".html")) return send(f + ".html");
  if (existsSync(join(f, "index.html"))) return send(join(f, "index.html"));
  res.writeHead(404); res.end("not found");
});
await new Promise((r) => server.listen(PORT, r));

const require_ = createRequire(import.meta.url);
let chromium;
try {
  chromium = require_("playwright-core").chromium;
} catch {
  // Fallback to a global install for machines that don't run npm ci first.
  const root = require_("node:child_process").execSync("npm root -g", { encoding: "utf8" }).trim();
  chromium = require_(join(root, "playwright")).chromium;
}

function listPages(dir, acc = []) {
  for (const n of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, n.name);
    if (n.isDirectory()) listPages(p, acc);
    else if (n.name.endsWith(".html")) acc.push(p);
  }
  return acc;
}

const pages = listPages(DIST);
const VIEWPORTS = [
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "desktop", width: 1440, height: 900 },
];

const browser = await chromium.launch();
const problems = [];
let shots = 0;

for (const vp of VIEWPORTS) {
  mkdirSync(join(OUT, vp.name), { recursive: true });
  const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  const page = await ctx.newPage();
  for (const f of pages) {
    const url = `http://127.0.0.1:${PORT}/${relative(DIST, f).replace(/\\/g, "/")}`;
    const errs = [];
    const onC = (m) => { if (m.type() === "error") errs.push(m.text()); };
    const onF = (r) => errs.push(`requestfailed ${r.url()}`);
    page.on("console", onC); page.on("requestfailed", onF);
    await page.goto(url, { waitUntil: "load", timeout: 30000 });
    await page.waitForTimeout(80);
    const info = await page.evaluate(() => {
      const h1 = document.querySelectorAll("h1").length;
      const de = document.documentElement;
      const overflow = Math.max(de.scrollWidth - de.clientWidth, 0);
      const navs = [...document.querySelectorAll("nav")].map((n) => ({
        label: n.getAttribute("aria-label"),
        links: n.querySelectorAll("a").length,
        visible: n.getBoundingClientRect().height > 0,
      }));
      return { h1, overflow, navs, lang: de.getAttribute("lang") };
    });
    const rel = relative(DIST, f).replace(/\\/g, "/").replace(/\.html$/, "");
    const out = join(OUT, vp.name, rel.replace(/\//g, "__") + ".png");
    await page.screenshot({ path: out });
    shots++;
    if (info.h1 !== 1) problems.push(`${rel} @${vp.name}: ${info.h1} <h1>`);
    if (info.overflow > 1) problems.push(`${rel} @${vp.name}: horizontal overflow ${info.overflow}px`);
    if (!info.lang) problems.push(`${rel} @${vp.name}: no lang on <html>`);
    if (vp.name === "mobile") {
      if (!info.navs.some((n) => n.visible)) problems.push(`${rel} @mobile: no visible <nav>`);
      for (const n of info.navs) {
        if (!n.label) problems.push(`${rel}: <nav> without aria-label`);
        else if (n.links === 0) problems.push(`${rel}: <nav aria-label="${n.label}"> has 0 links`);
      }
    }
    if (errs.length) problems.push(`${rel} @${vp.name}: ${errs.slice(0, 2).join(" | ")}`);
    page.off("console", onC); page.off("requestfailed", onF);
  }
  await ctx.close();
  console.log(`${vp.name}: ${pages.length} shots`);
}
await browser.close();
server.close();

const out = { shots, problems: problems.length, byKind: {} };
for (const p of problems) {
  const k = p.replace(/^.*?: /, "").replace(/\d+/g, "N");
  out.byKind[k] = (out.byKind[k] || 0) + 1;
}
writeFileSync(join(OUT, "problems.txt"), problems.length ? problems.join("\n") : "no problems found", "utf8");
console.log(`\nscreenshots: ${out.shots}`);
console.log(`problems: ${problems.length}`);
for (const [k, v] of Object.entries(out.byKind).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(v).padStart(5)}  ${k}`);
}