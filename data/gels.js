// Gel equivalence table. Every gel maps to one of the Allergan base tiers below.
// The competitor tier assignments are a clinical judgment. Until they have been
// confirmed, set GEL_MAP_CONFIRMED = false and the app shows them as "proposed".
window.GEL_TIERS = ["Responsive", "SoftTouch", "Cohesive"]; // softest -> firmest
window.GEL_MAP_CONFIRMED = false;

window.GEL_MAP = {
  "Allergan|Responsive": "Responsive",
  "Allergan|SoftTouch": "SoftTouch",
  "Allergan|Cohesive": "Cohesive",

  "Mentor|MemoryGel": "Responsive",       // proposed
  "Mentor|MemoryGel Xtra": "SoftTouch",   // proposed
  "Mentor|MemoryGel Boost": "Cohesive",   // proposed
  "Mentor|MemoryShape": "Cohesive",       // proposed (form-stable shaped gel)
  "Motiva|ProgressiveGel": "Responsive",  // proposed
  "Sientra|HSC": "SoftTouch",             // proposed
  "Sientra|HSC+": "Cohesive",             // proposed
};
