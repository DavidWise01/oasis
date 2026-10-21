import { SAPPHON_SPECTRUM, SAPPHON_BROADBAND, SAPPHON_SPECTRUM_GLYPH, validateSapphonSpectrum } from "./sapphon-spectrum.mjs";

const expected = "{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}";
if (!validateSapphonSpectrum() || expected !== SAPPHON_SPECTRUM_GLYPH) {
  throw new Error("SAPPHON_SPECTRUM_INVARIANT_FAILED");
}

const spectralHost = document.getElementById("spectrum-pairs");
const whiteHost = document.getElementById("white-sapphon-pair");
const direction = document.getElementById("spectrum-direction");
if (!spectralHost || !whiteHost || !direction) throw new Error("SAPPHON_RENDER_MOUNT_MISSING");

function make(tag, className, content) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (content !== undefined) el.textContent = String(content);
  return el;
}

function card(band, broadband = false) {
  const panel = make("article", "pair");
  panel.style.setProperty("--tone", band.accent);
  panel.dataset.color = band.color.toLowerCase();
  panel.dataset.polarity = "-+";
  panel.dataset.wavelength = broadband ? "broadband" : band.low + "-" + band.high;
  panel.append(
    make("h3", "", band.color === "Violet" ? "ANNY · PURPLE / VIOLET" : band.color.toUpperCase() + " · SAPPHON"),
    make("div", "range", broadband ? band.rangeLabel : band.low + "–" + band.high + " nm · approx")
  );
  const atoms = make("div", "atoms");
  atoms.setAttribute("role", "img");
  atoms.setAttribute("aria-label", band.color + ": minus and plus Sapphon partners joined by a diatomic bond");
  for (const sign of ["−", "+"]) {
    if (sign === "+") atoms.append(make("span", "bond"));
    const atom = make("span", "atom");
    atom.append(make("strong", "charge", sign));
    atoms.append(atom);
  }
  panel.append(atoms);
  const members = make("div", "members");
  for (const [sign, name, endpoint] of [
    ["−", band.minus, band.low],
    ["+", band.plus, band.high]
  ]) {
    const member = make("div", "member");
    member.append(
      make("span", "greek", sign + " " + name.word),
      make("span", "latin", name.latin),
      make("span", "meaning", name.meaning),
      make("span", "nm", broadband ? "multi-λ" : endpoint + " nm")
    );
    members.append(member);
  }
  panel.append(members);
  panel.append(make("p", "slot-annotation",
    broadband ? "White companion · no monochromatic slot" : "Analytical cubit slots · " + band.slots.join(", ")));
  return panel;
}

let longToShort = true;
function render() {
  spectralHost.replaceChildren();
  const order = longToShort ? SAPPHON_SPECTRUM : [...SAPPHON_SPECTRUM].reverse();
  for (const band of order) spectralHost.append(card(band));
  direction.textContent = longToShort ? "⇄ Show short → long wavelength" : "⇄ Show long → short wavelength";
}
direction.addEventListener("click", () => { longToShort = !longToShort; render(); });
whiteHost.replaceChildren(card(SAPPHON_BROADBAND, true));
render();
