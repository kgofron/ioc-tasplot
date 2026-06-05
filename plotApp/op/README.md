# Phoebus operator displays

| File | Purpose |
|------|---------|
| `bob/TASPlot.bob` | Minimal **Browse Data** + **Graph Data** (macro `P`, default `TAS:Plot:`) |

## Open in Phoebus

1. Start IOC: `iocBoot/iocTasplot/./st.cmd`
2. Phoebus → **File → Open** → `plotApp/op/bob/TASPlot.bob`
3. Macro **`P`** defaults to `TAS:Plot:` (matches `PREFIX` in `st.cmd` and `plot.substitutions`)
4. CA gateway: same host as IOC (or set `EPICS_CA_ADDR_LIST`)
5. Click **Acquire** after adjusting path/name/scan number

SPiCE reference screenshots: [docs/reference/spice-gui/](../../docs/reference/spice-gui/README.md).
