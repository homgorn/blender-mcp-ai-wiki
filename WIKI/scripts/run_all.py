#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-command pipeline. The build order is a real dependency graph, not a habit:
if you rebuild the site without rebuilding the DB, the site serves stale chunks
and validate() stays green. So: run everything, in order, from here.

    python scripts/run_all.py                 # full rebuild + validate + tests
    python scripts/run_all.py --fast          # skip exports (saves ~40 s)
    python scripts/run_all.py --skip-tests    # skip the unit suite
    python scripts/run_all.py --step build_site.py   # run a single step

Idempotent: every step can run twice with the same result.
Exit 0 = green pipeline, 1 = a step failed.
"""
import argparse, os, shutil, subprocess, sys, time
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

S = Path(r"C:\BLENDER ai\WIKI\scripts")
PY = sys.executable

# (label, argv, is_gate)  gates decide the exit code
CORE = [
    ("frontmatter fix",   [str(S / "fix_frontmatter.py")], True),
    ("lang frontmatter",  [str(S / "fix_lang_frontmatter.py")], True),
    # Tags feed the search index, /api/tags and the cross-reference graph. An
    # untagged article is invisible to all three, so filling them is part of
    # building the database, not a separate chore. Not a gate: a new file whose
    # title matches no vocabulary entry should not break the build.
    ("tag articles",      [str(S / "tag_articles.py")], False),
    ("mark stubs",        [str(S / "mark_stubs.py")], False),
    ("parity check",      [str(S / "check_missing.py")], True),
    ("build database",    [str(S / "build_database.py")], True),
    ("build graph",       [str(S / "build_graph.py")], True),
]

# Deliberately NOT part of the pipeline: complete_sections.py rewrites prose in
# the corpus (it converts "Setup 01, WF-01" into real links). A build must not
# silently edit source articles. Run it on purpose:
#     python WIKI/scripts/complete_sections.py [--refresh]
TAIL = [
    ("rebuild crossref",  [str(S / "rebuild_crossref.py")], False),
    ("build index",       [str(S / "build_index.py")], True),
    ("build site",        [str(S / "build_site.py")], True),
    ("og image",          [str(S / "make_og.py")], False),
]


def run(label, argv, tail=""):
    t0 = time.time()
    r = subprocess.run([PY, *argv], capture_output=True, text=True, timeout=1800)
    dt = time.time() - t0
    out = (r.stdout or "") + (r.stderr or "")
    status = "OK " if r.returncode == 0 else "FAIL"
    line = f"  [{status}] {label:<20} {dt:6.1f}s"
    if tail:
        line += f"  {tail}"
    print(line, flush=True)
    if r.returncode != 0:
        print(out[-1500:], file=sys.stderr)
    return r.returncode == 0, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="skip CSV/Notion/Obsidian exports")
    ap.add_argument("--skip-tests", action="store_true")
    ap.add_argument("--skip-site", action="store_true", help="skip the Astro build + SEO gates")
    ap.add_argument("--step", help="run one script by name and exit")
    a = ap.parse_args()

    if a.step:
        ok, _ = run(a.step, [str(S / a.step)])
        return 0 if ok else 1

    t0 = time.time()
    print("== pipeline ==")
    failed = []
    site = S.parent.parent / "web"   # the Astro project
    for label, argv, gate in CORE:
        ok, out = run(label, argv)
        if not ok and gate:
            failed.append(label)
    if failed:
        print(f"\nPIPELINE FAILED at: {', '.join(failed)}")
        return 1

    if not a.fast:
        for i in range(4):
            ok, _ = run(f"export chunk {i}/4",
                        [str(S / "export_all.py"), "--chunk", str(i), "--chunks", "4"])
            if not ok:
                failed.append("export")

    for label, argv, gate in TAIL:
        ok, _ = run(label, argv)
        if not ok and gate:
            failed.append(label)
    if failed:
        print(f"\nPIPELINE FAILED at: {', '.join(failed)}")
        return 1

    print("== gates ==")
    ok, out = run("validate.py", [str(S / "validate.py")])
    if not ok:
        print(out[-3000:])
        return 1
    if not a.skip_tests:
        ok, out = run("test_wiki.py", [str(S / "test_wiki.py")])
        if not ok:
            print(out[-3000:])
            return 1
    run("quality report", [str(S / "quality_report.py")])

    # --strict adds template conformance as a hard gate. It is on now that the
    # report reads 0: a section is considered present only if a marker matches
    # case-insensitively and MULTILANG does not count as a cross-reference.
    ok, out = run("validate.py --strict", [str(S / "validate.py"), "--strict"])
    if not ok:
        print(out[-2000:])
        return 1

    # The Astro site reads the database this pipeline just rebuilt, so it is
    # part of the same correctness chain — not a separate optional build.
    if not a.skip_site:
        # npm is a .cmd shim on Windows; subprocess needs its real path or it
        # is not found even though `npm` works in the shell.
        npm = shutil.which("npm") or shutil.which("npm.cmd")
        if npm is None:
            print("  [INFO] npm not found on PATH — skipping the Astro build")
        elif (site / "package.json").exists():
            # The Astro build bakes the origin into canonical/hreflang/sitemap.
            # Without it the build would ship localhost URLs, so a real one is
            # required for the site step even when the rest of the pipeline can
            # run anywhere.
            origin = os.environ.get("PUBLIC_SITE_URL", "").strip()
            if not origin or origin.startswith("http://"):
                print("  [WARN] PUBLIC_SITE_URL is unset or http:// — the site build would")
                print("         ship a localhost origin. Set PUBLIC_SITE_URL=https://... first.")
                return 1
            env = dict(os.environ)
            for label, cmd in [
                ("site build+verify", [npm, "run", "all"]),
                ("site preflight",    [npm, "run", "preflight"]),
            ]:
                ts = time.time()
                r = subprocess.run(cmd, cwd=str(site), capture_output=True, text=True,
                                   env=env, timeout=3600)
                dt = time.time() - ts
                tail = [ln for ln in (r.stdout or "").splitlines()
                        if "RESULT:" in ln or "md-twins" in ln]
                print(f"  [{'OK ' if r.returncode == 0 else 'FAIL'}] {label:<20} {dt:6.1f}s"
                      + (f"  {tail[-1][:80]}" if tail else ""), flush=True)
                if r.returncode != 0:
                    print((r.stdout + r.stderr)[-2500:], file=sys.stderr)
                    return 1
        else:
            print("  [INFO] web/ not present — skipping the Astro build")

    total = time.time() - t0
    print(f"\nPIPELINE GREEN in {total:.0f}s")
    print("local API (legacy site + search):  python scripts/wiki_api.py --port 8099")
    print("new Astro site:                    web/ -> npm run preview   (see web/README.md)")
    return 0


def out_tail(out):
    for ln in out.splitlines():
        if ln.startswith("OK "):
            return ln[:70]
    return ""


if __name__ == "__main__":
    sys.exit(main())
