# ioc-tasplot — session checkpoint (2026-07-11)

Handoff for resuming work after a break.

## Repository

- **Remote:** https://github.com/kgofron/ioc-tasplot
- **Branch:** `main` (sync with `origin/main` before long breaks)
- **Tests:** `44 passed` (`python3 -m pytest -q`)
- **Latest feature work:** Buffer polish (A/B overplot + table preview) + Data Buffers MVP

## What works (validated)

- IOC boots with PyDevice; prefix **`TAS:Plot:`**
- HB3 SPiCE `.dat` load via `tasplot` (exp382 scans 1–4 tested)
- Phoebus OPI: `plotApp/op/bob/TASPlot.bob`
- **Browse** (`SelectedFile` / FileSelector) → auto-load plot
- **Scan #** spinner → rebuilds `*_scanNNNN.dat`, auto-reload
- **Reload** button → re-read current file; **preserves X/Y** columns
- **Live** checkbox (`AutoReload`) → poll mtime/size every 1 s, re-acquire when file grows
- **Normalization** — `NormMode` (None / Column / Fixed), `NormCol`, `NormValue`
- **Log X / Log Y** — Phoebus local checkboxes → xyplot log scales
- **Errors** (`ShowErrors`) — Poisson √N on selected Y (`YdataErr`); works for **detector** and **monitor** (both count-like). Band looks thin at high *N* on a full-scale axis; zoom Y (or Log Y) to see it. Toggle Off → empty err waveform.
- **Overlay** — `OverlayEnable` + `OverlayFileNumber` second trace (orange)
- **Combine Data** — `+ list` / `− list` scan #s, Norm to + weight col, Bin tol → green **combine** trace (`CombineRun` / `CombineEnable`). Not full SpICE buffer UI yet.
- **Data Buffers** — 8 scratch slots; Save from Graph or Combine; Show purple trace; Write ASCII file
- **PyMca** button — peak fit / overlay (**shipped:** CERTIF SPEC pass-through; **SPiCE → temp SPEC** with named `#L` via `tasplot.export_spec`). Alternative later: **native SPiCE** in upstream PyMca — see [landscape § SPiCE in PyMca](reference/tas-plotting-tools-landscape.md#spice-in-pymca--two-viable-paths).
- **DataFileContents** — full-file text via I/O Intr (`DataFileText`, 64 KB)
- Plot title from `Command_RBV`; Y label from `PlotAxisLabel_RBV` (norm-aware)

**Dev data path:**

`/home/kg1/Documents/Detector/HB3/HB3_data/User/exp382/Datafiles/HB3_exp0382_scan0001.dat` … `0004.dat`

**Docs:** [tas-plotting-tools-landscape.md](reference/tas-plotting-tools-landscape.md), [hb2d-ioc-tasplot-scope-mapping.md](reference/hb2d-ioc-tasplot-scope-mapping.md)

## Build

```bash
cd /home/kg1/Documents/src/github/ioc-tasplot
make -sj
# After Db changes:
make -C plotApp/Db install
```

## IOC runtime

```bash
cd iocBoot/iocTasplot
./st.cmd
```

**Smoke test:**

```bash
caget TAS:Plot:NRows_RBV
caput TAS:Plot:AutoReload 1          # Live reload while file grows
caput TAS:Plot:OverlayFileNumber 2
caput TAS:Plot:OverlayEnable 1       # orange overlay trace
caput TAS:Plot:ShowErrors 1          # Poisson √N (0 = hide bars)
caput TAS:Plot:NormMode 1
caput -S TAS:Plot:NormCol monitor
```

**Phoebus:** `plotApp/op/bob/TASPlot.bob`, macro `P` = `TAS:Plot:`.

## PV layout (highlights)

| PV | Role |
|----|------|
| `SelectedFile` / `FileNumber` / `FullFileName_RBV` | Browse + Scan # |
| `Acquire` | Manual Reload (preserves axes) |
| `AutoReload` + `FilePoll` | Live reload on file growth |
| `XCol` / `YCol` / `Norm*` | Axes + normalization |
| `ShowErrors` | Poisson √N error bars on/off (`YdataErr`) |
| `OverlayEnable` / `OverlayFileNumber` | Second scan overlay |
| `CombineAddList` / `CombineSubList` / `CombineRun` | Combine +/− scan lists |
| `CombineNorm*` / `CombineBinTol` / `CombineEnable` | Combine renorm, binning, show result |
| `CombineXdata` / `CombineYdata` / `CombineYdataErr` | Combine result waveforms |
| `BufferSlot` / `BufferSave` / `BufferEnable` | Scratch buffers Slot A (8 slots) |
| `BufferSlotB` / `BufferEnableB` | Second buffer overplot (magenta) |
| `BufferSaveSource` / `BufferWriteFile` | Save from Graph or Combine; ASCII export |
| `BufferList_RBV` / `BufferTableText_RBV` | Slot occupancy + read-only table preview |
| `BufferXdata` / `BufferBXdata` … | Buffer A / B waveforms |
| `OverlayXdata` / `OverlayYdata` / `OverlayYdataErr` | Overlay waveforms |
| `Xdata` / `Ydata` / `YdataErr` | Primary plot |
| `DataFileText` | File contents panel |

## Done

- [x] tasplot parsers + PyDevice IOC + Phoebus Browse/Graph
- [x] Normalization + title/axis polish
- [x] Phase 4 — Log X / Log Y
- [x] Live reload (`AutoReload`)
- [x] Phase 5 — overlay second scan (basic Overplot)
- [x] Phase 6 — deepen PyMca launcher (CLI + API fallback)
- [x] Poisson √N error bars + `ShowErrors` toggle (Option A)
- [x] Combine Data MVP (+/− lists, bin tol, renorm, green trace)
- [x] Data Buffers MVP (8 slots, save Graph/Combine, purple trace, ASCII write)
- [x] Buffer polish — Slot B overplot, slot list, read-only table preview

## Next (when resuming)

1. **Beamline deploy** — `/epics/iocs/ioc-tasplot`, production paths, autosave
2. **Facility** — PVXS/QSRV 2
3. Optional: editable buffer table / Del-row Combine UI; in-OPI Gaussian fit if PyMca isn’t enough

**Monday prep (short):** demo paths (`demo/` + exp382); SPEC `#S` on YongCai `demo/yongcai_20240530.spec`; Phoebus CA address list if duplicate-server magenta borders persist. Briefing: [`demo/ADR-scan-formats.md`](../demo/ADR-scan-formats.md) (SPEC vs SPiCE + CRLF/`^M`).

## Operational notes

- Use **`caget -S ….$`** for long strings
- Rebuild Db after template changes, then restart IOC
- Log scales are **local** (`loc://`) — per OPI instance, not EPICS PVs
- Overlay uses same X/Y/norm as primary; scan # from same folder naming
- `YdataErr` = √|Y| for the **current Y column** after norm (not detector-only)
- Old Graffiti C IOC: `Detector/HB3/applications/hb3-Graffiti`
