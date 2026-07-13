# Post-meeting plan — HFIR SpICE plotting (2026-07-13)

Notes and proposed path after the instrument-scientist + DAQ meeting.
Decks (local, not in git): `demo/Beamlines/Plotting needs.pptx` (HB-2A MIDAS), `demo/Beamlines/SPICE at DEMAND.pptx`.

## What the meeting actually asked for

The invite opened on “plotting tools,” but the hard questions were:

| Theme | Meeting signal | Implication |
|-------|----------------|-------------|
| **Source of truth** | Current-experiment local files; access control vs archiver (DEMAND note) | Define *who writes*, *who may read*, *what is “official”* |
| **Integrity** | Don’t corrupt / rewrite experiment data when tools re-save | EOL/`^M`, export vs overwrite (see [ADR-scan-formats](../demo/ADR-scan-formats.md)) |
| **Security** | Stated as essential; SpICE never did much on Windows | Treat as **access + audit**, not cryptography on day one |
| **Control-room graph** | Overlay, axes, browse, combine/rebin (TAS), order-parameter / peak compare (DEMAND, HB-2A) | **ioc-tasplot**-class tool |
| **Automated fitting** | Alignments want **fit → PVs**; peak viewing / diagnostics | Fit engine behind EPICS, not only a GUI click |
| **Post-experiment** | TAVI pitched as Graffiti replacement (crashed in demo; still early) | Separate track from live desk |

**Clarify roles (recommended wording for follow-ups):**

```text
Control room (during experiment)  →  ioc-tasplot + Phoebus  [+ optional fit PVs]
Offline / take-home analysis      →  TAVI  (Graffiti replacement; post-processing)
Deep interactive peak UI          →  PyMca desktop (button already shipped)
2D / histogram / PSD ROI          →  TBD (instrument-specific; not solved by 1D SpICE plot)
```

## Use cases heard (from decks + notes)

| Instrument / voice | Need |
|--------------------|------|
| **HB-2A MIDAS** | Alignment & polarization cal (not user data); order-parameter overlays (IS user data); monitor diagnostics |
| **TAS** | Multi-cal compare; browse; combine; rebinning |
| **WAND²** | Alignment scans; **output PVs**; previous alignments |
| **DEMAND** | ROI; crystal alignment; peak viewing; peak compare / order parameter; archiver not ideal for access-controlled diagnostics |
| **Cross-cutting** | More **2D → 1D cut** stories that still want a **1D fit** |

## TAVI (Triple-Axis Visualization Toolkit)

| Finding | Plan stance |
|---------|-------------|
| Started ~2022; demo **crashed** | Treat as **promising offline**, not beamline-critical path this year |
| Designed for **post-processing**, loader-ish independence | Good **Graffiti take-home** story for users who used to copy Graffiti + data |
| Less useful **during** experiment (HB-2A note matches) | Do **not** block control-room plot on TAVI readiness |
| Histogram / 2D not first-class | Aligns with meeting: local 1D SpICE/SPEC first; 2D later |

**Decision:** keep TAVI in the landscape as **offline companion**; ioc-tasplot remains the **local live graph**.

## Data security / integrity (demystify the fuzzy words)

SpICE on Windows never gave strong “security.” For this project, define minimums:

1. **Integrity** — Prefer **read-only** of archive/experiment files; write exports to `/tmp` or a user scratch area (already: PyMca temp SPEC, Buffer Write File). Don’t silently convert CRLF/`^M` on originals.
2. **Source** — One experiment folder on disk as current run set; Scan # / path PVs are the browse contract.
3. **Access** — Instrument account + CA ACL / separate diagnostic PVs vs user plot PVs (WAND² / DEMAND); archiver ≠ access-controlled science store.
4. **Defer** — Post-experiment “user format” packaging (Aczel thread) to a later meeting.

## Automated fitting: can EPICS call PyMca and put results on PVs?

**Short answer:** Yes in principle, but **prefer not embedding the PyMca Qt GUI in the IOC**. Use a **headless / scripted** fit that PyMca (or a thin lmfit/numpy path) can run from Python inside PyDevice, then `caput`-equivalent updates on result PVs.

### Options

| Option | How | Pros | Cons | Verdict |
|--------|-----|------|------|---------|
| **A. PyDevice + PyMca batch API** | IOC action PV → convert SPiCE→SPEC if needed → `PyMca5` fitting modules (no GUI) → write `FitAmp`, `FitCen`, `FitSigma`, `FitBg`, `FitStatus` | Reuses known fit models; scientists recognize PyMca | Packaging (`python3-pymca5`), NumPy conflicts we already hit; API surface less documented than GUI | **Prototype if PyMca batch fit is stable** |
| **B. PyDevice + lmfit / scipy** | Same PV handshake; simple Gaussian (+ linear bg) in `tasplot` | Small, testable, no Qt; easy CI | Not “PyMca”; different UI for deep tweaks | **Best MVP for alignment → PVs** |
| **C. Launch GUI and scrape** | `open_in_pymca` then hope | Familiar | **No** reliable PV return path | **Reject** |
| **D. Separate fit microservice** | Side process; CA or REST | Isolates Qt/versions | Ops overhead | Later if A/B insufficient |

### Recommended sequence

1. **MVP (control-room):** in-IOC **1D Gaussian + linear background** on current Graph (or Buffer) X/Y → PVs (`FitRun`, `FitCen_RBV`, …). Optional: write fitted curve to a buffer slot. Covers WAND²-style “alignment → output PVs” and TAS cal peak.
2. **Depth:** keep **Open in PyMca** for interactive multi-peak / weird shapes (already shipped).
3. **If meeting insists on PyMca brand:** spike Option A for one week; fall back to B if binding is painful.
4. **2D → 1D:** treat as **cut producer** (instrument ROI / projection) feeding the **same 1D fit PVs** — do not wait on full 2D plotter inside ioc-tasplot.

### Sketch (MVP fit PVs)

```text
TAS:Plot:FitRun          (bo)     → run fit on Graph or BufferSource
TAS:Plot:FitSource       (mbbo)   Graph | BufferA | Combine
TAS:Plot:FitCen_RBV      (ai)
TAS:Plot:FitAmp_RBV      (ai)
TAS:Plot:FitSigma_RBV    (ai)
TAS:Plot:FitBg_RBV       (ai)
TAS:Plot:FitChi2_RBV     (ai)
TAS:Plot:FitStatus_RBV   (lsi)    OK / error
TAS:Plot:FitYdata        (waveform) optional model curve for plot
```

## Proposed roadmap (post-meeting)

| Priority | Work | Owner-ish |
|----------|------|-----------|
| **P0** | Capture meeting use cases in this doc / STATUS; demos stay on 1D SpICE+SPEC | DAQ + ioc-tasplot |
| **P1** | **Fit MVP → PVs** (Gaussian+bg) + Show fit curve | ioc-tasplot |
| **P1** | Beamline deploy (IOC path, CA address, no duplicate servers) | DAQ |
| **P2** | Multi-overlay / previous-alignment recall (WAND², HB-2A order param) — extend buffers or N overlay slots | ioc-tasplot |
| **P2** | Spike: headless PyMca fit vs lmfit (document choice) | ioc-tasplot |
| **P3** | 2D histogram / PSD ROI contract with instruments (DEMAND, MIDAS) — separate ADR | Instruments + DAQ |
| **P3** | TAVI offline story + Graffiti sunset messaging | Kyle / neutrons |
| **Later** | Post-experiment package format for users | Facility |

## What ioc-tasplot already covers vs gaps

| Meeting need | Status in repo |
|--------------|----------------|
| Browse current experiment | Done |
| Dynamic axes | Done |
| Overlay another run | Done (1 + buffer A/B) |
| Combine / rebin-ish | Done MVP |
| Live growing file | Done |
| Basic fit in GUI | PyMca button only |
| Fit parameters → PVs | **Gap → P1** |
| 2D / histogram / ROI | **Gap** |
| Multi-cal history / many overlays | Partial (buffers) |
| Production deploy | Gap |
| TAVI integration | Not required in IOC |

## Demo talking points (next follow-up)

1. Roles: **desk = ioc-tasplot**, **home = TAVI**, **deep fit UI = PyMca**.  
2. Security ≠ encryption first — **don’t rewrite raw files**; control who sees what.  
3. Automated fit is a **PV contract**, not a screenshot from PyMca.  
4. 2D instruments still get value from **1D cuts + same fit PVs**.
