# Phoebus operator displays

| File | Purpose |
|------|---------|
| `bob/TASPlot.bob` | Minimal **Browse Data** + **Graph Data** (macro `P`, default `TAS:Plot:`) |

## Open in Phoebus

1. Build (after Db changes): `make -sj` from repo root
2. Start IOC: `iocBoot/iocTasplot/./st.cmd` (keep terminal open)
3. Phoebus → **File → Open** → `plotApp/op/bob/TASPlot.bob`
4. Macro **`P`** defaults to `TAS:Plot:` (matches `PREFIX` in `st.cmd` and `plot.substitutions`)
5. If widgets show pink borders or **"multiple servers"** warnings: **Preferences → EPICS** → set **CA Address List** to the IOC host (optionally `:50950` if `EPICS_CAS_SERVER_PORT` is enabled in `st.cmd`) and disable auto address list
6. **File** field + folder button use `SelectedFile.$` (`lso`, full path); browse auto-loads the plot (SPiCE-like)
7. **Scan #** spinner rebuilds `HB3_*_scanNNNN.dat` in the same directory and reloads automatically
8. Long-string PVs need the `.$` suffix (`SelectedFile.$`, `FullFileName_RBV.$`); plain names truncate at 40 chars
9. **Reload** re-reads the current file (e.g. while a scan is still growing)
10. **Graph Data** — **X col** / **Y col** pull-downs (`XCol`, `YCol` combo, items from `ColHeaders_RBV`); **Columns** line lists all names

SPiCE reference screenshots: [docs/reference/spice-gui/](../../docs/reference/spice-gui/README.md).
