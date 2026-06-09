# ioc-tasplot — session checkpoint (2026-06-04)

Handoff for resuming work after a break.

## Repository

- **Remote:** https://github.com/kgofron/ioc-tasplot
- **Branch:** `main` (clean working tree; synced with `origin/main` at last check)
- **Tests:** `17 passed` (`python3 -m pytest -q`)
- **Latest commits (newest first):**
  - `d19aa89` feat(plot): auto-load on file browse and rename Acquire to Reload
  - `ff39509` feat(plot): SPiCE Scan # spinner and auto-reload on FileNumber
  - `b6bb09d` refactor(ioc): remove legacy FilePath and FileName PVs
  - `14b728d` feat(ioc): add SelectedFile PV and set_selected_file for Phoebus browse
  - `8530725` feat(op): simplify TASPlot browse with SelectedFile and FileSelector

## What works (validated)

- IOC boots with PyDevice; prefix **`TAS:Plot:`**
- HB3 SPiCE `.dat` load via `tasplot` (exp382 scans 1–4 tested)
- Phoebus OPI: `plotApp/op/bob/TASPlot.bob`
- **Browse** (`SelectedFile` / FileSelector) → auto-load plot (no button)
- **Scan #** spinner → rebuilds `*_scanNNNN.dat`, auto-reload
- **Reload** button → re-read current file (`TAS:Plot:Acquire` PV unchanged)
- Long paths via `lsi`/`lso` + Phoebus `.$` suffix (255 chars)

**Dev data path:**

`/home/kg1/Documents/Detector/HB3/HB3_data/User/exp382/Datafiles/HB3_exp0382_scan0001.dat` … `0004.dat`

## Build

```bash
cd /home/kg1/Documents/src/github/ioc-tasplot
cp configure/RELEASE.local.example configure/RELEASE.local   # once
make -sj
```

Requires: EPICS Base (`/epics/base`), `python3-dev`.  
`configure/CONFIG.PyDevice` is generated on build, gitignored.

## IOC runtime

**Start** (keep terminal open — IOC needs stdin):

```bash
cd iocBoot/iocTasplot
./st.cmd
```

Boot calls `set_selected_file(…scan0001.dat)` which auto-loads scan 1.

**Smoke test (second terminal):**

```bash
caget TAS:Plot:NRows_RBV
caget -S TAS:Plot:SelectedFile.$
caget -S TAS:Plot:FullFileName_RBV.$
caput TAS:Plot:FileNumber 2          # plot reloads without Reload button
caget TAS:Plot:NRows_RBV
caget TAS:Plot:LastError_RBV
```

**Phoebus:** File → Open → `plotApp/op/bob/TASPlot.bob`. Macro `P` = `TAS:Plot:`.

If pink borders or **“multiple servers”**: Preferences → EPICS → set CA address list to IOC host; optional `EPICS_CAS_SERVER_PORT` / `EPICS_CAS_BEACON_ADDR_LIST` in `st.cmd` (commented out by default; worked without them locally).

## PV layout (file selection)

| PV | Role |
|----|------|
| `SelectedFile` (`lso`, use `.$`) | Write: full path from File / FileSelector; auto-loads |
| `FileNumber` (`longout`) | Scan # spinner; auto-reload |
| `FullFileName_RBV` (`lsi`, use `.$`) | Resolved path IOC loads (grey header; updates on Scan #) |
| `FileExists_RBV` | File readable |
| `Acquire` (`longout`) | Manual reload only (**Reload** button in OPI) |
| `Xdata` / `Ydata` / `YdataErr` | Plot waveforms (SCAN 1 s) |
| `SpecScanNumber` | SPEC `#S` selection; auto-reload for spec files |

Legacy **`FilePath` / `FileName`** records removed.

## Architecture (short)

- `python/tasplot/` — SPiCE + SPEC parsers (no EPICS)
- `python/graffiti_app.py` — `graffiti_plot` singleton; methods from `@graffiti_plot.*` in DB
- `plotApp/Db/plot.template` — PyDevice records
- `plotApp/op/bob/TASPlot.bob` — Browse + Graph (SPiCE Data tab successor)

SPiCE GUI reference: [docs/reference/spice-gui/](reference/spice-gui/README.md)

## Done

- [x] tasplot parsers + fixtures + CI
- [x] PyDevice IOC build and boot
- [x] Long-string paths (`lsi`/`lso`, scanned readbacks)
- [x] Phoebus TASPlot.bob (browse, spinner, xyplot)
- [x] SelectedFile browse + FileNumber scroll with auto-reload
- [x] Reload button for growing scans / retry
- [x] Docs: `PYDEVICE_IOC.md`, `plotApp/op/README.md`

## Next (when resuming)

1. **Phoebus polish** — axis labels, plot title from scan metadata, DataFileContents-style text panel (SPiCE parity)
2. **Live reload** — periodic Reload or file watch while scan grows
3. **Normalization** — `NormMode`, `NormCol`, `NormValue` (SPiCE “Normalize to”)
4. **Beamline deploy** — `/epics/iocs/ioc-tasplot`, production paths in `st.cmd`, autosave
5. **Facility** — PVXS/QSRV 2; Combine Data / Data Buffers (later SPiCE tabs)

## Operational notes

- Plain `caget TAS:Plot:SelectedFile` truncates at 40 chars; use **`caget -S TAS:Plot:SelectedFile.$`**
- **File** (`SelectedFile.$`) is for paste/browse entry; after Scan # change, grey **FullFileName_RBV** shows the path IOC actually loads
- EPICS `DESC` fields max **40 characters** (boot fails if exceeded)
- Old Graffiti C IOC: `Detector/HB3/applications/hb3-Graffiti` (separate tree)
