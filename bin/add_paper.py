#!/usr/bin/env python3
"""Add a paper to _bibliography/papers.bib in one step.

  DOI         10.xxxx/... (or a doi.org URL): BibTeX from doi.org by content
              negotiation, falling back to the Crossref API. arXiv DOIs
              (10.48550/arXiv.*) go to the arXiv API.
  arXiv       an ID (2101.00001, hep-th/9901001) or an arxiv.org URL: metadata
              from the arXiv API, turned into an entry with eprint, archivePrefix,
              journal = "arXiv preprint arXiv:<id>" and the PDF link.
  .bib file   every entry in it.

Entries are normalized to the existing ones in papers.bib: "Last, First and
Last, First" authors, a pdf link (the DOI URL or the arXiv PDF), bibtex_show
and, with --selected, selected={true}. Fields other than the bibliographic
ones and the al-folio ones listed in _config.yml (filtered_bibtex_keywords) are
dropped. The key is lastnameYEARfirstword unless --key is given. An entry whose
DOI, arXiv ID or title is already in papers.bib is skipped. It warns when the
author list lacks the name highlighted on the page (scholar first_name/last_name
in _config.yml). Entries are appended as text; existing ones are not touched.

Network: only doi.org, api.crossref.org and export.arxiv.org are contacted
(redirects to any other host are not followed), with a 20 s timeout and no
retries. A local .bib file needs no network.
"""
import argparse
import html
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True  # importing the helper below must not leave bin/__pycache__
import sitelib
from sitelib import ROOT, die, warn, rel, fold

BIB = os.path.join(ROOT, "_bibliography", "papers.bib")
CONFIG = os.path.join(ROOT, "_config.yml")
HOSTS = {"doi.org", "api.crossref.org", "export.arxiv.org"}

# output order of the bibliographic fields; al-folio's own fields (from _config.yml) follow
CORE = ["title", "author", "year", "journal", "booktitle", "volume", "number", "pages",
        "publisher", "school", "institution", "doi", "eprint", "archiveprefix"]
CASE = {"archiveprefix": "archivePrefix", "primaryclass": "primaryClass"}
TYPES = {"article": "Article", "inproceedings": "InProceedings", "conference": "InProceedings",
         "incollection": "InCollection", "book": "Book", "misc": "Misc", "phdthesis": "PhdThesis",
         "mastersthesis": "MastersThesis", "techreport": "TechReport", "unpublished": "Unpublished"}
TEXT_FIELDS = {"title", "author", "journal", "booktitle", "publisher", "school", "institution"}
PARTICLES = {"von", "van", "de", "der", "den", "di", "da", "del", "della", "la", "le", "du", "dos", "ter", "ten"}
STOP = {"a", "an", "the", "on", "of", "in", "for", "to", "and", "with", "from", "by", "at", "is", "are", "how", "why", "what", "towards", "toward"}


# ---------------------------------------------------------------- BibTeX parsing

def parse_bib(text):
    """[(type, key, {field: (value, braced)})] for the @entries in text (not @string etc.)."""
    out, i = [], 0
    while (m := re.compile(r"@\s*([A-Za-z]+)\s*([{(])").search(text, i)):
        typ, i = m.group(1).lower(), m.end()
        close = "}" if m.group(2) == "{" else ")"
        depth, j = 1, i
        while j < len(text) and depth:
            c = text[j]
            if c in "{(" and (c == "{" or close == ")"):
                depth += 1
            elif c in "})" and (c == "}" or close == ")"):
                depth -= 1
            j += 1
        body, i = text[m.end():j - 1], j
        if typ in ("string", "comment", "preamble"):
            continue
        key, _, rest = body.partition(",")
        out.append((typ, key.strip(), parse_fields(rest)))
    return out


def parse_fields(s):
    fields, i, n = {}, 0, len(s)
    while i < n:
        m = re.compile(r"\s*,?\s*([A-Za-z][\w:.+-]*)\s*=\s*").match(s, i)
        if not m:
            break
        name, i = m.group(1).lower(), m.end()
        parts, braced = [], True
        while i < n:
            c = s[i]
            if c == "{":
                depth, j = 1, i + 1
                while j < n and depth:
                    depth += {"{": 1, "}": -1}.get(s[j], 0) if s[j - 1] != "\\" else 0
                    j += 1
                parts.append(s[i + 1:j - 1]); i = j
            elif c == '"':
                depth, j = 0, i + 1
                while j < n and not (s[j] == '"' and depth == 0):
                    depth += {"{": 1, "}": -1}.get(s[j], 0)
                    j += 1
                parts.append(s[i + 1:j]); i = j + 1
            else:
                m2 = re.compile(r"[^,#\s}]+").match(s, i)
                if not m2:
                    break
                parts.append(m2.group(0)); i = m2.end()
                braced = braced and m2.group(0).isdigit()
            m3 = re.compile(r"\s*#\s*").match(s, i)
            if not m3:
                break
            i = m3.end()
        fields[name] = (" ".join(" ".join(parts).split()), braced)
        m4 = re.compile(r"\s*,").match(s, i)
        i = m4.end() if m4 else i + 1
    return fields


# ---------------------------------------------------------------- normalizing

def split_top(s, sep):
    """Split on sep outside braces."""
    out, depth, cur, i = [], 0, "", 0
    while i < len(s):
        c = s[i]
        depth += {"{": 1, "}": -1}.get(c, 0)
        if depth == 0 and s.startswith(sep, i):
            out.append(cur); cur = ""; i += len(sep); continue
        cur += c; i += 1
    return out + [cur]


def norm_name(name):
    name = " ".join(name.split())
    parts = [p.strip() for p in split_top(name, ",")]
    if len(parts) >= 2:  # already "Last, First" (or "Last, Jr, First")
        return ", ".join(p for p in parts if p)
    toks = split_top(name, " ")
    if len(toks) == 1:
        return toks[0]
    k = len(toks) - 1
    for idx in range(1, len(toks) - 1):
        if toks[idx].lower() in PARTICLES:
            k = idx
            break
    return f"{' '.join(toks[k:])}, {' '.join(toks[:k])}"


def last_first(name):
    last, _, first = name.partition(",")
    return last.strip(), first.strip()


def escape(v):
    """Escape what breaks BibTeX/LaTeX in text fields; leave existing escapes and $math$ alone."""
    v = html.unescape(v)
    v = re.sub(r"(?<!\\)([&%#_])", r"\\\1", v)
    depth = 0
    for c in v:
        depth += {"{": 1, "}": -1}.get(c, 0)
        if depth < 0:
            break
    if depth:
        v = v.replace("{", "").replace("}", "")
    return v


def doi_of(f):
    for k in ("doi", "pdf", "url"):
        if k in f and (m := re.search(r"(10\.\d{4,9}/[^\s{}]+)", f[k][0])):
            return m.group(1).rstrip(".").lower()
    return None


def eprint_of(f):
    if "eprint" in f:
        return re.sub(r"v\d+$", "", f["eprint"][0].strip()).lower()
    for k in ("pdf", "url", "journal"):
        if k in f and (m := re.search(r"arxiv(?:\.org/(?:abs|pdf)/|:)\s*([\w.\-/]+?\d)(v\d+)?(?:\.pdf)?(?:\s|$|\})", f[k][0], re.I)):
            return m.group(1).lower()
    return None


def title_key(t):
    return re.sub(r"[^a-z0-9]", "", fold(re.sub(r"\\[a-zA-Z]+|[{}$\\]", "", t)))


def normalize(typ, fields, extras, selected):
    f = {k: v for k, v in fields.items()}
    out = {}
    if "author" in f:
        names = [norm_name(n) for n in split_top(f["author"][0], " and ") if n.strip()]
        f["author"] = (" and ".join(names), True)
    if "pages" in f:
        f["pages"] = (re.sub(r"\s*[-‐‑‒–—]+\s*", "--", f["pages"][0]), True)
    doi, ep = doi_of(f), eprint_of(f)
    if doi:
        f["doi"] = (doi, True)
    if "pdf" not in f:
        if doi:
            f["pdf"] = (f"https://doi.org/{doi}", True)
        elif ep:
            f["pdf"] = (f"https://arxiv.org/pdf/{ep}", True)
        elif "url" in f:
            f["pdf"] = f["url"]
    f.setdefault("bibtex_show", ("false", True))
    if selected:
        f["selected"] = ("true", True)
    tail = ["bibtex_show", "selected"]  # last, as in papers.bib
    for k in CORE + [e for e in extras if e not in CORE + tail] + tail:
        if k in f:
            v, braced = f[k]
            out[CASE.get(k, k)] = (escape(v) if k in TEXT_FIELDS else v, braced)
    return TYPES.get(typ, typ.capitalize()), out


def make_key(fields, taken):
    last = last_first(split_top(fields.get("author", ("anon",))[0], " and ")[0])[0]
    last = re.sub(r"[^a-z]", "", fold(re.sub(r"\\.|[{}]", "", last))) or "anon"
    year = re.sub(r"\D", "", fields.get("year", ("",))[0])[:4]
    words = [re.sub(r"[^a-z0-9]", "", fold(w)) for w in re.sub(r"\\[a-zA-Z]+|[{}$]", " ", fields.get("title", ("",))[0]).split()]
    word = next((w for w in words if w and w not in STOP), words[0] if words else "")
    base = f"{last}{year}{word}"
    key, n = base, 0
    while key.lower() in taken:
        n += 1
        key = base + "abcdefghijklmnopqrstuvwxyz"[n] if n < 26 else f"{base}{n}"
    return key


def format_entry(typ, key, fields):
    lines = [f"  {k}={{{v}}}" if braced else f"  {k}={v}" for k, (v, braced) in fields.items()]
    return f"@{typ}{{{key},\n" + ",\n".join(lines) + "\n}\n"


# ---------------------------------------------------------------- sources

def classify(arg):
    if arg.lower().endswith(".bib"):
        return "bib", arg
    m = re.search(r"(?:^|doi\.org/|doi:\s*)(10\.\d{4,9}/\S+)$", arg, re.I)
    if m:
        doi = urllib.parse.unquote(m.group(1))
        a = re.fullmatch(r"10\.48550/arxiv\.(.+)", doi, re.I)
        return ("arxiv", a.group(1)) if a else ("doi", doi)
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([\w.\-/]+?)(?:\.pdf)?/?$", arg, re.I) or \
        re.fullmatch(r"(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)", arg, re.I)
    if m:
        return "arxiv", m.group(1)
    return None, arg


def fetch_doi(doi):
    path = urllib.parse.quote(doi, safe="/:;()._-")
    try:
        status, body = sitelib.http_get(f"https://doi.org/{path}", accept="application/x-bibtex", hosts=HOSTS)
        if status == 200 and body.lstrip().startswith("@"):
            return body, "doi.org"
        why = f"HTTP {status}"
    except sitelib.OffListRedirect as e:
        why = f"redirected to {e}, which this script doesn't contact"
    print(f"doi.org: {why}; trying api.crossref.org")
    status, body = sitelib.http_get(f"https://api.crossref.org/works/{path}/transform/application/x-bibtex", hosts=HOSTS)
    if status == 200 and body.lstrip().startswith("@"):
        return body, "api.crossref.org"
    if status == 404:
        die(f"DOI {doi} not found (doi.org: {why}; api.crossref.org: HTTP 404)")
    die(f"could not get BibTeX for {doi} (doi.org: {why}; api.crossref.org: HTTP {status})")


ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def arxiv_entry(xml_text, want):
    """(type, fields) from an arXiv API Atom response."""
    root = ET.fromstring(xml_text)
    e = root.find("a:entry", ATOM)
    if e is None or "/api/errors" in (e.findtext("a:id", "", ATOM)) or not e.findtext("a:title", "", ATOM).strip():
        die(f"arXiv ID {want} not found")
    abs_id = e.findtext("a:id", "", ATOM)
    ident = re.sub(r"v\d+$", "", abs_id.split("/abs/", 1)[-1])
    title = " ".join(e.findtext("a:title", "", ATOM).split())
    authors = [" ".join(a.findtext("a:name", "", ATOM).split()) for a in e.findall("a:author", ATOM)]
    year = e.findtext("a:published", "", ATOM)[:4]
    f = {
        "title": (title, True),
        "author": (" and ".join(authors), True),
        "year": (year, True),
        "journal": (f"arXiv preprint arXiv:{ident}", True),
        "eprint": (ident, True),
        "archiveprefix": ("arXiv", True),
        "pdf": (f"https://arxiv.org/pdf/{ident}", True),
    }
    doi = e.findtext("arxiv:doi", "", ATOM).strip()
    if doi:
        f["doi"] = (doi, True)
    return "article", f


def fetch_arxiv(ident):
    q = urllib.parse.urlencode({"id_list": ident})
    status, body = sitelib.http_get(f"https://export.arxiv.org/api/query?{q}", accept="application/atom+xml", hosts=HOSTS)
    if status != 200:
        die(f"export.arxiv.org returned HTTP {status} for {ident}")
    return arxiv_entry(body, ident)


# ---------------------------------------------------------------- config

def scholar_names():
    text = open(CONFIG, encoding="utf-8").read()
    block = re.search(r"^scholar:\n((?:[ \t]+.*\n|\n)*)", text, re.M)
    names = {}
    for key in ("first_name", "last_name"):
        m = re.search(rf"^\s+{key}:\s*\[(.*?)\]", block.group(1) if block else "", re.M)
        names[key] = [v.strip().strip("\"'") for v in m.group(1).split(",")] if m else []
    return names["first_name"], names["last_name"]


def config_extras():
    text = open(CONFIG, encoding="utf-8").read()
    m = re.search(r"^filtered_bibtex_keywords:\s*\[(.*?)\]", text, re.M | re.S)
    return [w.strip().lower() for w in m.group(1).split(",") if w.strip()] if m else ["bibtex_show", "selected", "pdf"]


def highlight_check(fields, firsts, lasts):
    authors = [last_first(n) for n in split_top(fields.get("author", ("",))[0], " and ")]
    strip = lambda s: re.sub(r"[*∗†‡§¶‖&^{}]", "", s)
    if any(strip(l) in lasts and f in firsts for l, f in authors):
        return None
    near = [f"{l}, {f}" for l, f in authors if strip(l) in lasts or fold(strip(l)) in [fold(x) for x in lasts]]
    want = f"{lasts[0] if lasts else '?'}, {firsts[0] if firsts else '?'}"
    if near:
        return f"author list has {', '.join(near)} but not exactly '{want}', so the name won't be highlighted"
    return f"'{want}' (scholar first_name/last_name in _config.yml) is not in the author list, so no name will be highlighted"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="DOI, arXiv ID or URL, or path/to/file.bib")
    ap.add_argument("--key", help="citation key (default: lastnameYEARfirstword); one entry only")
    ap.add_argument("--selected", action="store_true", help="set selected={true} (shown on the about page)")
    ap.add_argument("--dry-run", action="store_true", help="print what would change and write nothing")
    a = ap.parse_args()

    kind, val = classify(a.source.strip())
    try:
        if kind == "bib":
            if not os.path.isfile(val):
                die(f"no such file: {val}")
            entries = [(t, f) for t, _, f in parse_bib(open(val, encoding="utf-8").read())]
            if not entries:
                die(f"no BibTeX entries in {val}")
            print(f"read {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} from {val}")
        elif kind == "doi":
            body, host = fetch_doi(val)
            entries = [(t, f) for t, _, f in parse_bib(body)]
            if not entries:
                die(f"{host} returned no BibTeX entry for {val}")
            print(f"fetched {val} from {host}")
        elif kind == "arxiv":
            entries = [fetch_arxiv(val)]
            print(f"fetched arXiv:{val} from export.arxiv.org")
        else:
            die(f"'{val}' is not a DOI (10.xxxx/...), an arXiv ID or URL, or a .bib file")
    except ConnectionError as e:
        die(f"network error: {e}")
    if a.key and len(entries) > 1:
        die(f"--key needs a single entry, but there are {len(entries)}")
    if a.key and not re.fullmatch(r"[A-Za-z][\w:.\-]*", a.key):
        die(f"--key '{a.key}' has characters BibTeX keys can't contain")

    bib_text = open(BIB, encoding="utf-8").read()
    existing = parse_bib(bib_text)
    taken = {k.lower() for _, k, _ in existing}
    seen = {"doi": {}, "eprint": {}, "title": {}}
    for _, k, f in existing:
        for name, v in (("doi", doi_of(f)), ("eprint", eprint_of(f)), ("title", title_key(f.get("title", ("",))[0]))):
            if v:
                seen[name][v] = k
    extras = config_extras()
    firsts, lasts = scholar_names()

    blocks, added = [], []
    for typ, fields in entries:
        if not fields.get("title", ("",))[0] or not re.search(r"\d{4}", fields.get("year", ("",))[0]):
            warn(f"skipping an entry without a title or year: {fields.get('title', ('?',))[0][:60]}")
            continue
        typ, f = normalize(typ, fields, extras, a.selected)
        ids = (("doi", doi_of(f)), ("eprint", eprint_of(f)), ("title", title_key(f["title"][0])))
        dup = next(((n, v, seen[n][v]) for n, v in ids if v and v in seen[n]), None)
        if dup:
            print(f"skip: already in {rel(BIB)} as '{dup[2]}' (same {dup[0]}): {f['title'][0]}")
            continue
        if a.key:
            if a.key.lower() in taken:
                die(f"key '{a.key}' is already used in {rel(BIB)}")
            key = a.key
        else:
            key = make_key(f, taken)
        taken.add(key.lower())
        for n, v in ids:
            if v:
                seen[n][v] = key
        if (msg := highlight_check(f, firsts, lasts)):
            warn(f"{key}: {msg}")
        blocks.append(format_entry(typ, key, f))
        added.append(key)

    if not blocks:
        print("nothing to add")
        return
    block = "\n".join(blocks)
    tag = "would " if a.dry_run else ""
    print(f"{tag}append {len(blocks)} entr{'y' if len(blocks) == 1 else 'ies'} to {rel(BIB)}:")
    print("".join("    " + ln + "\n" for ln in block.rstrip("\n").split("\n")), end="")
    if a.dry_run:
        print("dry run: nothing written")
        return
    sitelib.append_text(BIB, block, False)
    print(f"added {', '.join(added)} to {rel(BIB)}")
    print(f"next: check the entry (venue name, title capitalization), then git add {rel(BIB)} && git commit, and push")


if __name__ == "__main__":
    main()
