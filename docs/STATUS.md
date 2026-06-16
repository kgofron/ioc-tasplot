# ioc-tasplot — session checkpoint (2026-06-16)

Handoff for resuming work after a break.

## Repository

- **Remote:** https://github.com/kgofron/ioc-tasplot
- **Branch:** `main` (sync with `origin/main` before long breaks)
- **Tests:** `23 passed` (`python3 -m pytest -q`)
- **Latest commits (newest first):**
  - `e7b9af6` chore: refresh STATUS, drop legacy CHAR PVs, add PyMca launcher
  - `94ed04c` docs(reference): add TAS plotting tools landscape for meeting prep
  - `865bb9d` style(op): tighten Graph Data toolbar layout in TASPlot.bob
  - `5d8e234` fix(phoebus): bind File field to SelectedFile for path entry
  - `22ce8fd` feat(plot): add SpICE-style Y normalization (Phase 2)

## What works (validated)

- IOC boots with PyDevice; prefix **`TAS:Plot:`**
- HB3 SPiCE `.dat` load via `tasplot` (exp382 scans 1–4 tested)
- Phoebus OPI: `plotApp/op/bob/TASPlot.bob`
- **Browse** (`SelectedFile` / FileSelector) → auto-load plot (no button)
- **Scan #** spinner → rebuilds `*_scanNNNN.dat`, auto-reload
- **Reload** button → re-read current file (`TAS:Plot:Acquire` PV unchanged)
- **Normalization** — `NormMode` (None / Column / Fixed), `NormCol`, `NormValue`
- **DataFileContents** — full-file text via I/O Intr (`DataFileText`, 64 KB cap)
- Long paths via `lsi`/`lso` + Phoebus `.$` suffix (255 chars)
- Optional **Open in PyMca** button (requires `python3-pymca5` on workstation)

**Dev data path** (verified on disk):

`/home/kg1/Documents/Detector/HB3/HB3_data/User/exp382/Datafiles/HB3_exp0382_scan0001.dat` … `0004.dat`

**Meeting / landscape docs:**

- [tas-plotting-tools-landscape.md](reference/tas-plotting-tools-landscape.md) — TAVI vs ioc-tasplot vs PyMca vs ioc-hkl
- [hb2d-ioc-tasplot-scope-mapping.md](reference/hb2d-ioc-tasplot-scope-mapping.md)

## Build

```bash
cd /home/kg1/Documents/src/github/ioc-tasplot
cp configure/RELEASE.local.example configure/RELEASE.local   # once
make -sj
```

Requires: EPICS Base (`/epics/base`), `python3-dev`.  
`configure/CONFIG.PyDevice` is generated on build, gitignored.

After **Db** changes: `make -C plotApp/Db install` (or full `make -sj`).

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
caput TAS:Plot:NormMode 1            # Column normalization
caput -S TAS:Plot:NormCol monitor
```

**Phoebus:** File → Open → `plotApp/op/bob/TASPlot.bob`. Macro `P` = `TAS:Plot:`.

If pink borders or **“multiple servers”**: Preferences → EPICS → set CA address list to IOC host; optional `EPICS_CAS_SERVER_PORT` / `EPICS_CAS_BEACON_ADDR_LIST` in `st.cmd` (commented out by default; worked without them locally).

## PV layout (file selection + plot)

| PV | Role |
|----|------|
| `SelectedFile` (`lso`, use `.$`) | Write: full path from File / FileSelector; auto-loads |
| `FileNumber` (`longout`) | Scan # spinner; auto-reload |
| `FullFileName_RBV` (`lsi`, use `.$`) | Resolved path IOC loads (grey header; updates on Scan #) |
| `FileExists_RBV` | File readable |
| `Acquire` (`longout`) | Manual reload only (**Reload** button in OPI) |
| `XCol` / `YCol` | Plot axis column selection |
| `NormMode` / `NormCol` / `NormValue` | SPiCE-style Y normalization |
| `Xdata` / `Ydata` / `YdataErr` | Plot waveforms (SCAN 1 s) |
| `DataFileText` | Full file text (I/O Intr, Browse Data parity) |
| `SpecScanNumber` | SPEC `#S` selection; auto-reload for spec files |

Legacy **`FilePath` / `FileName`** and unused pcaspy-style CHAR path waveforms removed.

## Architecture (short)

- `python/tasplot/` — SPiCE + SPEC parsers (no EPICS)
- `python/graffiti_app.py` — `graffiti_plot` singleton; methods from `@graffiti_plot.*` in DB
- `plotApp/Db/plot.template` — PyDevice records
- `plotApp/op/bob/TASPlot.bob` — Browse + Graph (SPiCE Data tab successor)
- `plotApp/op/scripts/open_in_pymca.sh` — optional PyMca launcher (offline fit)

SPiCE GUI reference: [docs/reference/spice-gui/](reference/spice-gui/README.md)

## Done

- [x] tasplot parsers + fixtures + CI
- [x] PyDevice IOC build and boot
- [x] Long-string paths (`lsi`/`lso`, scanned readbacks)
- [x] Phoebus TASPlot.bob (browse, spinner, xyplot)
- [x] SelectedFile browse + FileNumber scroll with auto-reload
- [x] Reload button for growing scans / retry
- [x] DataFileContents full file (I/O Intr, 64 KB)
- [x] Normalization (`NormMode`, `NormCol`, `NormValue`)
- [x] Landscape doc (TAVI, PyMca, ioc-hkl evaluation)
- [x] Docs: `PYDEVICE_IOC.md`, `plotApp/op/README.md`

## Next (when resuming)

1. **Phoebus polish** — plot title from scan metadata, axis labels from norm mode
2. **Live reload** — file watch or periodic reload while scan grows
3. **Phase 4** — log scales (SPiCE Graph Data)
4. **Phase 5** — combine scans / overlay traces
5. **Phase 6** — peak fit in OPI or delegate to PyMca
6. **Beamline deploy** — `/epics/iocs/ioc-tasplot`, production paths in `st.cmd`, autosave
7. **Facility** — PVXS/QSRV 2; Data Buffers tab (later SpICE parity)

## Operational notes

- Plain `caget TAS:Plot:SelectedFile` truncates at 40 chars; use **`caget -S TAS:Plot:SelectedFile.$`**
- **File** (`SelectedFile.$`) is for paste/browse entry; grey **FullFileName_RBV** shows the path IOC loads after Scan #
- EPICS `DESC` fields max **40 characters** (boot fails if exceeded)
- Old Graffiti C IOC: `Detector/HB3/applications/hb3-Graffiti` (separate tree)
- PyMca optional: `apt install python3-pymca5`; local prototype at `/epics/iocs/ioc-pymca`
