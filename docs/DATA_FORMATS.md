# Scan data file formats

Graffiti / `tasplot` supports two ASCII families used during experiments.

## 1. SPiCE `.dat` (HFIR TAS)

### Path convention (HB-3)

```
{user_root}/exp{experiment}/Datafiles/HB3_exp{experiment:04d}_scan{scan:04d}.dat
```

- Folder `exp382` matches `# experiment_number = 382`.
- Filename uses **four-digit** experiment and scan indices (`0382`, `0001`).

### Structure

1. **Header** — lines `# key = value` (metadata, lattice, UB matrix, presets).
2. **Column declaration** — `# col_headers =` then a line `#   Pt.  motor  time  detector  ...`.
3. **Data** — whitespace-separated rows (no `#` prefix); first column is point index.
4. **Footer** (optional) — `# Sum of Counts`, `# Center of Mass`, `# FWHM`, completion line.

**Default plot axes:** `# def_x`, `# def_y` (e.g. `s1`, `detector`).

**Parser notes:** Column names and order change per scan (scanned motor moves in the header row). Always parse `col_headers` per file.

---

## 2. CERTIF SPEC standard data file

Official definition: [spec_manA4.pdf](https://certif.com/downloads/css_docs/spec_manA4.pdf) — *Standard Data-File Format* (User Manual § “Standard Data File Format”, Reference Manual `#F` / `#S` / `#L` / `#N`).

### File-level header (once per file)

| Line | Meaning |
|------|---------|
| `#F filename` | Path/name file was opened with |
| `#E epoch` | UNIX epoch seconds at file creation (for `Epoch` column) |
| `#D date` | Human-readable date |
| `#C text` | Comment (e.g. user, sample) |
| `#O0` … | Motor names (two spaces between names) |
| `#o0` … | Optional short motor aliases |

### Per-scan block

Each scan begins with `#S` (often preceded by a blank line in spec output):

| Line | Meaning |
|------|---------|
| `#S n command args…` | Scan number and scan macro invocation |
| `#D date` | Scan start time |
| `#T` / `#M` | Count-to-time or count-to-monitor preset |
| `#G0` … `#G4` | Diffractometer / UB geometry (site-specific) |
| `#Q h k l` | Reciprocal-space position at scan start |
| `#P0` … | Motor positions at scan start (columns ↔ `#O` motors) |
| `#N columns` | Number of numeric data columns |
| `#L lab1 lab2 …` | Column labels (**two spaces** between labels per manual) |
| `#C …` | Comments (may appear inside data; scan may abort) |

**Data rows:** space-separated floats; row continues until next `#` control line, blank line, or next `#S`.

**scans.4 defaults** (same manual): **x = first column**, **y = last column**, monitor often second-to-last when present.

### NSLS-II example on disk

| Item | Value |
|------|--------|
| Path | `/home/kg1/Documents/src/PyMCA/YongCai/20240530` |
| Source | Yong Cai (BNL / NSLS-II) |
| Instrument context | `#C fourc User = xf10id` — four-circle SPEC |
| Scans | Many `#S` blocks in one file (e.g. `ascan ugap …`) |
| Columns | 47 in scan 2: `UGap H K L Epoch Seconds Monitor Detector …` |

Scan 1 in that file was aborted with zero points (`#C Scan aborted after 0 points`); scan 2+ contain numeric tables.

---

## Unified model (`ScanDataset`)

Both parsers populate:

- `format` — `"spice"` or `"spec"`
- `meta` — header key/value strings
- `columns` — data column names
- `data` — `numpy` array shape `(n_points, n_columns)`
- `default_x`, `default_y` — column names for plotting
- `scan_number` — SPiCE: `# scan`; SPEC: `#S` first field
- `command` — scan command string when present

## Format detection

1. If any line matches `# scan =` or `# def_x =` → **SPiCE**.
2. Else if file starts with `#F ` and contains `#S ` → **SPEC**.
3. Else raise `FormatError`.

## Concurrent support evaluation

| Capability | SPiCE `.dat` | SPEC file |
|------------|--------------|-----------|
| One file per scan | Yes (HB3) | Optional (multi-scan file common) |
| Live append during scan | Yes (rewrite/append rows) | Yes (same; tail parser can refresh) |
| Default X/Y | `def_x`, `def_y` | First/last column or name heuristics (`Detector`, scanned motor from `#S`) |
| HKL in table | Often `h`, `k`, `l` columns | `#Q` + `H`,`K`,`L` columns |
| Merge scans | By scan number across files | By `#S` number inside file or across files |
| PyMca | SpecFile-compatible subset | Native SPEC |

**Recommendation:** Keep **one plotting UI** and **two parsers** behind `load_scan()` / `load_spec_file()`. The **PyDevice IOC** (`graffiti_app` + `tasplot`) should call this library — not a separate pcaspy parser. See [PYDEVICE_IOC.md](PYDEVICE_IOC.md).

## Future work

- PyDevice IOC build/Makefile (mirror ioc-hkl); PVXS via facility `add_pvxs.py`
- Live file watcher (inotify) for growing scans
- Gaussian/Lorentzian fits (Graffiti parity)
- SPEC `.I` index files (optional, per scans.4)
- Export to ONCat/Mantid (out of band)
