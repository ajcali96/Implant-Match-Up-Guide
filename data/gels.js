// Gel equivalence table. Every gel maps to one of the Allergan base tiers below.
// Competitor tiers were confirmed by the user on 2026-11-07. If a gel is added or
// a tier is changed, set GEL_MAP_CONFIRMED = false so the app flags it as proposed.
window.GEL_TIERS = ["Responsive", "SoftTouch", "Cohesive"]; // softest -> firmest
window.GEL_MAP_CONFIRMED = true;

window.GEL_MAP = {
  "Allergan|Responsive": "Responsive",
  "Allergan|SoftTouch": "SoftTouch",
  "Allergan|Cohesive": "Cohesive",

  "Mentor|MemoryGel": "Responsive",
  "Mentor|MemoryGel Xtra": "SoftTouch",
  "Mentor|MemoryGel Boost": "Cohesive",
  "Mentor|MemoryShape": "Cohesive",
  "Motiva|ProgressiveGel": "Responsive",
  "Sientra|HSC": "SoftTouch",
  "Sientra|HSC+": "Cohesive",
};
