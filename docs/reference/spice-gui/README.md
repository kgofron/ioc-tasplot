# SPiCE GUI reference (HB3)

Screenshots of the legacy **HB3 Triple Axis Control Program** (SPiCE) **Data** tab.
Used as UX reference for **ioc-tasplot** Phoebus OPIs — not a pixel-perfect target.

## Full-window captures

| Image | SPiCE tab | ioc-tasplot phase |
|-------|-----------|-------------------|
| [BrowseData-full-window.png](BrowseData-full-window.png) | Browse Data | **v1 (done)** — file browse, Scan # spinner |
| [GraphData-full-window.png](GraphData-full-window.png) | Graph Data | **v1 (done)** — xyplot, column picker |
| [CombineData-full-window.png](CombineData-full-window.png) | Combine Data | **Phase 5** — multi-scan merge |
| [DataBuffers-full-window.png](DataBuffers-full-window.png) | Data Buffers | **Phase 5** — scratch buffers |

## Detail captures (cropped)

| Image | Shows | ioc-tasplot phase |
|-------|-------|-------------------|
| [BrowseData-norm-menu.png](BrowseData-norm-menu.png) | “No normalization” menu | **Phase 2 (done)** — `NormMode` |
| [BrowseData-scan-plot.png](BrowseData-scan-plot.png) | Browse plot + `DataFileContents` | **Done** — `DataFileText` full file |
| [GraphData-column-picker-y.png](GraphData-column-picker-y.png) | Y column dropdown | **Phase 1 (done)** — `YCol` |
| [GraphData-column-picker-x.png](GraphData-column-picker-x.png) | X column dropdown | **Phase 1 (done)** — `XCol` |
| [GraphData-norm-and-plot.png](GraphData-norm-and-plot.png) | Graph tab, norm dropdown | **Phase 2 (done)** |
| [GraphData-new-plot-menu.png](GraphData-new-plot-menu.png) | New Plot / Overplot | **Phase 5** — overlay traces |
| [GraphData-log-scales.png](GraphData-log-scales.png) | Linear / log axis scales | **Phase 4** |
| [GraphData-peak-fit.png](GraphData-peak-fit.png) | Gaussian fit + background | **Phase 6** — or PyMca button |
| [CombineData-scan-lists.png](CombineData-scan-lists.png) | +/- scan lists, norm row | **Phase 5** |
| [DataBuffers-table.png](DataBuffers-table.png) | Buffer table + save | **Phase 5** |

## PV mapping (SpICE → ioc-tasplot)

| SPiCE control | ioc-tasplot PV | Status |
|---------------|----------------|--------|
| File / scan path | `SelectedFile`, `FileNumber`, `FullFileName_RBV` | **Done** |
| X column | `XCol`, `XCol_RBV`, `DetX_RBV` | **Done** |
| Y column | `YCol`, `YCol_RBV`, `DetY_RBV` | **Done** |
| Column list | `ColHeaders_RBV` | **Done** |
| Normalize to | `NormMode`, `NormCol`, `NormValue`, `NormCol_RBV` | **Done** |
| File text panel | `DataFileText` | **Done** |
| Plot | `Xdata`, `Ydata`, `YdataErr` | **Done** |
| Axis label | `PlotAxisLabel_RBV` | **Done** (norm-aware) |
| Reload / growing scan | `Acquire` (Reload button) | **Done** |
| Peak fit | — | **Phase 6** or **PyMca** (optional button) |
| Overplot / combine | — | **Phase 5** |
| Log scales | — | **Phase 4** |

Modern UI: [`plotApp/op/bob/TASPlot.bob`](../../../plotApp/op/bob/TASPlot.bob) (Phoebus) instead of nested LabVIEW tabs.
