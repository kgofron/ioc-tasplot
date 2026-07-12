# Phoebus operator displays

| File | Purpose |
|------|---------|
| `bob/TASPlot.bob` | **Browse Data** + **Graph Data** (macro `P`, default `TAS:Plot:`) |
| `scripts/open_in_pymca.sh` | Open current scan in PyMca (peak fit / overlay) |

 Phoebus **command** actions expand `$(P)` but **not** `$(D)`, and they **split the command on spaces** (so no `bash -c "..."` one-liners). The PyMca button runs:

`bash ../scripts/open_in_pymca.sh $(P)`

with the process working directory = folder containing the open `.bob`. That matches:

- **Repo:** `plotApp/op/bob/` + `plotApp/op/scripts/`
- **Deploy:** `…/R1-0/Common/` + `…/R1-0/scripts/`

Failures log to `/tmp/open_in_pymca.log` and Phoebus Console.

## Open in Phoebus

1. Build (after Db changes): `make -sj` from repo root; `make -C plotApp/Db install` if only Db changed
2. Start IOC: `iocBoot/iocTasplot/./st.cmd` (keep terminal open)
3. Phoebus → **File → Open** → `plotApp/op/bob/TASPlot.bob`
4. Macro **`P`** defaults to `TAS:Plot:`
5. If pink borders / **"multiple servers"**: Preferences → EPICS → CA Address List = IOC host
6. **File** + folder button → `SelectedFile.$` (auto-load)
7. **Scan #** → rebuilds `*_scanNNNN.dat`; grey header = `FullFileName_RBV.$`
8. **Reload** — re-read file (keeps X/Y); **Live** — auto-reload when file grows
9. **Over #** + **Overlay** — second trace (orange) from another scan # in the same folder
10. **PyMca** — opens current file for peak fit (needs `python3-pymca5` / `pymca`). Launcher uses `caget -S`, forces apt NumPy 1.x if needed, and logs to `/tmp/open_in_pymca.log` (Phoebus hides stderr). SPICE `.dat` and SPEC both open via SpecFile.
11. **Graph Data** — X/Y cols, Norm, **Log X / Log Y**, **Errors** (`ShowErrors` — Poisson √N on Y); title from `Command_RBV.$`; Y label from `PlotAxisLabel_RBV`
12. **DataFileContents** — `DataFileText` CHAR waveform

SPiCE reference: [docs/reference/spice-gui/](../../docs/reference/spice-gui/README.md).
