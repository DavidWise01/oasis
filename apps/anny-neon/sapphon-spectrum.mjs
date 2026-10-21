// Anny's symbolic seven-band Sapphon wavelength delimiter registry.
// These nm boundaries are illustrative teaching bins, not standardized color cutoffs.
// One opposing polarity at EACH end of EVERY band: − low nm, + high nm.
// Greek partner epithets denote symbolic roles, not scientific properties.
export const SAPPHON_SPECTRUM = Object.freeze([
  {
    "color": "Red",
    "accent": "#ff6972",
    "low": 620,
    "high": 750,
    "slots": [
      1,
      2
    ],
    "minus": {
      "word": "Πῦρ",
      "latin": "Pyr",
      "meaning": "fire"
    },
    "plus": {
      "word": "Φλόγα",
      "latin": "Phloga",
      "meaning": "flame"
    }
  },
  {
    "color": "Orange",
    "accent": "#ffaa63",
    "low": 590,
    "high": 620,
    "slots": [
      3,
      4,
      5,
      6
    ],
    "minus": {
      "word": "Ἠώς",
      "latin": "Eos",
      "meaning": "dawn"
    },
    "plus": {
      "word": "Ἀνατολή",
      "latin": "Anatole",
      "meaning": "rising"
    }
  },
  {
    "color": "Yellow",
    "accent": "#f5dc73",
    "low": 570,
    "high": 590,
    "slots": [
      7,
      8
    ],
    "minus": {
      "word": "Ἥλιος",
      "latin": "Helios",
      "meaning": "sun"
    },
    "plus": {
      "word": "Χρυσός",
      "latin": "Chrysos",
      "meaning": "gold"
    }
  },
  {
    "color": "Green",
    "accent": "#86dbab",
    "low": 495,
    "high": 570,
    "slots": [
      9,
      10
    ],
    "minus": {
      "word": "Φύσις",
      "latin": "Physis",
      "meaning": "nature"
    },
    "plus": {
      "word": "Χλόη",
      "latin": "Chloe",
      "meaning": "green shoot"
    }
  },
  {
    "color": "Blue",
    "accent": "#80b9ff",
    "low": 450,
    "high": 495,
    "slots": [
      11,
      12,
      13,
      14,
      15
    ],
    "minus": {
      "word": "Θάλασσα",
      "latin": "Thalassa",
      "meaning": "sea"
    },
    "plus": {
      "word": "Οὐρανός",
      "latin": "Ouranos",
      "meaning": "sky"
    }
  },
  {
    "color": "Indigo",
    "accent": "#b6a1ff",
    "low": 420,
    "high": 450,
    "slots": [
      16,
      17
    ],
    "minus": {
      "word": "Βάθος",
      "latin": "Bathos",
      "meaning": "depth"
    },
    "plus": {
      "word": "Νύξ",
      "latin": "Nyx",
      "meaning": "night"
    }
  },
  {
    "color": "Violet",
    "accent": "#d6a3ff",
    "low": 380,
    "high": 420,
    "slots": [
      18
    ],
    "minus": {
      "word": "Ἴρις",
      "latin": "Iris",
      "meaning": "rainbow"
    },
    "plus": {
      "word": "Αἰθήρ",
      "latin": "Aither",
      "meaning": "upper air"
    }
  }
]);
export const SAPPHON_SPECTRUM_GLYPH = "{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}";
export function validateSapphonSpectrum(bands = SAPPHON_SPECTRUM) {
 const slots=bands.flatMap(b=>b.slots);
 const labels=bands.flatMap(b=>[b.minus.word,b.plus.word]);
 return bands.length===7
  && JSON.stringify(slots)===JSON.stringify(Array.from({length:18},(_,i)=>i+1))
  && bands.every((b,i)=>b.low<b.high && (i===0 || bands[i-1].low===b.high))
  && bands[0].high===750 && bands[6].low===380
  && new Set(labels).size===14;
}

// White is a broadband mixture, not one monochromatic spectral interval.
// Retained as the existing Sapphon companion; it does not consume a cubit slot.
export const SAPPHON_BROADBAND = Object.freeze({
 color: "White", accent: "#e9f4ff", rangeLabel: "Broadband · no single wavelength",
 minus: {word:"Λευκός",latin:"Leukos",meaning:"white"},
 plus: {word:"Σελήνη",latin:"Selene",meaning:"moon"}
});
