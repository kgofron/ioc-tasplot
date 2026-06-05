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
6. **Directory** / **Name stem** / **Scan #** use `lso`/`longout` PVs (255-char paths; old 40-char `stringout` truncated paths)
7. Click **Acquire** after adjusting path/name/scan number (e.g. scan `1` → `HB3_exp0382_scan0001.dat`)

SPiCE reference screenshots: [docs/reference/spice-gui/](../../docs/reference/spice-gui/README.md).
