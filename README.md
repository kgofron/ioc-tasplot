# ioc-tasplot

Live TAS scan plotting via a **PyDevice** EPICS IOC (Graffiti / SPiCE Graph Data successor). Loads **SPiCE** `.dat` and **CERTIF SPEC** scan files into waveform PVs for Phoebus and PVXS clients.

## Supported formats

| Format | Typical source | Reference |
|--------|----------------|-----------|
| **SPiCE** `.dat` | HFIR HB-3, HB-1, CTAX (legacy SPiCE) | ORNL SPiCE graph-data conventions |
| **CERTIF SPEC** | NSLS-II, many synchrotron diffractometers | [SPEC standard data file format](https://certif.com/downloads/css_docs/spec_manA4.pdf) |

One Python API loads either format into the same `ScanDataset` structure (metadata, column names, arrays, default X/Y).

## HB3 SPiCE layout

```
{user_root}/exp{N}/Datafiles/HB3_exp{NNNN}_scan{SSSS}.dat
```

Example: `exp382/Datafiles/HB3_exp0382_scan0001.dat`

Default user root on this system (development):  
`/home/kg1/Documents/Detector/HB3/HB3_data/User`

## SPEC sample (Yong Cai, NSLS-II)

A multi-scan SPEC file from Yong Cai (BNL) is on this machine at:

`/home/kg1/Documents/src/PyMCA/YongCai/20240530`

A truncated copy for unit tests lives under `tests/fixtures/spec_yongcai_sample.spec`.

## EPICS delivery: PyDevice IOC (not pcaspy)

Production plotting is a **PyDevice soft IOC** (like [ioc-hkl](https://github.com/hkl-projects/ioc-hkl)), so PVs live in a normal database, **PVXS/QSRV 2** applies, **autosave** works, and **Secure EPICS** can be used when deployed.

See [docs/PYDEVICE_IOC.md](docs/PYDEVICE_IOC.md), `plotApp/Db/plot.template`, `python/graffiti_app.py`, `iocBoot/iocTasplot/st.cmd`.

## Install (development)

```bash
cd /home/kg1/Documents/src/github/ioc-tasplot
PYTHONPATH=. python3 -m pytest
pip install -e ".[dev]"   # optional
```

## Build EPICS IOC

Requires EPICS Base and Python development headers (`python3-dev` on Ubuntu).
If you see `Python.h: No such file or directory`, install `python3-dev`, then
`make -C configure clean_pydevice && make` (regenerates `configure/CONFIG.PyDevice`).

```bash
cd /home/kg1/Documents/src/github/ioc-tasplot
cp configure/RELEASE.local.example configure/RELEASE.local   # edit EPICS_BASE / PYTHON_CONFIG
make -j
```

Boot (after build):

```bash
cd iocBoot/iocTasplot
../../bin/linux-x86_64/plotApp st.cmd
```

`src/` contains [PyDevice](https://github.com/klemenv/PyDevice) device support (vendored for standalone builds).

## Quick use

```python
from tasplot import load_scan, load_spec_file, hb3_scan_path

# SPiCE HB3 scan
path = hb3_scan_path("/home/kg1/Documents/Detector/HB3/HB3_data/User", 382, 1)
scan = load_scan(path)
print(scan.format, scan.default_x, scan.default_y, scan.nrows)

# SPEC: one scan from multi-scan file (scan number 2)
spec_path = "tests/fixtures/spec_yongcai_sample.spec"
scan2 = load_spec_file(spec_path, scan_number=2)
```

## Phoebus

Minimal OPI (Browse + Graph Data): `plotApp/op/bob/HB3Plot.bob` — see [plotApp/op/README.md](plotApp/op/README.md).

SPiCE GUI reference images: [docs/reference/spice-gui/](docs/reference/spice-gui/README.md).

## Repository layout

```
tasplot/              # Python library (parsers)
python/               # PyDevice backend (graffiti_app.py)
plotApp/Db/           # EPICS database templates
plotApp/op/bob/       # Phoebus displays
iocBoot/iocTasplot/   # st.cmd
docs/
tests/
```

## References

- CERTIF SPEC format: https://certif.com/downloads/css_docs/spec_manA4.pdf
- ORNL SPiCE graph data: https://neutrons.ornl.gov/spice/tab_graphdata.html
- [ioc-hkl](https://github.com/hkl-projects/ioc-hkl) — PyDevice IOC template
