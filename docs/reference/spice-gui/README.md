# SPiCE GUI reference (HB3)

Screenshots of the legacy **HB3 Triple Axis Control Program** (SPiCE) **Data** tab.
Used as UX reference for **ioc-tasplot** Phoebus OPIs — not a pixel-perfect target.

| Image | SPiCE tab | ioc-tasplot scope |
|-------|-----------|-------------------|
| [BrowseData.png](BrowseData.png) | Browse Data | **v1** — `SelectedFile`, `FileNumber`, `FullFileName_RBV`, `FileExists_RBV` (legacy SPiCE used separate dir/name fields) |
| [GraphData.png](GraphData.png) | Graph Data | **v1** — `Acquire`, `Xdata`/`Ydata`/`YdataErr`, `DetX_RBV`/`DetY_RBV` |
| [CombineData.png](CombineData.png) | Combine Data | **Later** — multi-scan merge/normalize |
| [DataBuffers.png](DataBuffers.png) | Data Buffers | **Later** — scratch buffers / export |

Modern UI: single Phoebus panel ([`plotApp/op/bob/TASPlot.bob`](../../../plotApp/op/bob/TASPlot.bob)) instead of nested LabVIEW tabs.
