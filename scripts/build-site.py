#!/usr/bin/env python3
"""Build a publish-ready copy of the wiki for GitHub.

Excludes working files (log.md, open-questions.md, raw/, .claude/), converts
[[wiki-links]] to relative markdown links, and regenerates index.html with
GitHub blob URLs so the markdown renders. Source tree is left untouched.
"""
import pathlib, re, shutil, sys, json

SRC = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("/tmp/neobank-site")
REPO = "fernfant/neobank-stack"
BLOB = f"https://github.com/{REPO}/blob/main"
EXCLUDE = {"log.md", "open-questions.md", "index.html"}
SKIP_NAMES = {".DS_Store", "Thumbs.db", ".gitignore"}
NO_CONVERT = {"CLAUDE.md"}
EXCLUDE_DIRS = {"raw", ".claude", ".git", "__pycache__"}

ART = {
 "ref":  ("https://fernfant.github.io/neobank-stack/diagrams/reference-architecture.html", "Reference architecture", "Ten bands, three archetypes, the card-auth hot path, and Monzo Stand-in — a complete backup bank on a second cloud."),
 "indep":("https://fernfant.github.io/neobank-stack/summary/independent-bank.html", "Building an independent bank", "Own licence, own settlement account, own scheme membership \u2014 ten layers, every decision, and named vendor options at each."),
 "rails":("https://fernfant.github.io/neobank-stack/summary/payment-rails.html", "Payment rails", "Auth vs clearing vs settlement, reversal windows to scale, and four payment archetypes with named vendor options."),
 "monzo":("https://fernfant.github.io/neobank-stack/summary/monzo-payments.html", "Monzo payments", "The six-year insourcing arc, the deliberately monolithic scheme gateway, and why an internal transfer touches no rail at all."),
 "vend": ("https://fernfant.github.io/neobank-stack/summary/vendor-map.html", "Vendor map — who runs what", "43 vendors across 8 layers, with the banks publicly named as using each — and the gaps marked honestly."),
 "deep": ("https://fernfant.github.io/neobank-stack/summary/deep-dive.html", "The four you build", "Reconciliation, rail adapters, KYC orchestration, fraud — with real architectures and 30+ named packages."),
 "brief":("https://fernfant.github.io/neobank-stack/summary/summary-with-diagram.html", "Executive brief", "Nine minutes: six findings, three archetypes, where the two markets diverge, build-vs-buy defaults."),
}

def parse(f):
    t = f.read_text(); fm = {}
    m = re.match(r"---\n(.*?)\n---\n", t, re.S)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                k, v = line.split(":", 1); fm[k.strip()] = v.strip()
    sm = re.search(r"##\s*Summary\s*\n+(.+?)(?:\n\n|\Z)", t, re.S)
    desc = ""
    if sm:
        para = re.sub(r"\*\*|\*|`|\[\[|\]\]", "", " ".join(sm.group(1).split()))
        parts = re.split(r"(?<=[.!?])\s+", para)
        desc = parts[0]
        if len(desc) < 70 and len(parts) > 1: desc += " " + parts[1]
        if len(desc) > 190: desc = desc[:187].rsplit(" ", 1)[0] + "…"
    return fm, desc, t

# ---- gather ----
pages = []
for f in sorted((SRC / "wiki").rglob("*.md")):
    fm, desc, _ = parse(f)
    pages.append(dict(path=str(f.relative_to(SRC)), stem=str(f.relative_to(SRC / "wiki")).replace(".md", ""),
                      title=fm.get("title", "").strip(), desc=desc))
titles = {p["stem"]: p["title"] for p in pages}

# ---- copy tree, converting wiki-links ----
# Clear the output dir but PRESERVE .git — this dir is usually a checkout of the
# published repo, and blowing away .git turns every rebuild into a fresh history.
OUT.mkdir(parents=True, exist_ok=True)
for child in OUT.iterdir():
    if child.name == ".git": continue
    shutil.rmtree(child) if child.is_dir() else child.unlink()
copied = converted = 0
for f in SRC.rglob("*"):
    rel = f.relative_to(SRC)
    if any(part in EXCLUDE_DIRS for part in rel.parts): continue
    if f.is_dir(): continue
    if rel.name in EXCLUDE and len(rel.parts) == 1: continue
    if rel.name in SKIP_NAMES: continue
    dst = OUT / rel; dst.parent.mkdir(parents=True, exist_ok=True)
    if f.suffix == ".md" and rel.name not in NO_CONVERT:
        t = f.read_text()
        def repl(m):
            global converted
            stem = m.group(1)
            if stem not in titles: return m.group(0)
            converted += 1
            depth = len(rel.parts) - 1
            up = "../" * max(0, depth - 1) if rel.parts[0] == "wiki" else "wiki/"
            target = (up + stem + ".md") if rel.parts[0] == "wiki" else f"wiki/{stem}.md"
            return f"[{titles[stem]}]({target})"
        t = re.sub(r"\[\[([a-z0-9/-]+)\]\]", repl, t)
        if rel.name in {"README.md", "index.md"}:
            t = "\n".join(l for l in t.split("\n")
                          if "log.md" not in l and "open-questions.md" not in l)
        dst.write_text(t)
    elif f.suffix == ".md":
        t = f.read_text()
        if rel.name in {"README.md", "index.md"}:
            t = "\n".join(l for l in t.split("\n")
                          if "log.md" not in l and "open-questions.md" not in l)
        dst.write_text(t)
    else:
        shutil.copy2(f, dst)
    copied += 1

# ---- index.html with GitHub blob links ----
nsrc = len({u for p in (SRC).rglob("*.md") for u in re.findall(r"https?://[^\s)|]+", p.read_text())})
nwords = sum(len(p.read_text().split()) for p in (SRC / "wiki").rglob("*.md"))

def sel(pred): return [p for p in pages if pred(p)]
layers = sorted(sel(lambda p: "/layers/" in p["path"]), key=lambda p: p["path"])
deep = sorted(sel(lambda p: "/deep-dives/" in p["path"]), key=lambda p: p["path"])
banksuk = [p for p in pages if "/banks/" in p["path"] and any(k in p["title"] for k in ("UK", "Germany"))]
banksus = [p for p in pages if "/banks/" in p["path"] and p not in banksuk]
rest = sel(lambda p: "/vendors/" in p["path"] or "/comparisons/" in p["path"])
overview = sel(lambda p: p["path"] == "wiki/overview.md")

def li(p):
    return (f'<li><a href="{BLOB}/{p["path"]}"><span class="t">{p["title"]}</span>'
            f'<span class="d">{p["desc"]}</span></a></li>')
def files(items):
    return '<div class="files">' + "".join(f'<a href="{BLOB}/{h}">{lbl}</a>' for h, lbl in items) + "</div>"

css = (SRC / "scripts" / "_site.css").read_text()
html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Neobank Stack — how UK and USA neobanks are actually built</title>
<meta name="description" content="A sourced, self-maintaining knowledge base on neobank technology stacks: ledger, payment rails, card issuing, financial crime, credit and infrastructure.">
{css}</head><body>
<div class="wrap">
<header class="top">
  <p class="eyebrow">UK &amp; USA neobank technology research</p>
  <h1>Neobank Stack</h1>
  <p class="standfirst">How UK and USA neobanks are actually built — the ledger, the rails, the card stack, financial crime, credit, data and the infrastructure underneath. Every non-obvious claim is sourced and confidence-tagged.</p>
  <p class="meta"><span><b>{len(pages)}</b> pages</span><span><b>{nsrc}</b> sources</span><span><b>{nwords:,}</b> words</span><span><b>11</b> banks</span><span><a href="https://github.com/{REPO}">GitHub</a></span></p>
</header>

<div class="prose"><h2>Start here</h2>
<p class="lede">Four rendered reads. Everything below is the source material behind them.</p></div>
<div class="cards prose">
{''.join(f'<a class="card" href="{u}"><span class="k">{k}</span><span class="h">{t}</span><span class="p">{d}</span></a>' for k,(u,t,d) in [("Architecture",ART["ref"]),("Independent bank",ART["indep"]),("Payment rails",ART["rails"]),("Monzo",ART["monzo"]),("Attribution",ART["vend"]),("Deep dive",ART["deep"]),("Summary",ART["brief"])])}
</div>

<div class="prose"><div class="new">
<p class="eyebrow">Selected findings</p>
<p><strong>Monzo Stand-in</strong> — a complete backup bank on a different cloud: 18 services on GCP against ~3,000 on AWS, at ~1% of the cost, with real customers running on it continuously. The strongest public answer to the cloud-concentration question.</p>
<p><strong>Balance reads amplify with account age</strong> — and if the read is too slow during card authorisation, the scheme approves on your behalf, beyond available balance, with your fraud checks never running.</p>
<p><strong>Both regulators converged independently</strong> on continuous, provable reconciliation — the FCA through safeguarding rules, the FDIC through a bankruptcy. Build that subsystem first, in either market.</p>
</div>
<h2>The thesis</h2></div>
<ul class="idx prose">{''.join(li(p) for p in overview)}{li(layers[0])}</ul>

<div class="prose"><h2>The ten layers</h2>
<p class="lede">What the options are, what the trade-off is, and what each choice forces downstream.</p></div>
<ul class="idx prose">{''.join(li(p) for p in layers[1:])}</ul>

<div class="prose"><h2>Deep dives — the four you build</h2>
<p class="lede">Real implementations, named open-source packages, and the vendors still worth paying.</p></div>
<ul class="idx prose">{''.join(li(p) for p in deep)}</ul>

<div class="prose"><h2>The banks</h2></div>
<div class="prose two">
<section><h3>UK &amp; Europe</h3><ul class="idx">{''.join(li(p) for p in banksuk)}</ul></section>
<section><h3>United States</h3><ul class="idx">{''.join(li(p) for p in banksus)}</ul></section>
</div>

<div class="prose"><h2>Vendors &amp; comparisons</h2></div>
<ul class="idx prose">{''.join(li(p) for p in rest)}</ul>

<div class="prose">
<h2>Templates &amp; diagrams</h2>
<p class="lede">For designing your own stack, or interrogating someone else's.</p>
{files([("templates/architecture-diagram-template.md","architecture-diagram-template.md"),
        ("templates/key-questions.md","key-questions.md — 100 questions"),
        ("templates/vendor-evaluation-scorecard.md","vendor-evaluation-scorecard.md"),
        ("diagrams/reference-architecture.mmd","reference-architecture.mmd"),
        ("diagrams/uk-neobank.mmd","uk-neobank.mmd"),
        ("diagrams/usa-neobank.mmd","usa-neobank.mmd"),
        ("diagrams/card-auth-sequence.mmd","card-auth-sequence.mmd"),
        ("diagrams/recon-flow.mmd","recon-flow.mmd")])}

<h2>Method</h2>
<p class="lede">Sourced, tagged, and maintained by scheduled agents rather than by hand.</p>
<p>Every non-obvious claim carries a confidence tag — <strong>confirmed</strong> when a company or regulator said it, <strong>reported</strong> for credible third parties, <strong>inferred</strong> when deduced from job ads or vendor customer lists. Anything sourced from more than about eighteen months ago is dated, because a 2020 fact driving a 2026 recommendation is the most dangerous thing in a document like this. Vendor-published figures are marked as such: much of the vendor-comparison material in this sector is content marketing, usable for building a shortlist and close to worthless as evidence.</p>
<p>A daily scout sweeps a watchlist of banks, vendors and regulators; a weekly lint hunts contradictions, stale claims and orphan pages. The schema they follow is in the repo.</p>
{files([("CLAUDE.md","CLAUDE.md — the schema"),("README.md","README.md"),("jobs/README.md","jobs/README.md")])}

<footer>
<p>Compiled from {nsrc} public sources — engineering blogs from Monzo, Chime, Uber, Airbnb, Stripe, N26 and Revolut; S-1 filings; and regulator publications from the FCA, PSR, Bank of England and FDIC. Corrections and missing attributions welcome via <a href="https://github.com/{REPO}/issues">issues</a>.</p>
</footer>
</div>
</div></body></html>"""
(OUT / "index.html").write_text(html)
(OUT / ".nojekyll").write_text("")
(OUT / ".gitignore").write_text(".DS_Store\n*.log\n")
print(f"built  → {OUT}\nfiles  : {copied}\nlinks  : {converted} wiki-links converted\npages  : {len(pages)}")
