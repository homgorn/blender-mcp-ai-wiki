#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wiki API — stdlib only, localhost only.

Run:  python wiki_api.py --port 8099
Docs: SDD/API.md (contract), /api/openapi.json (machine-readable)

Design notes
------------
* DB/index are cached in memory and reloaded only when mtime changes
  (previously every single request re-parsed a 9.4 MB JSON -> ~1.5 s each).
* ThreadingHTTPServer: a slow static asset no longer blocks /api/*.
* ETag + If-None-Match -> 304, so the browser stops refetching 2.6 MB chunks.
* GET never mutates state: /api/export is POST-only.
"""
import argparse, hashlib, json, re, subprocess, sys, time, threading, mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

WIKI = Path(r"C:\BLENDER ai\WIKI")
DB = WIKI / "db" / "wiki_database.json"
IDX = WIKI / "db" / "search_index.json"
GRAPH = WIKI / "db" / "graph.json"
API_VERSION = "1.1"
ENTRY_MAX_CHARS = 30000
SEARCH_TTL = 120
SEARCH_CACHE_MAX = 200

# ---------------------------------------------------------------- data layer
_lock = threading.Lock()
_state = {"db": None, "idx": None, "stamp": None}
_search_cache = {}


def _stamp():
    return (DB.stat().st_mtime, IDX.stat().st_mtime)


def load(force=False):
    """Return (db, idx), re-parsing only when the files changed on disk."""
    with _lock:
        try:
            stamp = _stamp()
        except OSError as ex:
            raise RuntimeError(f"DB not built: {ex} (run build_database.py first)")
        if force or _state["db"] is None or _state["stamp"] != stamp:
            _state["db"] = json.loads(DB.read_text(encoding="utf-8"))
            _state["idx"] = json.loads(IDX.read_text(encoding="utf-8"))
            _state["stamp"] = stamp
            _search_cache.clear()
        return _state["db"], _state["idx"]


def _cache_get(k):
    v = _search_cache.get(k)
    return v[1] if v and time.time() - v[0] < SEARCH_TTL else None


def _cache_put(k, v):
    if len(_search_cache) > SEARCH_CACHE_MAX:
        _search_cache.pop(next(iter(_search_cache)))
    _search_cache[k] = (time.time(), v)


# ---------------------------------------------------------------- search
STOP = {"the", "and", "for", "with", "from", "что", "как", "для", "все", "каждый"}


def search(db, idx, q, limit=10, lang="", cat=""):
    s = q.lower().strip()
    if not s:
        return []
    words = [w for w in re.findall(r"\w{2,}", s) if w not in STOP]
    if not words:
        return []
    terms = idx.get("terms", {})
    cands = None
    for w in words:
        ids = set(terms.get(w, ()))
        for t, tids in terms.items():          # prefix/substring fallback
            if w in t or t in w:
                ids.update(tids)
        cands = ids if cands is None else (cands & ids)
    if not cands:
        return []
    out = []
    for e in db["entries"]:
        m = e["meta"]
        if m["id"] not in cands:
            continue
        if lang and m.get("language") != lang:
            continue
        if cat and m.get("category") != cat:
            continue
        title = m.get("title", "").lower()
        desc = m.get("description", "").lower()
        tags = " ".join(m.get("tags", [])).lower()
        sc = 0
        for w in words:
            if w in title:
                sc += 10
            if w in desc:
                sc += 5
            if w in tags:
                sc += 3
        out.append({"score": sc, "id": m["id"], "title": m.get("title", ""),
                    "category": m.get("category", ""), "type": m.get("type", ""),
                    "difficulty": m.get("difficulty", 0), "tags": m.get("tags", []),
                    "language": m.get("language", "en"), "file": e["file_path"]})
    out.sort(key=lambda x: -x["score"])
    return out[:limit]


def graph_payload(limit=300, lang="", cat=""):
    """Precomputed layout from db/graph.json (no O(n^2) in the browser)."""
    if not GRAPH.exists():
        return {"nodes": [], "links": []}
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = [n for n in g.get("nodes", [])
             if (not lang or n.get("lang") == lang) and (not cat or n.get("category") == cat)]
    keep = {n["id"] for n in nodes[:limit]}
    links = [{"source": l["source"], "target": l["target"]}
             for l in g.get("links", []) if l["source"] in keep and l["target"] in keep]
    return {"nodes": nodes[:limit], "links": links, "total_nodes": len(nodes)}


# ---------------------------------------------------------------- contract
ROUTES = ["/api/health", "/api/version", "/api/openapi.json", "/api/stats", "/api/tags",
          "/api/list", "/api/entry?id=", "/api/search?q=", "/api/sitemap", "/api/graph",
          "POST /api/rebuild", "POST /api/export"]


def openapi():
    j = lambda **kw: kw
    q = lambda n, d: j(name=n, required=False, schema=j(type="string", default=d))
    return j(openapi="3.0.3", info=j(title="Blender AI Wiki API", version=API_VERSION,
                                     description="Read-only knowledge base over the built JSON DB."),
             servers=[j(url="http://127.0.0.1:8099")],
             paths={
                 "/api/health": j(get=j(summary="Liveness + entry count",
                                        responses={"200": j(description="ok")})),
                 "/api/version": j(get=j(summary="API + DB contract versions")),
                 "/api/stats": j(get=j(summary="DB statistics")),
                 "/api/tags": j(get=j(summary="Tag -> entry ids")),
                 "/api/list": j(get=j(summary="Paginated list",
                                      parameters=[q("category", ""), q("lang", ""),
                                                  q("type", ""), q("limit", "50"), q("offset", "0")])),
                 "/api/entry": j(get=j(summary="One entry with full content",
                                       parameters=[q("id", "")],
                                       responses={"404": j(description="not found")})),
                 "/api/search": j(get=j(summary="Full-text search",
                                        parameters=[q("q", ""), q("lang", ""),
                                                    q("category", ""), q("limit", "10")])),
                 "/api/sitemap": j(get=j(summary="All entry ids")),
                 "/api/graph": j(get=j(summary="Precomputed graph",
                                       parameters=[q("limit", "300"), q("lang", ""), q("category", "")])),
                 "/api/rebuild": j(post=j(summary="Rebuild the database",
                                          responses={"200": j(description="rebuild log tail")})),
                 "/api/export": j(post=j(summary="Run exports (has side effects: writes files)",
                                         parameters=[q("format", "csv"), q("chunk", "0"), q("chunks", "1")])),
             })


# ---------------------------------------------------------------- handler
class H(BaseHTTPRequestHandler):
    server_version = "WikiAPI/" + API_VERSION
    protocol_version = "HTTP/1.1"      # keep-alive; required for 304 to be useful
    quiet = False

    # -- plumbing
    def log_message(self, fmt, *a):
        if not self.quiet:
            sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % a))

    def _send(self, body: bytes, ctype: str, code: int = 200, cache: str = "no-store"):
        etag = '"%s"' % hashlib.md5(body).hexdigest()[:16]
        if self.headers.get("If-None-Match") == etag and code == 200:
            self.send_response(304)
            self.send_header("ETag", etag)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("ETag", etag)
        self.send_header("Cache-Control", cache)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_json(self, obj, code=200, cache="no-store"):
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8", code, cache)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def send_file(self, rel: str) -> bool:
        base = (WIKI / "site").resolve()
        p = (base / rel.lstrip("/")).resolve()
        if not p.is_relative_to(base) or not p.is_file():
            return False
        mt, _ = mimetypes.guess_type(str(p))
        data = p.read_bytes()
        # data/ is generated but not content-hashed -> short cache + ETag revalidation
        self._send(data, mt or "application/octet-stream", 200,
                   "max-age=300, must-revalidate" if rel.startswith("data/") else "no-cache")
        return True

    # ---- helpers
    @staticmethod
    def _q(q, k, d=""):
        return q.get(k, [d])[0]

    @staticmethod
    def _int(v, d, lo, hi):
        try:
            return max(lo, min(int(v), hi))
        except (TypeError, ValueError):
            return d

    # ---- routes
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        try:
            u = urlparse(self.path)
            q = parse_qs(u.query)
            p = u.path
            g = self._q

            if p in ("/site", "/site/"):
                p = "/site/index.html"
            if p.startswith("/site/") and self.send_file(p[len("/site"):] or "index.html"):
                return
            if p in ("/", "/index.html", "/app.js", "/style.css") and self.send_file(p.lstrip("/") or "index.html"):
                return

            if p == "/api/version":
                db, _ = load()
                return self.send_json({"api": API_VERSION, "db": db.get("version", "1.0"),
                                       "python": sys.version.split()[0],
                                       "contract": "SDD/API.md"})
            if p == "/api/openapi.json":
                return self.send_json(openapi())
            if p == "/api/export":
                return self.send_json({"error": "GET must not mutate state",
                                       "hint": "use POST /api/export?format=csv&chunk=0&chunks=1"}, 405)

            db, idx = load()
            n = db.get("total_entries", len(db["entries"]))

            if p in ("/api/health", "/"):
                return self.send_json({"ok": True, "entries": n, "version": db.get("version", "1.0"),
                                       "api": API_VERSION})
            if p == "/api/stats":
                return self.send_json(db.get("statistics", {}), cache="max-age=60")
            if p == "/api/tags":
                return self.send_json({"tags": idx.get("tags", {})}, cache="max-age=300")
            if p == "/api/sitemap":
                items = [{"id": e["meta"]["id"], "lang": e["meta"].get("language", "en"),
                          "cat": e["meta"].get("category", ""),
                          "url": f"#entry={e['meta']['id']}"} for e in db["entries"]]
                return self.send_json({"total": len(items), "items": items}, cache="max-age=300")
            if p == "/api/list":
                cat, lang, typ = g(q, "category"), g(q, "lang"), g(q, "type")
                limit = self._int(g(q, "limit", "50"), 50, 1, 200)
                off = self._int(g(q, "offset", "0"), 0, 0, 10 ** 9)
                items = [{"id": e["meta"]["id"], "title": e["meta"].get("title", ""),
                          "category": e["meta"].get("category", ""), "type": e["meta"].get("type", ""),
                          "difficulty": e["meta"].get("difficulty", 0), "tags": e["meta"].get("tags", []),
                          "language": e["meta"].get("language", "en"), "file": e["file_path"]}
                         for e in db["entries"]
                         if (not cat or e["meta"].get("category") == cat)
                         and (not lang or e["meta"].get("language") == lang)
                         and (not typ or e["meta"].get("type") == typ)]
                pages = (len(items) + limit - 1) // limit if items else 0
                return self.send_json({"total": len(items), "limit": limit, "offset": off,
                                       "total_pages": pages, "items": items[off:off + limit]})
            if p == "/api/entry":
                eid = g(q, "id", "")
                for e in db["entries"]:
                    if e["meta"]["id"] == eid:
                        full = e.get("full_content", "") or ""
                        cut = len(full) > ENTRY_MAX_CHARS
                        return self.send_json({
                            "meta": e["meta"], "sections": e.get("sections", []),
                            "file": e["file_path"],
                            "full_content": full[:ENTRY_MAX_CHARS],
                            "truncated": cut,
                            "truncated_at": ENTRY_MAX_CHARS if cut else None,
                            "total_chars": len(full)}, cache="max-age=60")
                return self.send_json({"error": "not found", "id": eid}, 404)
            if p == "/api/search":
                s, lang, cat = g(q, "q", ""), g(q, "lang", ""), g(q, "category", "")
                limit = self._int(g(q, "limit", "10"), 10, 1, 50)
                if not s.strip():
                    return self.send_json({"items": []})
                ck = f"{s}|{limit}|{lang}|{cat}"
                hit = _cache_get(ck)
                if hit is not None:
                    return self.send_json({"items": hit, "cached": True})
                res = search(db, idx, s, limit, lang, cat)
                _cache_put(ck, res)
                return self.send_json({"items": res, "cached": False})
            if p == "/api/graph":
                return self.send_json(graph_payload(self._int(g(q, "limit", "300"), 300, 1, 5000),
                                                    g(q, "lang", ""), g(q, "category", "")),
                                      cache="max-age=300")
            return self.send_json({"error": "unknown route", "routes": ROUTES}, 404)
        except Exception as ex:
            self.send_json({"error": str(ex), "type": type(ex).__name__}, 500)

    def do_POST(self):
        try:
            u = urlparse(self.path)
            if u.path == "/api/rebuild":
                r = subprocess.run([sys.executable, str(WIKI / "scripts" / "build_database.py")],
                                   capture_output=True, text=True, timeout=300)
                load(force=True)
                return self.send_json({"ok": r.returncode == 0, "out": (r.stdout + r.stderr)[-2000:]})
            if u.path == "/api/export":
                q = parse_qs(u.query)
                g = self._q
                fmt, chunk, chunks = g(q, "format", "csv"), g(q, "chunk", "0"), g(q, "chunks", "1")
                r = subprocess.run([sys.executable, str(WIKI / "scripts" / "export_all.py"),
                                    "--chunk", chunk, "--chunks", chunks],
                                   capture_output=True, text=True, timeout=300)
                return self.send_json({"ok": r.returncode == 0, "format": fmt,
                                       "out": (r.stdout + r.stderr)[-1000:],
                                       "files": {"csv": f"db/wiki_export_{chunk}.csv",
                                                 "notion": f"export_notion/notion_import_{chunk}.json",
                                                 "obsidian": "export_obsidian/"}})
            return self.send_json({"error": "unknown route", "routes": ROUTES}, 404)
        except Exception as ex:
            self.send_json({"error": str(ex), "type": type(ex).__name__}, 500)


def serve(port, host="127.0.0.1", quiet=False):
    H.quiet = quiet
    load()                                   # fail fast with a clear message
    httpd = ThreadingHTTPServer((host, port), H)
    httpd.daemon_threads = True
    print(f"Wiki API v{API_VERSION} on http://{host}:{port}  (site: /site/)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Blender AI Wiki API (stdlib only)")
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--host", default="127.0.0.1", help="localhost by default on purpose")
    ap.add_argument("--quiet", action="store_true", help="suppress request log")
    a = ap.parse_args()
    try:
        serve(a.port, a.host, a.quiet)
    except OSError as ex:
        if getattr(ex, "errno", None) in (48, 10048) or "in use" in str(ex).lower():
            print(f"Port {a.port} is already in use. Stop the other wiki_api.py, "
                  f"or run: python wiki_api.py --port {a.port + 1}", file=sys.stderr)
            sys.exit(2)
        raise
