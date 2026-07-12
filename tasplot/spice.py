from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from tasplot.dataset import ScanDataset

_META_RE = re.compile(r"^#\s*([^=]+?)\s*=\s*(.*)$")


def parse_spice_dat(path: str | Path) -> ScanDataset:
    """Parse a SPiCE-style .dat scan file (HFIR TAS)."""
    path = str(path)
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    # Normalize DOS CRLF / bare CR so tokens never carry trailing \\r.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()

    meta: dict[str, str] = {}
    columns: list[str] = []
    default_x: str | None = None
    default_y: str | None = None
    data_rows: list[list[float]] = []
    footer: dict[str, str] = {}

    data_start: int | None = None
    data_end: int | None = None

    for i, line in enumerate(lines):
        m = _META_RE.match(line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            meta[key] = val
            if key == "def_x":
                default_x = val
            elif key == "def_y":
                default_y = val
            elif key == "col_headers":
                continue
            continue

        if line.startswith("#") and "Pt." in line and "=" not in line:
            header_line = line.lstrip("#").strip()
            columns = header_line.split()
            data_start = i + 1
            continue

        if data_start is not None and data_end is None:
            stripped = line.strip()
            if not stripped:
                # Blank lines are common while a live scan file grows; skip them.
                continue
            if stripped.startswith("#"):
                data_end = i
                fm = _META_RE.match(line)
                if fm:
                    footer[fm.group(1).strip().lower()] = fm.group(2).strip()
                continue
            parts = stripped.split()
            # Drop editor artifacts like a trailing literal "^M" (caret+M).
            parts = [p[:-2] if p.endswith("^M") else p for p in parts]
            row = _parse_numeric_row(parts, expected=len(columns) if columns else None)
            if row is not None:
                data_rows.append(row)

    if not columns:
        raise ValueError(f"no column header (Pt.) found in {path}")

    data = np.array(data_rows, dtype=float) if data_rows else np.zeros((0, len(columns)))

    scan_number = None
    if "scan" in meta:
        try:
            scan_number = int(meta["scan"].split()[0])
        except ValueError:
            pass

    return ScanDataset(
        format="spice",
        path=path,
        meta={**meta, **footer},
        columns=columns,
        data=data,
        default_x=default_x,
        default_y=default_y,
        scan_number=scan_number,
        command=meta.get("command"),
    )


def _parse_numeric_row(
    parts: list[str], expected: int | None = None
) -> list[float] | None:
    """Return floats for a data row, or None if incomplete/corrupt (live scan safe)."""
    if not parts or not _looks_numeric_row(parts):
        return None
    if expected is not None and len(parts) != expected:
        # Growing file may have a partial last line — skip until complete.
        return None
    try:
        return [float(x) for x in parts]
    except ValueError:
        return None


def _looks_numeric_row(parts: list[str]) -> bool:
    try:
        float(parts[0])
        return True
    except ValueError:
        return False
