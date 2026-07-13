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

SPiCE conversion needs the **ioc-tasplot** checkout (package `tasplot`). When scripts are deployed under `/epics/GUI/.../scripts/`, set `IOC_TASPLOT_ROOT` to the repo root, or keep a checkout at `~/Documents/src/github/ioc-tasplot` (auto-detected).

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
10. **Combine Data** — `+ list` / `− list`, Norm to + weight col, Bin tol → **Combine** + **Show** (green trace). Shared folder scan #s; blank Combine X/Y = Graph X/Y.
11. **PyMca** — peak fit (`python3-pymca5` / `pymca`). **Shipped path:** SPiCE → temp SPEC (`tasplot.export_spec`) so SpecFile shows `s1`/`detector` names; CERTIF SPEC unchanged. **Longer-term alternative:** native SPiCE support in upstream PyMca (ESRF / [vasole/pymca](https://github.com/vasole/pymca)) — see [landscape](../../docs/reference/tas-plotting-tools-landscape.md#spice-in-pymca--two-viable-paths). Logs: `/tmp/open_in_pymca.log`.
12. **Graph Data** — X/Y cols, Norm, **Log X / Log Y**, **Errors** (`ShowErrors` — Poisson √N on Y); title from `Command_RBV.$`; Y label from `PlotAxisLabel_RBV`
13. **DataFileContents** — `DataFileText` CHAR waveform

SPiCE reference: [docs/reference/spice-gui/](../../docs/reference/spice-gui/README.md).
