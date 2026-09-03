#!/usr/bin/env python3
"""
Turn a BibTeX file into _data/publications.yml.

You normally do not need to run this yourself. Dropping an updated
publications.bib into the repository triggers the "Update publications"
GitHub Action, which runs this script and commits the result.

To run it by hand:
    python3 tools/bib_to_yaml.py publications.bib

Works with exports from Zotero, Google Scholar, Mendeley, EndNote and
anything else that emits standard BibTeX. Needs nothing but Python 3.

Names listed in LAB_MEMBERS are shown in bold on the website.
"""

import os
import re
import sys
import unicodedata

LAB_MEMBERS = [
    "Akay", "Pearson", "Hencel", "Shen", "Williams", "Brown", "Okon", "Agu",
    "Skukan", "Adesina", "D'Asaro", "Hammond", "Almototah",
]

# Checked in this order; the first field present becomes the venue.
VENUE_FIELDS = ["journal", "journaltitle", "booktitle", "repository",
                "archiveprefix", "howpublished", "publisher", "school"]

# LaTeX accent commands mapped to Unicode combining marks, so \'e composes
# into e-acute, \v{c} into c-caron, \c{c} into c-cedilla, and so on.
COMBINING = {
    "'": "\u0301", "`": "\u0300", "^": "\u0302", '"': "\u0308",
    "~": "\u0303", ".": "\u0307", "=": "\u0304", "u": "\u0306",
    "v": "\u030C", "c": "\u0327", "k": "\u0328", "H": "\u030B",
    "r": "\u030A", "d": "\u0323", "b": "\u0331",
}

# Standalone LaTeX commands with a direct Unicode equivalent.
COMMANDS = {
    "ss": "\u00df", "o": "\u00f8", "O": "\u00d8", "aa": "\u00e5",
    "AA": "\u00c5", "ae": "\u00e6", "AE": "\u00c6", "oe": "\u0153",
    "l": "\u0142", "L": "\u0141", "i": "i", "j": "j",
    "textendash": "\u2013", "textemdash": "\u2014",
    "textquotesingle": "'", "textprime": "\u2032",
    "textmu": "\u00b5", "mu": "\u03bc", "alpha": "\u03b1",
    "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4",
    "kappa": "\u03ba", "sigma": "\u03c3", "psi": "\u03c8",
    "textdegree": "\u00b0", "degree": "\u00b0",
    "&": "&", "%": "%", "_": "_", "$": "$", "#": "#",
}

# Wrappers whose *content* we keep but whose command we drop.
WRAPPERS = ("textit", "textbf", "emph", "textrm", "textsc", "text",
            "textsuperscript", "textsubscript", "mathrm", "mbox")


def clean(s):
    """Reduce a BibTeX field to plain Unicode text."""
    # \textit{Foo} -> Foo   (keep the content, lose the command)
    for w in WRAPPERS:
        s = re.sub(r"\\" + w + r"\s*\{([^{}]*)\}", r"\1", s)
    # \'{e} / \'e / \v{c} / \= u  -> composed accented character
    s = re.sub(r"\\([\'`^\"~.=uvckHrbd])\s*\{?\s*(\w)\s*\}?",
               lambda m: m.group(2) + COMBINING.get(m.group(1), ""), s)
    # \ss, \textendash, \&
    s = re.sub(r"\\([a-zA-Z]+|[&%_$#])\s*\{\s*\}|\\([a-zA-Z]+|[&%_$#])",
               lambda m: COMMANDS.get(m.group(1) or m.group(2), ""), s)
    s = re.sub(r"[{}$]", "", s)
    s = s.replace("--", "\u2013")
    s = re.sub(r"\s+", " ", s)
    s = unicodedata.normalize("NFC", s)
    return s.strip().rstrip(",").strip()


def split_entries(text):
    """Yield (type, body) for each @type{...} entry, respecting nested braces."""
    for match in re.finditer(r"@(\w+)\s*\{", text):
        kind = match.group(1).lower()
        i, depth = match.end(), 1
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        yield kind, text[match.end():i - 1]


def parse_fields(body):
    """Pull key = {value} or key = "value" pairs out of an entry body."""
    fields = {}
    for m in re.finditer(r"(\w+)\s*=\s*", body):
        key = m.group(1).lower()
        i = m.end()
        if i >= len(body):
            break
        if body[i] == "{":
            depth, j = 1, i + 1
            while j < len(body) and depth:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                j += 1
            value = body[i + 1:j - 1]
        elif body[i] == '"':
            j = body.find('"', i + 1)
            value = body[i + 1:j if j != -1 else len(body)]
        else:
            j = i
            while j < len(body) and body[j] not in ",\n":
                j += 1
            value = body[i:j]
        fields[key] = clean(value)
    return fields


def format_authors(raw):
    """'Akay, Alper and Miska, Eric' -> 'A. Akay, E. Miska', lab names bolded."""
    out = []
    for name in re.split(r"\s+and\s+", raw):
        name = name.strip()
        if not name or name.lower() == "others":
            continue
        if "," in name:
            last, first = [p.strip() for p in name.split(",", 1)]
        else:
            parts = name.split()
            last, first = parts[-1], " ".join(parts[:-1])
        initials = " ".join(f"{p[0]}." for p in re.split(r"[\s.-]+", first) if p)
        formatted = f"{initials} {last}".strip()
        if any(m.lower() == last.lower() for m in LAB_MEMBERS):
            formatted = f"<strong>{formatted}</strong>"
        out.append(formatted)
    return ", ".join(out)


def yaml_quote(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 tools/bib_to_yaml.py path/to/publications.bib")
    path = sys.argv[1]
    if not os.path.exists(path):
        sys.exit(f"No such file: {path}")
    text = open(path, encoding="utf-8", errors="replace").read()

    pubs = []
    for kind, body in split_entries(text):
        if kind in ("comment", "preamble", "string"):
            continue
        f = parse_fields(body)
        if not f.get("title"):
            continue

        venue = next((f[k] for k in VENUE_FIELDS if f.get(k)), "")
        raw_year = f.get("year") or f.get("date") or ""
        m = re.search(r"(19|20)\d{2}", raw_year)
        year = m.group(0) if m else "n.d."
        volume = f.get("volume", "")
        if volume and f.get("pages"):
            volume = f"{volume}:{f['pages']}"

        pubs.append({
            "title": f["title"].rstrip("."),
            "authors": format_authors(f.get("author", "") or f.get("editor", "")),
            "venue": venue,
            "volume": volume,
            "year": year,
            "doi": f.get("doi", "").replace("https://doi.org/", ""),
            "url": f.get("url", "") or (
                "https://doi.org/" + f["doi"] if f.get("doi") else ""),
        })

    # Zotero libraries commonly hold both the preprint and the journal version,
    # or the same paper imported twice. Keep the first of each DOI, else title.
    seen, unique = set(), []
    for p in pubs:
        key = p["doi"].lower() or re.sub(r"\W", "", p["title"]).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    dropped = len(pubs) - len(unique)
    pubs = unique

    pubs.sort(key=lambda p: (p["year"], p["title"]), reverse=True)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "_data", "publications.yml")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# Generated by tools/bib_to_yaml.py from publications.bib.\n")
        fh.write("# Editing this file by hand works, but re-running the\n")
        fh.write("# converter overwrites it. Edit publications.bib instead.\n\n")
        if not pubs:
            fh.write("[]\n")
        for p in pubs:
            fh.write(f"- title: {yaml_quote(p['title'])}\n")
            fh.write(f"  authors: {yaml_quote(p['authors'])}\n")
            fh.write(f"  venue: {yaml_quote(p['venue'])}\n")
            if p["volume"]:
                fh.write(f"  volume: {yaml_quote(p['volume'])}\n")
            fh.write(f"  year: {yaml_quote(p['year'])}\n")
            if p["doi"]:
                fh.write(f"  doi: {yaml_quote(p['doi'])}\n")
            if p["url"]:
                fh.write(f"  url: {yaml_quote(p['url'])}\n")
            fh.write("\n")

    print(f"Wrote {len(pubs)} publications to {out}")
    if dropped:
        print(f"({dropped} duplicate entr{'y' if dropped == 1 else 'ies'} skipped)")


if __name__ == "__main__":
    main()
