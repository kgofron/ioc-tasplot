# Phoebus operator displays

| File | Purpose |
|------|---------|
| `bob/HB3Plot.bob` | Minimal **Browse Data** + **Graph Data** (prefix `HB3:Plot:`) |

## Open in Phoebus

1. Start IOC: `iocBoot/iocTasplot/./st.cmd`
2. Phoebus → **File → Open** → `plotApp/op/bob/HB3Plot.bob`
3. CA gateway: same host as IOC (or set `EPICS_CA_ADDR_LIST`)
4. Click **Acquire** after adjusting path/name/scan number

Override prefix at open if `st.cmd` uses a different `P=` in `plot.substitutions`.

SPiCE reference screenshots: [docs/reference/spice-gui/](../../docs/reference/spice-gui/README.md).
