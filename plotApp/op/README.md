# Phoebus operator displays

| File | Purpose |
|------|---------|
| `bob/TASPlot.bob` | Minimal **Browse Data** + **Graph Data** (macro `P`, default `TAS:Plot:`) |

## Open in Phoebus

1. Start IOC: `iocBoot/iocTasplot/./st.cmd`
2. Phoebus → **File → Open** → `plotApp/op/bob/TASPlot.bob`
3. Set macro **`P`** to match `plot.substitutions` (e.g. `HB3:Plot:` on HB3 dev `st.cmd`, or `TAS:Plot:`)
4. CA gateway: same host as IOC (or set `EPICS_CA_ADDR_LIST`)
5. Click **Acquire** after adjusting path/name/scan number

SPiCE reference screenshots: [docs/reference/spice-gui/](../../docs/reference/spice-gui/README.md).
