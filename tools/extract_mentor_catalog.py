"""Extract every gel breast implant from the Mentor 2025 US Product Catalog
(169630-3, effective July 2025) into data/source/mentor.csv.

Usage: python3 tools/extract_mentor_catalog.py CATALOG.pdf

The catalog pages interleave labels from product drawings with the table text,
so plain text extraction is unreliable. Instead this reads word positions
(pdftotext -bbox) and, for each product code, takes the numbers printed on the
same baseline to its left, then assigns line/profile from the nearest table
heading above it. Tissue expanders and saline implants (pages 6-7) are skipped.
"""
import csv, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIELDS = ["manufacturer", "line", "catalog", "gel", "profile", "shape", "surface",
          "volume_cc", "diameter_cm", "projection_cm", "height_cm"]

# (pages, code pattern) -> line, gel, surface, shape
CODE_RULES = [
    ((2,),   r"3507\d{3}MC",       "MemoryGel",             "MemoryGel",       "Smooth",   "Round"),
    ((2,),   r"350\d{4}BC",        "MemoryGel",             "MemoryGel",       "Smooth",   "Round"),
    ((2,),   r"SUHE\d{3,4}",       "MemoryGel Enhance",     "MemoryGel",       "Smooth",   "Round"),
    ((3,),   r"S(MP|MH|HP)B\d{3}", "MemoryGel Boost",       "MemoryGel Boost", "Smooth",   "Round"),
    ((3,),   r"S(MP|MH|HP)X\d{3}", "MemoryGel Xtra",        "MemoryGel Xtra",  "Smooth",   "Round"),
    ((4,),   r"T(MP|HP)X\d{3}",    "MemoryGel Xtra SILTEX", "MemoryGel Xtra",  "Textured", "Round"),
    ((4,),   r"354\d{4}MC",        "MemoryGel SILTEX",      "MemoryGel",       "Textured", "Round"),
    ((4,),   r"354\d{4}",          "MemoryGel SILTEX",      "MemoryGel",       "Textured", "Round"),
    ((5,),   r"3[35]4\d{4}",       "MemoryShape SILTEX",    "MemoryShape",     "Textured", "Shaped"),
]

# Table headings as printed, mapped to the profile name stored in the data.
HEADINGS = {
    "Moderate Classic Profile": "Moderate Classic",
    "Moderate Plus Profile": "Moderate Plus",
    "High Profile": "High",
    "Ultra High Profile": "Ultra High",
    "Ultra High Profile Enhance": "Ultra High",
    "Moderate High Profile": "Moderate High",
    "Moderate Plus Profile Xtra": "Moderate Plus",
    "Moderate High Profile Xtra": "Moderate High",
    "High Profile Xtra": "High",
    "Moderate Plus Xtra": "Moderate Plus",
    # MemoryShape: "<code> Profile, <Height> Height/" then "<Projection> Projection"
    "TM+ Profile, Tall Height/": "TM+ Tall Height, Moderate Plus Projection",
    "TH Profile, Tall Height/": "TH Tall Height, High Projection",
    "MM Profile, Medium Height/": "MM Medium Height, Moderate Projection",
    "MM+ Profile, Medium Height/": "MM+ Medium Height, Moderate Plus Projection",
    "MH Profile, Medium Height/": "MH Medium Height, High Projection",
    "LM+ Profile, Low Height/": "LM+ Low Height, Moderate Plus Projection",
}


def words_by_page(pdf):
    html = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True,
                          text=True, check=True).stdout
    pages = []
    for pg in html.split("<page ")[1:]:
        pages.append([(float(a), float(b), float(c), float(d), w) for a, b, c, d, w in
                      re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" '
                                 r'yMax="([\d.]+)">([^<]*)</word>', pg)])
    return pages


def find_headings(words):
    """Locate every heading phrase from HEADINGS on the page, returning (x, y, profile).
    Words are grouped by baseline and sorted by x, because the PDF's word order
    interleaves labels from the product drawings."""
    lines = []
    # drawing labels ("round mod plus", "memshape_MM") share the headings' baselines; they are lowercase
    for w in sorted((w for w in words if w[4][:1].isupper()), key=lambda w: (w[1], w[0])):
        if lines and abs(lines[-1][-1][1] - w[1]) < 2:
            lines[-1].append(w)
        else:
            lines.append([w])
    found = []
    for line in lines:
        line.sort(key=lambda w: w[0])
        for i, (x0, y0, x1, y1, w) in enumerate(line):
            if i and 0 <= x0 - line[i-1][2] < 12:
                continue  # continues the previous phrase
            phrase, j = w, i + 1
            while j < len(line) and 0 <= line[j][0] - line[j-1][2] < 12:
                phrase += " " + line[j][4]; j += 1
            best = max((h for h in HEADINGS if phrase == h or phrase.startswith(h + " ")),
                       key=len, default=None)
            if best:
                found.append((x0, y0, HEADINGS[best]))
    return found


def extract(pdf):
    rows = []
    for pno, words in enumerate(words_by_page(pdf), 1):
        if pno not in (2, 3, 4, 5):
            continue
        headings = find_headings(words)
        for x0, y0, x1, y1, w in words:
            rule = next((r for r in CODE_RULES if pno in r[0] and re.fullmatch(r[1], w)), None)
            if not rule:
                continue
            _, _, line, gel, surface, shape = rule
            cols = ["Vol.", "Wid.", "Hght.", "Proj."] if shape == "Shaped" else ["Vol.", "Dia.", "Proj."]
            # the table's column headers: nearest "Vol." above this code, within the table width
            vol_hdrs = [(y0 - b, a, b) for a, b, c, d, t in words
                        if t == "Vol." and b < y0 and 0 < x0 - a < 200]
            assert vol_hdrs, (pno, w)
            _, hx, hy = min(vol_hdrs)
            centers = []
            for col in cols:
                hs = [(a + c) / 2 for a, b, c, d, t in words if t == col and abs(b - hy) < 2 and 0 <= a - hx < 160]
                assert len(hs) == 1, (pno, w, col, hs)
                centers.append(hs[0])
            # the number printed under each column header on this code's baseline
            nums = []
            for cx in centers:
                hits = [(abs((a + c) / 2 - cx), t) for a, b, c, d, t in words
                        if abs(b - y0) < 2.5 and abs((a + c) / 2 - cx) < 12 and re.fullmatch(r"\d+(\.\d)?", t)]
                hits.sort()
                assert hits and hits[0][0] < 3, (pno, w, cx, hits)   # value is centred under its header
                nums.append(float(hits[0][1]))
            want = len(cols)
            # heading: nearest above, whose left edge is within the table width
            cands = [(y0 - hy, prof) for hx, hy, prof in headings if hy < y0 and -40 <= x0 - hx <= 200]
            assert cands, (pno, w)
            profile = min(cands)[1]
            rec = dict(manufacturer="Mentor", line=line, catalog=w, gel=gel, profile=profile,
                       shape=shape, surface=surface, volume_cc=int(nums[0]),
                       diameter_cm=nums[1], projection_cm=nums[-1],
                       height_cm=nums[2] if want == 4 else "")
            rows.append(rec)
    return rows


def encoded_volume(r):
    """Volume encoded in the product code, or None when the code does not carry it."""
    c, p = r["catalog"], r["profile"]
    if m := re.fullmatch(r"[A-Z]+(\d{3,4})", c):            # SUHE930, SMPB130, TMPX115
        return int(m.group(1))
    if m := re.fullmatch(r"3507(\d{3})MC", c):             # 3507130MC -> 130
        return int(m.group(1))
    if re.fullmatch(r"350\d{4}BC", c):                      # 3501251BC -> 125 ; 3505135BC (UHP) -> 135
        return int(c[4:7]) if p == "Ultra High" else int(c[3:6])
    if m := re.fullmatch(r"354(\d{3})\dMC", c):            # 3541307MC -> 130
        return int(m.group(1))
    if r["shape"] == "Shaped":
        return None                                          # MemoryShape codes do not encode volume
    if re.fullmatch(r"354\d{4}", c):                        # 3541251 -> 125 ; 3544125 (HP) / 3545135 (UHP)
        return int(c[4:7]) if p in ("High", "Ultra High") else int(c[3:6])
    return None                                              # MemoryShape 354xxxx (page 5)


def check(rows):
    for r in rows:
        enc = encoded_volume(r)
        assert enc is None or enc == r["volume_cc"], ("volume/code mismatch", r["catalog"], r["volume_cc"], enc)
        assert r["projection_cm"] < r["diameter_cm"], ("dimension order", r["catalog"])
    cats = [r["catalog"] for r in rows]
    assert len(cats) == len(set(cats)), "duplicate codes"


if __name__ == "__main__":
    rows = extract(pathlib.Path(sys.argv[1]))
    check(rows)
    out = ROOT / "data" / "source" / "mentor.csv"
    with open(out, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=FIELDS); wr.writeheader(); wr.writerows(rows)
    from collections import Counter
    for k, n in sorted(Counter((r["line"], r["profile"], r["surface"]) for r in rows).items()):
        print(f"{n:3}  {k[0]:24} {k[1]:45} {k[2]}")
    print(len(rows), "implants ->", out)
