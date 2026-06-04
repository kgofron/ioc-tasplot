from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator

import numpy as np

from tasplot.dataset import ScanDataset

# CERTIF SPEC: labels on #L are separated by two or more spaces (spec_manA4.pdf).
_LABEL_SPLIT = re.compile(r"  +")
_SCAN_START = re.compile(r"^#S\s+(\d+)\s*(.*)$")


def parse_spec_file(
    path: str | Path,
    scan_number: int | None = None,
    scan_index: int | None = None,
) -> ScanDataset:
    """
    Load one scan from a CERTIF SPEC data file.

    Parameters
    ----------
    scan_number:
        Match the integer after ``#S`` (user scan number). If duplicate numbers
        exist, the last occurrence is used (scans.4 convention).
    scan_index:
        Zero-based index among all ``#S`` blocks in the file.
    """
    path = str(path)
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    file_meta, scans = _split_spec_scans(text)

    if not scans:
        raise ValueError(f"no #S scans found in {path}")

    if scan_index is not None:
        if scan_index < 0 or scan_index >= len(scans):
            raise IndexError(f"scan_index {scan_index} out of range (0..{len(scans)-1})")
        block = scans[scan_index]
    elif scan_number is not None:
        matches = [s for s in scans if s["scan_number"] == scan_number]
        if not matches:
            available = sorted({s["scan_number"] for s in scans})
            raise ValueError(
                f"scan #{scan_number} not in {path}; available: {available[:20]}..."
            )
        block = matches[-1]
    else:
        block = scans[-1]

    return _parse_spec_scan_block(path, block, file_meta)


def list_spec_scans(path: str | Path) -> list[dict[str, int | str | None]]:
    """Summarize ``#S`` blocks without loading full tables."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    _, scans = _split_spec_scans(text)
    out = []
    for i, s in enumerate(scans):
        ds = _parse_spec_scan_block(str(path), s, {})
        out.append(
            {
                "index": i,
                "scan_number": s["scan_number"],
                "command": ds.command,
                "nrows": ds.nrows,
                "columns": len(ds.columns),
            }
        )
    return out


def _split_spec_scans(text: str) -> tuple[dict[str, str], list[dict]]:
    lines = text.splitlines()
    file_meta: dict[str, str] = {}
    scans: list[dict] = []
    current: dict | None = None
    in_file_header = True

    for line in lines:
        sm = _SCAN_START.match(line)
        if sm:
            in_file_header = False
            if current is not None:
                scans.append(current)
            current = {
                "scan_number": int(sm.group(1)),
                "command": sm.group(2).strip() or None,
                "lines": [line],
            }
            continue

        if in_file_header:
            _store_spec_line(file_meta, line)
            continue

        if current is not None:
            current["lines"].append(line)

    if current is not None:
        scans.append(current)

    return file_meta, scans


def _store_spec_line(meta: dict[str, str], line: str) -> None:
    if not line.startswith("#") or len(line) < 2:
        return
    tag = line[1]
    rest = line[2:].strip()
    if tag in "FEDC":
        key = {"F": "file", "E": "epoch", "D": "date", "C": "comment"}[tag]
        meta[key] = rest
    elif tag == "O" and rest[:1].isdigit():
        meta.setdefault("motors", "")
        meta["motors"] += rest + "\n"


def _parse_spec_scan_block(
    path: str, block: dict, file_meta: dict[str, str]
) -> ScanDataset:
    meta: dict[str, str] = dict(file_meta)
    columns: list[str] = []
    ncols: int | None = None
    default_x: str | None = None
    default_y: str | None = None
    data_rows: list[list[float]] = []

    for line in block["lines"]:
        if not line.startswith("#"):
            parts = line.split()
            if parts and _looks_numeric_row(parts):
                if ncols is not None and len(parts) != ncols:
                    continue
                data_rows.append([float(x) for x in parts])
            continue

        if len(line) < 2:
            continue
        tag = line[1]
        rest = line[2:].strip()

        if tag == "D":
            meta["date"] = rest
        elif tag == "T":
            meta["preset"] = rest
        elif tag == "M":
            meta["monitor_preset"] = rest
        elif tag == "Q":
            meta["Q"] = rest
        elif tag == "N":
            try:
                ncols = int(rest.split()[0])
                meta["ncolumns"] = str(ncols)
            except ValueError:
                pass
        elif tag == "L":
            columns = [c for c in _LABEL_SPLIT.split(rest.strip()) if c]
        elif tag == "C":
            meta.setdefault("comments", "")
            meta["comments"] += rest + "\n"

    data = (
        np.array(data_rows, dtype=float)
        if data_rows
        else np.zeros((0, len(columns) if columns else 0))
    )

    if columns and data.shape[0] and data.shape[1] != len(columns):
        # Pad or trim if site wrote inconsistent rows
        ncol = len(columns)
        fixed = []
        for row in data_rows:
            if len(row) == ncol:
                fixed.append(row)
        data = np.array(fixed, dtype=float) if fixed else np.zeros((0, ncol))

    if columns:
        default_x = columns[0]
        default_y = _pick_spec_y(columns, block.get("command"))

    return ScanDataset(
        format="spec",
        path=path,
        meta=meta,
        columns=columns,
        data=data,
        default_x=default_x,
        default_y=default_y,
        scan_number=block["scan_number"],
        command=block.get("command"),
        file_meta=file_meta,
    )


def _pick_spec_y(columns: list[str], command: str | None) -> str:
    """Prefer Detector; else last column (scans.4 default)."""
    lower = {c.lower(): c for c in columns}
    if "detector" in lower:
        return lower["detector"]
    if "det" in lower:
        return lower["det"]
    if command:
        motor = command.split()[0] if command.split() else None
        if motor and motor in columns:
            return motor
    return columns[-1]


def _looks_numeric_row(parts: list[str]) -> bool:
    try:
        float(parts[0])
        return True
    except ValueError:
        return False
