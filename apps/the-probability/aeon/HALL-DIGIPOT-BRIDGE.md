# AEON Thought Loop · Hall sensors + digital potentiometers

**Status:** browser software engine implemented; optional physical bridge protocol implemented, but no device-specific firmware is included. Hardware must be separately wired and programmed for the sensor/digipot part numbers you own.

## Meaning of Hall and pots in the arcade

Eight **virtual Hall channels** (U, D, L, R, B, A, SELECT, START) are response estimates, not measurements of a real magnetic field. They are derived from before/after observations of **physically delivered NES button events**.

Eight **software digital potentiometer wipers**, each 32–224 on a 0–255 scale, adjust button candidate preference and bounded hold length (1–6 emulated frames). A digital NES button still has only on/off states; software wiper values are **not** analog button voltage.

A *real* Hall-effect sensor requires actual magnetic hardware. A *real* digital potentiometer requires a chip matched to voltage limits, resistance, and control bus. Never drive a NES console/controller port directly from this page.

## Regressive loop

    history[-1] → before[0] → delivered input → after[+1]
       |                              |
       +-- check prior transition <--+
                     |
             {-1, 0, +1}
                     |
       virtual / real Hall reading
                     |
       bounded 8-bit wiper update
                     |
          next actual button hold

The regressive comparison detects genuine A → B → A reversals; A → A is not a reversal. One stable positive screen change reduces motor effort, a negative (no observed change) gradually increases it, and a RAM-only ambiguous observation changes the wiper only slightly. Repeated transitions are damped. This loop is a **heuristic controller**, not proof that the NES player is moving successfully or understanding the game.

## Web Serial bridge (optional)

Click **CONNECT HALL SERIAL** in Chrome/Edge on the HTTPS GitHub Pages site. It prompts you to choose a connected authorized USB serial device at 115200 baud.

The device should send one UTF-8 newline-delimited JSON object containing eight normalized Hall values in **this order**:

    {"hall":[0,42,81,127,160,200,220,255]}

The browser sends updated wipers to the device at most once per 150 ms:

    {"type":"wipers","values":[128,128,128,128,128,128,128,128]}

Your firmware must translate these logical wipers into its specific SPI/I2C chip commands, selecting the correct CS/address, obeying data-sheet voltage and end-stop limits. No such translation is implicit in the page. Hardware connection is **opt-in**, and the UI otherwise shows **VIRTUAL HALL PROXY**.

## Firmware integration checklist

- Define sensor part numbers, safe supply voltage, ground, calibration and range normalization.
- Define digipot part numbers and whether each channel is an independent chip or a multi-channel device.
- Implement the eight-value serial packet and checksum/framing if needed for noisy links.
- Verify minimum/maximum wiper limits with a separate instrument before enabling outputs.
- Verify physical measurements match the page readouts. A passing browser test does not certify a physical circuit.

## Persistent state / export

Each ROM + Markdown profile stores its own bounded Hall/digipot memory in this browser's local storage. The **EXPORT** button emits the current channels and receipt history. Clearing browser site storage clears it. Electron filesystem persistence is separate.

## AEON field map

    WEAK³ → MED² → STRONG¹ | STRONG¹ → MED² → WEAK³
                       3 : 2 : 1 : 1 : 2 : 3

This is a symbolic software field modulation, not a physical force or actual 4D tesseract.

## Regression tests performed

- 11 isolated engine checks: false press rejection, ternary classification, bounded wipers, real A→B→A reversal, serial parsing and snapshot restoration.
- Integration simulation through the browser page controller: eight delivered presses/releases and eight witness receipts in order; all eight Hall channels updated; local persistence keys created; no JavaScript exceptions.
- Inline scripts and the standalone module parse successfully.
- Native Electron execution and physical Hall/digipot hardware are not tested.
