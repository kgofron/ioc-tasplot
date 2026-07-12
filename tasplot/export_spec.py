"""Export ScanDataset as a minimal CERTIF SPEC file (for PyMca SpecFile)."""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

from tasplot.dataset import ScanDataset


def dataset_to_spec_text(scan: ScanDataset, *, source_path: str | None = None) -> str:
    """Build a one-scan SPEC file text with named ``#L`` columns."""
    if scan.nrows == 0:
        raise ValueError("cannot export empty scan to SPEC")
    if not scan.columns:
        raise ValueError("cannot export scan without columns")

    src = source_path or scan.path or "spice.dat"
    base = Path(src).name
    scan_no = int(scan.scan_number or 1)
    command = (scan.command or "spice").strip() or "spice"
    # CERTIF #L: labels separated by two or more spaces.
    labels = "  ".join(_spec_label(c) for c in scan.columns)

    lines = [
        f"#F {base}",
        f"#E {int(time.time())}",
        f"#D {time.strftime('%a %b %d %H:%M:%S %Y')}",
        f"#C converted from SPICE by ioc-tasplot ({src})",
        f"#S {scan_no} {command}",
        f"#N {len(scan.columns)}",
        f"#L {labels}",
    ]
    for row in scan.data:
        lines.append(" ".join(f"{float(v):.8g}" for v in row))
    lines.append("")
    return "\n".join(lines)


def write_temp_spec(scan: ScanDataset, *, source_path: str | None = None) -> Path:
    """Write ``scan`` to a temp ``.spec`` file; caller owns cleanup."""
    text = dataset_to_spec_text(scan, source_path=source_path)
    fd, name = tempfile.mkstemp(prefix="ioc-tasplot-pymca-", suffix=".spec")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
    except Exception:
        try:
            os.unlink(name)
        except OSError:
            pass
        raise
    return Path(name)


def _spec_label(name: str) -> str:
    """SPEC #L labels cannot contain spaces; keep SPICE tokens intact otherwise."""
    cleaned = name.strip().replace(" ", "_")
    return cleaned or "col"
