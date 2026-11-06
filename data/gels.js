// Gel equivalence table. Every gel maps to one of the Allergan base tiers below.
// Add competitor gels here as their catalogs are loaded, e.g.
//   "Mentor|MemoryGel": "Responsive",
// The tier assignment is a clinical judgment and should be confirmed by the user.
window.GEL_TIERS = ["Responsive", "SoftTouch", "Cohesive"]; // softest -> firmest

window.GEL_MAP = {
  "Allergan|Responsive": "Responsive",
  "Allergan|SoftTouch": "SoftTouch",
  "Allergan|Cohesive": "Cohesive",
};
