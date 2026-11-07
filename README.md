# Implant Match-Up Guide

Match breast implants across manufacturers by dimensions and gel type, with
**Allergan Natrelle INSPIRA** as the base that every other implant is compared against.

Open `index.html` in any browser. It has no server or internet dependency, so it works offline.

## How matching works

1. Choose an Allergan implant by catalog number (e.g. `SRX-400`) or by gel, profile and volume.
2. Candidates are filtered by:
   - **gel tier**: each manufacturer's gel is mapped to Responsive, SoftTouch or Cohesive in `data/gels.js`
   - **shape**: round or shaped (MemoryShape implants also carry a height)
   - **surface**: smooth or textured
   - **maximum base-width difference**
   - **manufacturer**
3. Results are ranked by `3 × |Δwidth| + 2 × |Δprojection| + |Δvolume| / 100`, so base width counts most, then projection, then volume.

## Data

| Manufacturer | Lines | Gels | Implants | Source |
| --- | --- | --- | --- | --- |
| Allergan (base) | Natrelle INSPIRA smooth round | Responsive, SoftTouch, Cohesive | 300 | Product Order Form MBD125570-v4 01/22 (hand transcribed) |
| Mentor | MemoryGel, Enhance, Xtra, Boost (smooth round); MemoryGel SILTEX, Xtra SILTEX (textured round); MemoryShape SILTEX (textured shaped) | MemoryGel, MemoryGel Xtra, MemoryGel Boost, MemoryShape | 429 | Product Catalog 169630-3, effective July 2025 |
| Motiva | SmoothSilk Round, SmoothSilk Ergonomix | ProgressiveGel | 81 | Order Form US-ERGO1-0001 R1 |
| Sientra | Round, smooth and textured | HSC, HSC+ | 304 | Quick Reference Guide MDC-0270 R11 |

| File | Purpose |
| --- | --- |
| `tools/allergan_source.py` | Hand transcription of the Allergan order form tables |
| `tools/extract_mentor_catalog.py` | Parses the Mentor catalog PDF (by word position) into `data/source/mentor.csv` |
| `tools/extract_sources.py` | Parses the Motiva and Sientra files into `data/source/*.csv` |
| `tools/build_data.py` | Merges everything into `data/implants.csv` and `data/implants.js` |
| `data/gels.js` | Gel equivalence table |

### Gel equivalence (confirmed 2026-11-07)

| Allergan tier | Equivalent gels |
| --- | --- |
| Responsive | Mentor MemoryGel, Motiva ProgressiveGel |
| SoftTouch | Mentor MemoryGel Xtra, Sientra HSC |
| Cohesive | Mentor MemoryGel Boost, Mentor MemoryShape, Sientra HSC+ |

If a gel is added or a tier changed, set `GEL_MAP_CONFIRMED = false` in `data/gels.js` until it is confirmed again.

### Adding a manufacturer

Add a parser to `tools/extract_sources.py` (or write `data/source/<name>.csv` with the same columns),
run `python3 tools/build_data.py`, and add its gels to `GEL_MAP` in `data/gels.js`.

> Always confirm against current manufacturer documentation before ordering.
