(() => {
  const ALL = window.IMPLANTS;
  const BASE_MFR = "Allergan";
  const PROFILE_ORDER = ["Low", "Low-Plus", "Moderate", "Full", "Extra-Full"];
  const base = ALL.filter(i => i.manufacturer === BASE_MFR);
  const $ = id => document.getElementById(id);

  const tierOf = i => window.GEL_MAP[`${i.manufacturer}|${i.gel}`] || null;
  const uniq = a => [...new Set(a)];
  const opts = (el, values, keep) => {
    el.innerHTML = values.map(v => `<option>${v}</option>`).join("");
    if (keep && values.includes(keep)) el.value = keep;
  };

  // Ranking: width matters most, then projection, then volume.
  const score = (a, b) =>
    3 * Math.abs(a.diameter_cm - b.diameter_cm) +
    2 * Math.abs(a.projection_cm - b.projection_cm) +
    Math.abs(a.volume_cc - b.volume_cc) / 100;

  // Colour a difference: green = close, amber = moderate, red = large.
  const delta = (d, unit, near, far) => {
    if (Math.abs(d) < 1e-9) return `<small class="d0">same</small>`;
    const cls = Math.abs(d) <= near ? "d0" : Math.abs(d) <= far ? "d1" : "d2";
    const txt = unit === "cc" ? Math.round(d) : d.toFixed(2).replace(/0$/, "");
    return `<small class="${cls}">${d > 0 ? "+" : "−"}${String(txt).replace("-", "")} ${unit}</small>`;
  };

  // Picker
  $("catalogs").innerHTML = base.map(i => `<option value="${i.catalog}">`).join("");
  opts($("gel"), window.GEL_TIERS.filter(g => base.some(i => i.gel === g)));
  const mfrs = uniq(ALL.map(i => i.manufacturer));
  const others = mfrs.filter(m => m !== BASE_MFR);
  $("fMfr").innerHTML =
    (others.length ? `<option value="others">All other manufacturers</option>` : "") +
    `<option value="all">All, including Allergan</option>` +
    mfrs.map(m => `<option value="${m}">${m} only</option>`).join("");

  function refreshProfiles() {
    const p = PROFILE_ORDER.filter(p => base.some(i => i.gel === $("gel").value && i.profile === p));
    opts($("profile"), p, $("profile").value);
    refreshVolumes();
  }
  function refreshVolumes() {
    const v = base.filter(i => i.gel === $("gel").value && i.profile === $("profile").value)
      .map(i => i.volume_cc).sort((a, b) => a - b);
    opts($("volume"), v.map(String), $("volume").value);
  }
  function selectedFromDropdowns() {
    return base.find(i => i.gel === $("gel").value && i.profile === $("profile").value &&
      String(i.volume_cc) === $("volume").value);
  }
  function setDropdowns(i) {
    $("gel").value = i.gel; refreshProfiles();
    $("profile").value = i.profile; refreshVolumes();
    $("volume").value = String(i.volume_cc);
  }

  let current = null;

  function show(i) {
    current = i;
    if (!i) { $("base").hidden = $("matchSec").hidden = true; return; }
    $("base").hidden = $("matchSec").hidden = false;
    if ($("q").value.trim().toUpperCase() !== i.catalog) $("q").value = i.catalog;
    $("base").innerHTML = `
      <div class="basehead">
        <span class="cat">${i.catalog}</span>
        <span><span class="tag">${i.manufacturer} ${i.line}</span>
        <span class="tag">${i.surface} ${i.shape}</span></span>
      </div>
      <div class="specs">
        <div class="spec"><span>Gel</span><b>${i.gel}</b></div>
        <div class="spec"><span>Profile</span><b>${i.profile}</b></div>
        <div class="spec"><span>Width</span><b>${i.diameter_cm.toFixed(2)} cm</b></div>
        <div class="spec"><span>Projection · Volume</span><b>${i.projection_cm.toFixed(1)} cm · ${i.volume_cc} cc</b></div>
      </div>`;
    renderGelNote();
    renderMatches();
  }

  function renderMatches() {
    const i = current; if (!i) return;
    const mf = $("fMfr").value, sameGel = $("fGel").value === "same";
    const sameSurf = $("fSurf").value === "same";
    const maxW = parseFloat($("fWidth").value);
    const n = parseInt($("fCount").value, 10);
    const list = ALL.filter(c => c !== i)
      .filter(c => mf === "all" ? true : mf === "others" ? c.manufacturer !== BASE_MFR : c.manufacturer === mf)
      .filter(c => !sameGel || tierOf(c) === tierOf(i))
      .filter(c => !sameSurf || c.surface === i.surface)
      .filter(c => isNaN(maxW) || Math.abs(c.diameter_cm - i.diameter_cm) <= maxW + 1e-9)
      .map(c => ({ c, s: score(i, c) }))
      .sort((a, b) => a.s - b.s)
      .slice(0, n);

    $("results").querySelector("tbody").innerHTML = list.map(({ c }) => `
      <tr class="${c.manufacturer === BASE_MFR ? "pickable" : ""}" data-cat="${c.catalog}">
        <td><b>${c.catalog}</b></td>
        <td>${c.manufacturer}<small>${c.line}</small></td>
        <td>${c.gel}${tierOf(c) && tierOf(c) !== c.gel ? `<small>≈ ${tierOf(c)}</small>` : ""}</td>
        <td>${c.profile}<small class="muted">${c.surface}</small></td>
        <td>${c.diameter_cm.toFixed(2)}${delta(c.diameter_cm - i.diameter_cm, "cm", 0.25, 0.5)}</td>
        <td>${c.projection_cm.toFixed(1)}${delta(c.projection_cm - i.projection_cm, "cm", 0.3, 0.7)}</td>
        <td>${c.volume_cc}${delta(c.volume_cc - i.volume_cc, "cc", 25, 60)}</td>
      </tr>`).join("");

    const empty = $("empty");
    empty.hidden = list.length > 0;
    if (!list.length) {
      empty.textContent = others.length || mf !== "others"
        ? "No implants match these filters. Try a larger width difference or any gel."
        : "No other manufacturers are loaded yet. Choose “All, including Allergan” to compare across Allergan profiles.";
    }
  }

  $("gel").addEventListener("change", () => { refreshProfiles(); show(selectedFromDropdowns()); });
  $("profile").addEventListener("change", () => { refreshVolumes(); show(selectedFromDropdowns()); });
  $("volume").addEventListener("change", () => show(selectedFromDropdowns()));
  $("q").addEventListener("input", () => {
    const hit = base.find(i => i.catalog === $("q").value.trim().toUpperCase());
    if (hit) { setDropdowns(hit); show(hit); }
  });
  ["fMfr", "fGel", "fSurf", "fWidth", "fCount"].forEach(id => $(id).addEventListener("input", renderMatches));
  $("results").addEventListener("click", e => {
    const tr = e.target.closest("tr.pickable"); if (!tr) return;
    const hit = base.find(i => i.catalog === tr.dataset.cat);
    if (hit) { setDropdowns(hit); show(hit); window.scrollTo({ top: 0, behavior: "smooth" }); }
  });

  // Gel equivalence notice
  function renderGelNote() {
    const note = $("gelNote"), t = current && tierOf(current);
    const peers = Object.entries(window.GEL_MAP)
      .filter(([k, v]) => v === t && !k.startsWith(BASE_MFR + "|"))
      .map(([k]) => k.replace("|", " "));
    note.hidden = window.GEL_MAP_CONFIRMED || !peers.length;
    note.innerHTML = `<b>Proposed gel match, not yet confirmed:</b> ${t} ≈ ${peers.join(", ")}.`;
  }

  // Default selection
  $("gel").value = "Responsive"; refreshProfiles();
  $("profile").value = "Moderate"; refreshVolumes();
  show(selectedFromDropdowns());
})();
