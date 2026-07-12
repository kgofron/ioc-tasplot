# ioc-tasplot — session checkpoint (2026-07-11)

Handoff for resuming work after a break.

## Repository

- **Remote:** https://github.com/kgofron/ioc-tasplot
- **Branch:** `main` (sync with `origin/main` before long breaks)
- **Tests:** `26 passed` (`python3 -m pytest -q`)
- **Latest feature work:** Phase 4 log scales, live reload, Phase 5 overlay, Phase 6 PyMca deepen

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
- **Overlay** — `OverlayEnable` + `OverlayFileNumber` second trace (orange)
- **PyMca** button — opens current file for peak fit / rich overlay
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

## Next (when resuming)

1. **Combine Data** — multi-scan add/subtract (full SpICE Combine tab)
2. **Data Buffers** — scratch buffers tab
3. **Beamline deploy** — `/epics/iocs/ioc-tasplot`, production paths, autosave
4. **Facility** — PVXS/QSRV 2
5. Optional: in-OPI Gaussian fit if scientists reject PyMca-only peak fit

## Operational notes

- Use **`caget -S ….$`** for long strings
- Rebuild Db after template changes, then restart IOC
- Log scales are **local** (`loc://`) — per OPI instance, not EPICS PVs
- Overlay uses same X/Y/norm as primary; scan # from same folder naming
- Old Graffiti C IOC: `Detector/HB3/applications/hb3-Graffiti`
