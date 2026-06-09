# HB2D EPICS Upgrade — Data Handling & Experiment Control

Reference notes from the HB2D instrument requirements review. Shared for TAX-team input because much of this work may apply across TAX instruments (not only HB2D).

**Meeting:** HB2D EPICS Upgrade — Data Handling & Experiment Control Discussion  
**Source:** HB2D requirements document (Visualization & Data Handling; Scan & Experiment Control sections) plus IDAC SME questions.

**Relevance to ioc-tasplot:** The **Graph Data** items align with the SpICE *Data → Graph data* tab and this repository’s Browse + Graph OPI (`TASPlot.bob`). Real-time plotting, scan selection, and axis choice are in scope for future phases; MCU-based scan control and motor orchestration are out of scope here.

**Scope mapping:** [hb2d-ioc-tasplot-scope-mapping.md](hb2d-ioc-tasplot-scope-mapping.md) — requirement-by-requirement status for the HB2D / TAX discussion.

---

## Meeting context

The HB2D EPICS upgrade started several months ago. The instrument team has shared requirements; SMEs have been reviewing them. At the stage of reviewing **Visualization & Data Handling** and **Scan & Experiment Control**, Klemen noted that similar development may be needed across all **TAX** instruments, so TAX-team feedback is requested.

---

## Visualization and Data Handling

- Implement **MCU-based scan control** with detector capture at each step, accounting for low beam-monitor efficiency (~0.1%). MCU must be configurable (e.g. 1 MCU = 1000 or 2000 neutrons).
- Integrate **NI-based** data acquisition hardware.
- Provide a **macro/stack interface** for editing scan commands and running pre-saved scan files; **Python-compatible**.
- Build **visualization tools** to graph results, detect peaks or waveforms, and reuse peak positions from prior scans in different parameter spaces. Fitting should be automated from sensible initial guesses.

### Graph Data

- Similar functionality to **SpICE** (*Data → Graph data* tab).
- Plot **real-time** and **historical** data.
- Choose **scan number** and **X/Y axes**.
- Integration of **tilting-angle scan** for Larmor diffraction.
- **Two-flipper** measurements calculator.
- **Quick calculators** from the ILL website.

---

## Scan and Experiment Control

Per-step scan workflow:

1. Move motors to target positions for each scan step.
2. Confirm position before data acquisition.
3. Trigger detector acquisition after positioning.

Additional capabilities:

- Support **step scans based on MCU** (Monitor Count Unit), not time. MCU derives from beam-monitor counts (~0.1% efficiency) as the primary normalization method.
- **Modify scan parameters dynamically** during a run.
- **Plot arbitrary parameters** while scanning is in progress.
- **Estimate** total scan time.
- **Error detection** — motor limit violations, syntax/grammar mistakes in scan definitions, etc.
- **Sweep function** — plot live data vs. motor rotation angle continuously; faster, loosely defined motor motion for sample alignment.
- Support **polarization systems** and integrate **CAEN** power supplies (including HB1 setup). Supply settings should adapt automatically to wavelength for proper flipping: `B(horizontal) = value / wavelength`.

---

## IDAC SME questions (discovery)

### Data handling

- What do you currently do with data after acquisition?
- In what format should data be stored or exported?
- How is data analyzed today? Are additional software tools needed?
- How far back must historical data remain accessible, and how often is older data used?
- What are storage requirements — **GPFS** vs. local?
- If stored locally, how much historical data must be retained?

### Scan

- What is the smallest **step resolution** required during a scan?
- What is the typical **duration or length** of each scan step?
