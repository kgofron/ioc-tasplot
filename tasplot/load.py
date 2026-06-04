from __future__ import annotations

from pathlib import Path

from tasplot.dataset import FormatError, ScanDataset
from tasplot.spec import parse_spec_file
from tasplot.spice import parse_spice_dat


def detect_format(path: str | Path) -> str:
    """
    Return ``"spice"`` or ``"spec"``.

    SPiCE: ``# scan =`` or ``# def_x =`` in header.
    SPEC: ``#F`` file header and ``#S`` scan markers per CERTIF manual.
    """
    path = Path(path)
    head = path.read_text(encoding="utf-8", errors="replace")[:8192]
    if "# scan =" in head or "# def_x =" in head or "# col_headers =" in head:
        return "spice"
    if head.lstrip().startswith("#F ") and "#S " in head:
        return "spec"
    raise FormatError(f"unrecognized scan format: {path}")


def load_scan(path: str | Path) -> ScanDataset:
    """Load a scan file; format detected automatically."""
    fmt = detect_format(path)
    if fmt == "spice":
        return parse_spice_dat(path)
    return parse_spec_file(path)


def load_spec_file(
    path: str | Path,
    scan_number: int | None = None,
    scan_index: int | None = None,
) -> ScanDataset:
    """Load a SPEC file (optionally select scan by number or index)."""
    return parse_spec_file(path, scan_number=scan_number, scan_index=scan_index)
