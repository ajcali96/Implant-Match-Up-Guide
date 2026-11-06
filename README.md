# Implant Match-Up Guide

Match breast implants across manufacturers by dimensions and gel type, with
**Allergan Natrelle INSPIRA** as the base that every other implant is compared against.

Open `index.html` in any browser. It has no server or internet dependency, so it works offline.

## How matching works

1. Choose an Allergan implant by catalog number (e.g. `SRX-400`) or by gel, profile and volume.
2. Candidates are filtered by:
   - **gel tier**: each manufacturer's gel is mapped to Responsive, SoftTouch or Cohesive in `data/gels.js`
   - **maximum base-width difference**
   - **manufacturer**
3. Results are ranked by `3 × |Δwidth| + 2 × |Δprojection| + |Δvolume| / 100`, so base width counts most, then projection, then volume.

## Data

| File | Purpose |
| --- | --- |
| `tools/allergan_source.py` | Hand transcription of the Allergan order form tables (MBD125570-v4 01/22) |
| `tools/build_data.py` | Generates `data/implants.csv` and `data/implants.js` |
| `data/gels.js` | Gel equivalence table (clinical judgment, needs confirmation) |

Currently loaded: Allergan Natrelle INSPIRA smooth round gel, with Low, Low-Plus, Moderate, Full and
Extra-Full profiles in Cohesive, SoftTouch and Responsive (300 implants).

### Adding a manufacturer

Add that manufacturer's rows to the build (same columns as `data/implants.csv`), run
`python3 tools/build_data.py`, and add its gels to `GEL_MAP` in `data/gels.js`.

> Always confirm against current manufacturer documentation before ordering.
