#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-tests for the wiki pipeline. stdlib unittest, no deps.

    python scripts/test_wiki.py            # fast suite (~10 s)
    WIKI_SLOW_TESTS=1 python scripts/test_wiki.py   # + full validate.py run

Covers the invariants that are easy to break silently:
  * frontmatter / tag / id-scheme parsing in build_database
  * multilang mirror pairing (a translation must have an original)
  * DB invariants (unique ids, non-empty bodies, required meta keys)
  * site artifacts the browser actually loads (meta.json + chunks/*)
  * HTTP contract of wiki_api.py, incl. ETag/304, pagination, 404/405
"""
import json, os, socket, sys, threading, unittest, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WIKI = Path(r"C:\BLENDER ai\WIKI")
sys.path.insert(0, str(WIKI / "scripts"))
import build_database as bd          # noqa: E402
import wiki_api                      # noqa: E402

DB = json.loads((WIKI / "db" / "wiki_database.json").read_text(encoding="utf-8"))
IDX = json.loads((WIKI / "db" / "search_index.json").read_text(encoding="utf-8"))
REQUIRED_META = ("id", "title", "category", "type", "tags", "language")


class TestParsing(unittest.TestCase):
    def test_frontmatter(self):
        md = "---\nid: x\nlang: es\ntags: [a, b]\n---\n# Title\nbody\n"
        fm = bd.extract_frontmatter(md)
        self.assertEqual(fm.get("id"), "x")
        self.assertEqual(fm.get("lang"), "es")
        self.assertEqual(fm.get("tags"), ["a", "b"])
        self.assertEqual(bd.extract_frontmatter("# no fm\n"), {})

    def test_tags_drop_hex_colors_and_digits(self):
        md = "Теги: #retopology #8b7355 #12 #uv\n"
        probe = WIKI / "prompts" / "01_geometry_basics.md"   # must exist: stat() is called
        meta = bd.extract_metadata(md, probe)
        self.assertIn("retopology", meta["tags"])
        self.assertIn("uv", meta["tags"])
        self.assertNotIn("8b7355", meta["tags"])   # hex color, not a tag
        self.assertNotIn("12", meta["tags"])

    def test_id_scheme(self):
        """multilang id must be {stem}__{lang} + orig_id == stem"""
        f = WIKI / "multilang" / "es" / "prompts" / "01_geometry_basics.md"
        if not f.exists():
            self.skipTest("no multilang prompts")
        meta = bd.extract_metadata(f.read_text(encoding="utf-8"), f)
        self.assertEqual(meta["id"], "01_geometry_basics__es")
        self.assertEqual(meta["orig_id"], "01_geometry_basics")
        self.assertEqual(meta["language"], "es")

    def test_sections_split(self):
        secs = bd.extract_content_sections("# T\n\n## A\nbody a\n\n## B\nbody b\n")
        self.assertEqual([s["heading"] for s in secs], ["A", "B"])

    def test_fallback_frontmatter_matches_pyyaml_on_real_corpus(self):
        """
        ADR 0004: the pipeline must work without PyYAML. Prove the minimal
        parser is equivalent on every real frontmatter block, not on a toy.
        """
        if bd.yaml is None:
            self.skipTest("PyYAML not installed")
        import re as _re
        checked = 0
        mismatches = []
        for f in (WIKI / "multilang").rglob("*.md"):
            t = f.read_text(encoding="utf-8")
            m = _re.match(r"^---\n(.*?)\n---", t, _re.DOTALL)
            if not m:
                continue
            block = m.group(1)
            try:
                ref = bd.yaml.safe_load(block)
            except Exception:
                continue
            got = bd.parse_frontmatter_min(block)
            checked += 1
            if ref != got:
                mismatches.append((str(f.relative_to(WIKI)), ref, got))
            if len(mismatches) > 3:
                break
        self.assertGreater(checked, 500, "corpus too small for this check to mean anything")
        self.assertEqual(mismatches, [], f"fallback parser diverged: {mismatches[:2]}")

    def test_fallback_parser_primitives(self):
        self.assertEqual(bd.parse_frontmatter_min("a: 1\nb: x\nc: true\nd: 1.5"),
                         {"a": 1, "b": "x", "c": True, "d": 1.5})
        self.assertEqual(bd.parse_frontmatter_min("t: [a, b]"), {"t": ["a", "b"]})
        self.assertEqual(bd.parse_frontmatter_min("l:\n  - one\n  - two"), {"l": ["one", "two"]})
        self.assertEqual(bd.parse_frontmatter_min('q: "x: y"'), {"q": "x: y"})


class TestCorpus(unittest.TestCase):
    def test_no_duplicate_ids(self):
        ids = [e["meta"]["id"] for e in DB["entries"]]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids: {len(ids) - len(set(ids))}")

    def test_meta_keys_and_body(self):
        for e in DB["entries"]:
            m = e["meta"]
            for k in REQUIRED_META:
                self.assertIn(k, m, f"{m.get('id')} missing meta.{k}")
            self.assertTrue((e.get("full_content") or "").strip(), f"{m['id']} empty body")
            self.assertTrue(e.get("file_path"))

    def test_multilang_parity(self):
        """Every translation must have a matching original file."""
        missing = []
        for lang in ("en", "ru", "es", "de", "zh"):
            base = WIKI / "multilang" / lang
            if not base.exists():
                continue
            for f in base.rglob("*.md"):
                rel = f.relative_to(base)
                if len(rel.parts) < 2:
                    continue
                if not (WIKI / rel.parts[0] / rel.name).exists():
                    missing.append(f"{rel.as_posix()}")
        self.assertEqual(missing, [], f"translations without original: {missing[:10]}")

    def test_lang_coverage_equal(self):
        counts = {l: len(list((WIKI / "multilang" / l).rglob("*.md")))
                  for l in ("en", "ru", "es", "de", "zh")}
        self.assertEqual(len(set(counts.values())), 1, f"lang parity broken: {counts}")

    def test_content_hashes_match_files(self):
        """DB must not be stale relative to the markdown sources."""
        import hashlib
        stale = []
        for e in DB["entries"][:400]:
            p = WIKI / e["file_path"]
            if not p.exists():
                stale.append(e["file_path"])
                continue
            h = hashlib.md5(p.read_text(encoding="utf-8").encode()).hexdigest()[:16]
            if h != e.get("content_hash"):
                stale.append(e["file_path"])
        self.assertEqual(stale[:5], [], f"DB stale vs sources: {len(stale)} files")


class TestSiteArtifacts(unittest.TestCase):
    def test_meta_and_chunks_match_db(self):
        meta = json.loads((WIKI / "site" / "data" / "meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["total"], len(DB["entries"]), "meta.json out of sync with DB")
        cats = {m["category"] for m in meta["items"]}
        total = 0
        for c in cats:
            p = WIKI / "site" / "data" / "chunks" / f"entries_{c}.json"
            self.assertTrue(p.exists(), f"missing chunk {p.name}")
            total += json.loads(p.read_text(encoding="utf-8"))["total"]
        self.assertEqual(total, len(DB["entries"]), "chunk totals != DB total")

    def test_graph_has_precomputed_positions(self):
        g = json.loads((WIKI / "site" / "data" / "graph.json").read_text(encoding="utf-8"))
        self.assertTrue(g["nodes"])
        for n in g["nodes"][:50]:
            self.assertIn("x", n, "graph node without precomputed x")
            self.assertIn("y", n, "graph node without precomputed y")

    def test_site_assets_present(self):
        for f in ("index.html", "app.js", "style.css", "graph.html"):
            self.assertTrue((WIKI / "site" / f).exists(), f"site/{f} missing")


class TestApiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        wiki_api.H.quiet = True
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), wiki_api.H)
        cls.srv.daemon_threads = True
        cls.port = cls.srv.server_address[1]
        cls.th = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.th.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def get(self, path, headers=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(e.headers)

    def j(self, path):
        st, body, _ = self.get(path)
        return st, json.loads(body.decode("utf-8"))

    def test_health(self):
        st, d = self.j("/api/health")
        self.assertEqual(st, 200)
        self.assertTrue(d["ok"])
        self.assertEqual(d["entries"], len(DB["entries"]))
        self.assertIn("api", d, "health must advertise the API contract version")

    def test_version_and_openapi(self):
        st, v = self.j("/api/version")
        self.assertEqual(st, 200)
        self.assertIn("api", v)
        st, o = self.j("/api/openapi.json")
        self.assertEqual(st, 200)
        self.assertIn("/api/entry", o["paths"])

    def test_search_returns_items(self):
        st, d = self.j("/api/search?q=retopology&limit=5")
        self.assertEqual(st, 200)
        self.assertIsInstance(d["items"], list)
        if d["items"]:
            self.assertIn("score", d["items"][0])
            self.assertIn("title", d["items"][0])

    def test_list_pagination_is_consistent(self):
        st, a = self.j("/api/list?category=prompts&limit=10")
        self.assertEqual(st, 200)
        self.assertEqual(len(a["items"]), min(10, a["total"]))
        self.assertEqual(a["total_pages"], -(-a["total"] // a["limit"]))
        st, b = self.j("/api/list?category=prompts&limit=10&offset=10")
        self.assertNotEqual([x["id"] for x in a["items"]], [x["id"] for x in b["items"]])

    def test_entry_has_honest_truncation_flag(self):
        eid = DB["entries"][0]["meta"]["id"]
        st, d = self.j(f"/api/entry?id={eid}")
        self.assertEqual(st, 200)
        self.assertIn("truncated", d, "truncation must be explicit, not silent")
        self.assertEqual(d["full_content"], d["full_content"][:30000])
        st, _ = self.j("/api/entry?id=does-not-exist")
        self.assertEqual(st, 404)

    def test_graph_uses_precomputed_layout(self):
        st, d = self.j("/api/graph?limit=25")
        self.assertEqual(st, 200)
        self.assertLessEqual(len(d["nodes"]), 25)
        for n in d["nodes"][:10]:
            self.assertIn("x", n)

    def test_unknown_route_and_method_semantics(self):
        st, d = self.j("/api/nope")
        self.assertEqual(st, 404)
        self.assertIn("routes", d)
        st, d = self.j("/api/export")           # GET must not mutate state
        self.assertEqual(st, 405)

    def test_etag_304(self):
        st, body, hdr = self.get("/api/stats")
        self.assertEqual(st, 200)
        etag = hdr.get("ETag")
        self.assertTrue(etag, "responses must carry an ETag")
        st2, body2, _ = self.get("/api/stats", headers={"If-None-Match": etag})
        self.assertEqual(st2, 304)
        self.assertEqual(body2, b"")

    def test_db_cache_avoids_reparse(self):
        """Two requests in a row must reuse the cached DB (mtime unchanged)."""
        wiki_api.load()
        db1, _ = wiki_api.load()
        db2, _ = wiki_api.load()
        self.assertIs(db1, db2, "DB re-parsed on a cache hit")


@unittest.skipUnless(os.environ.get("WIKI_SLOW_TESTS"), "set WIKI_SLOW_TESTS=1")
class TestFullValidation(unittest.TestCase):
    def test_validate_script_passes(self):
        import subprocess
        r = subprocess.run([sys.executable, str(WIKI / "scripts" / "validate.py")],
                           capture_output=True, text=True, timeout=900)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:] + r.stderr[-1000:])


if __name__ == "__main__":
    unittest.main(verbosity=2)
