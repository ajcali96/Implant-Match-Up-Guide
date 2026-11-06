# Implant Match-Up Guide

Match breast implants across manufacturers by dimensions and gel type, with
**Allergan Natrelle INSPIRA** as the base that every other implant is compared against.

Open `index.html` in any browser. It has no server or internet dependency, so it works offline.

## How matching works

1. Choose an Allergan implant by catalog number (e.g. `SRX-400`) or by gel, profile and volume.
2. Candidates are filtered by:
   - **gel tier**: each manufacturer's gel is mapped to Responsive, SoftTouch or Cohesive in `data/gels.js`
   - **surface**: smooth or textured
   - **maximum base-width difference**
   - **manufacturer**
3. Results are ranked by `3 × |Δwidth| + 2 × |Δprojection| + |Δvolume| / 100`, so base width counts most, then projection, then volume.

## Data

| Manufacturer | Lines | Gels | Implants | Source |
| --- | --- | --- | --- | --- |
| Allergan (base) | Natrelle INSPIRA smooth round | Responsive, SoftTouch, Cohesive | 300 | Product Order Form MBD125570-v4 01/22 (hand transcribed) |
| Mentor | MemoryGel smooth round | MemoryGel | 92 | Variant specification spreadsheet, 2026-11-04 |
| Motiva | SmoothSilk Round, SmoothSilk Ergonomix | ProgressiveGel | 81 | Order Form US-ERGO1-0001 R1 |
| Sientra | Round, smooth and textured | HSC, HSC+ | 304 | Quick Reference Guide MDC-0270 R11 |

| File | Purpose |
| --- | --- |
| `tools/allergan_source.py` | Hand transcription of the Allergan order form tables |
| `tools/extract_sources.py` | Parses the Mentor, Motiva and Sientra files into `data/source/*.csv` |
| `tools/build_data.py` | Merges everything into `data/implants.csv` and `data/implants.js` |
| `data/gels.js` | Gel equivalence table |

### Gel equivalence (proposed, awaiting clinical confirmation)

| Allergan tier | Equivalent gels |
| --- | --- |
| Responsive | Mentor MemoryGel, Motiva ProgressiveGel |
| SoftTouch | Sientra HSC |
| Cohesive | Sientra HSC+ |

Once confirmed, set `GEL_MAP_CONFIRMED = true` in `data/gels.js` to hide the "proposed" notice.

### Adding a manufacturer

Add a parser to `tools/extract_sources.py` (or write `data/source/<name>.csv` with the same columns),
run `python3 tools/build_data.py`, and add its gels to `GEL_MAP` in `data/gels.js`.

> Always confirm against current manufacturer documentation before ordering.
