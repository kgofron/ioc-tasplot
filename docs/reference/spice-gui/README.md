# SPiCE GUI reference (HB3)

Screenshots of the legacy **HB3 Triple Axis Control Program** (SPiCE) **Data** tab.
Used as UX reference for **ioc-tasplot** Phoebus OPIs — not a pixel-perfect target.

## Full-window captures

| Image | SPiCE tab | ioc-tasplot phase |
|-------|-----------|-------------------|
| [BrowseData-full-window.png](BrowseData-full-window.png) | Browse Data | **v1** — file browse, Scan # spinner |
| [GraphData-full-window.png](GraphData-full-window.png) | Graph Data | **v1** — default plot; **v2** — column picker |
| [CombineData-full-window.png](CombineData-full-window.png) | Combine Data | **Later** — multi-scan merge |
| [DataBuffers-full-window.png](DataBuffers-full-window.png) | Data Buffers | **Later** — scratch buffers |

## Detail captures (cropped)

| Image | Shows | ioc-tasplot phase |
|-------|-------|-------------------|
| [BrowseData-norm-menu.png](BrowseData-norm-menu.png) | “No normalization” menu | **Phase 2** — `NormMode` |
| [BrowseData-scan-plot.png](BrowseData-scan-plot.png) | Browse plot + `DataFileContents` | **Phase 4** — header text panel |
| [GraphData-column-picker-y.png](GraphData-column-picker-y.png) | Y column dropdown | **Phase 1** — `YCol` |
| [GraphData-column-picker-x.png](GraphData-column-picker-x.png) | X column dropdown | **Phase 1** — `XCol` |
| [GraphData-norm-and-plot.png](GraphData-norm-and-plot.png) | Graph tab, norm dropdown | **Phase 2** |
| [GraphData-new-plot-menu.png](GraphData-new-plot-menu.png) | New Plot / Overplot | **Phase 5** — overlay traces |
| [GraphData-log-scales.png](GraphData-log-scales.png) | Linear / log axis scales | **Phase 4** |
| [GraphData-peak-fit.png](GraphData-peak-fit.png) | Gaussian fit + background | **Phase 6** — or PyMca |
| [CombineData-scan-lists.png](CombineData-scan-lists.png) | +/- scan lists, norm row | **Phase 5** |
| [DataBuffers-table.png](DataBuffers-table.png) | Buffer table + save | **Phase 5** |

## PV mapping (current → planned)

| SPiCE control | ioc-tasplot PV (now) | Planned |
|---------------|----------------------|---------|
| File / scan path | `SelectedFile`, `FileNumber` | — |
| X column | `DetX_RBV` (read-only default) | `XCol` (writable) |
| Y column | `DetY_RBV` (read-only default) | `YCol` (writable) |
| Column list | — | `ColHeaders_RBV` |
| Normalize to | — | `NormMode`, `NormCol`, `NormValue` |
| Plot | `Xdata`, `Ydata`, `YdataErr` | + axis label readback |

Modern UI: [`plotApp/op/bob/TASPlot.bob`](../../../plotApp/op/bob/TASPlot.bob) (Phoebus) instead of nested LabVIEW tabs.
