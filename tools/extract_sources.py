"""Extract competitor catalogs into data/source/<manufacturer>.csv.

Usage:
  python3 tools/extract_sources.py --mentor MENTOR.xlsx --motiva MOTIVA.pdf --sientra SIENTRA.pdf

Sources used for the current data:
  Mentor  - MemoryGel variant specification spreadsheet (2026-11-04)
  Motiva  - SmoothSilk Round & SmoothSilk Ergonomix Order Form (US-ERGO1-0001 R1)
  Sientra - Round HSC & HSC+ Quick Reference Guide (MDC-0270 R11)
"""
import argparse, csv, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "source"
FIELDS = ["manufacturer", "line", "catalog", "gel", "profile", "shape", "surface",
          "volume_cc", "diameter_cm", "projection_cm"]


def pdf_text(path):
    return subprocess.run(["pdftotext", "-layout", str(path), "-"],
                          capture_output=True, text=True, check=True).stdout


def num(s):
    return float(re.sub(r"[^\d.]", "", str(s)))


def mentor(path):
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True).active
    rows = []
    for profile, code, vol, dia, proj in list(ws.iter_rows(values_only=True))[1:]:
        if not code:
            continue
        rows.append(dict(manufacturer="Mentor", line="MemoryGel", catalog=str(code).strip(),
                         gel="MemoryGel", profile=profile.replace(" Profile", "").strip(),
                         shape="Round", surface="Smooth", volume_cc=int(num(vol)),
                         diameter_cm=num(dia), projection_cm=num(proj)))
    return rows


def motiva(path):
    profiles = {"M": "Mini", "D": "Demi", "F": "Full"}
    rows = []
    for line in pdf_text(path).splitlines():
        m = re.match(r"\s*(\d+\.\d+)\s", line)
        if not m:
            continue
        base = float(m.group(1))
        for ergo, prof, vol, proj, vol2 in re.findall(r"\b(E?)RS([MDF])-(\d+)\s+(\d\.\d)\s+(\d+)", line):
            assert vol == vol2, line
            rows.append(dict(manufacturer="Motiva",
                             line="SmoothSilk Ergonomix" if ergo else "SmoothSilk Round",
                             catalog=f"{ergo}RS{prof}-{vol}", gel="ProgressiveGel",
                             profile=profiles[prof], shape="Round", surface="Smooth",
                             volume_cc=int(vol), diameter_cm=base, projection_cm=float(proj)))
    return rows


def sientra(path):
    suffix_profile = {"LP": "Low", "LPP": "Low Plus", "HP": "High", "XP": "Xtra High"}
    rows = []
    # Each record: width, projection, volume, then the catalog numbers on that row.
    rec = re.compile(r"(\d+\.\d+)\s+(\d\.\d)\s+(\d+)cc((?:\s+[12]0[5-7]\d\d-\d+[A-Z]+)+)")
    for line in pdf_text(path).splitlines():
        for wth, proj, vol, cats in rec.findall(line):
            for cat in cats.split():
                m = re.fullmatch(r"([12])0([5-7])(\d\d)-(\d+)([A-Z]+)", cat)
                textured, family, _, cvol, suffix = m.groups()
                assert int(cvol) == int(vol), line
                if suffix == "MP":
                    profile = "Moderate" if family == "5" or cat[3:5] == "12" else "Moderate Plus"
                else:
                    profile = suffix_profile[suffix]
                rows.append(dict(manufacturer="Sientra", line="HSC / HSC+",
                                 catalog=cat, gel="HSC+" if family == "7" else "HSC",
                                 profile=profile, shape="Round",
                                 surface="Textured" if textured == "2" else "Smooth",
                                 volume_cc=int(vol), diameter_cm=float(wth),
                                 projection_cm=float(proj)))
    return rows


def write(name, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows)} implants")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mentor"); ap.add_argument("--motiva"); ap.add_argument("--sientra")
    a = ap.parse_args()
    if a.mentor: write("mentor", mentor(a.mentor))
    if a.motiva: write("motiva", motiva(a.motiva))
    if a.sientra: write("sientra", sientra(a.sientra))
