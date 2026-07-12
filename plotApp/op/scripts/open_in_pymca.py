#!/usr/bin/env python3
"""Open a scan file in PyMca for peak fit / overlay (optional Phase 6 path).

Requires ``python3-pymca5`` / PyMca5, or a ``pymca`` binary on PATH.

SPiCE ``.dat`` files are converted to a temporary SPEC file so PyMca SpecFile
shows real column names (``s1``, ``detector``, …) instead of ``Column N``.
CERTIF SPEC files are passed through unchanged.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _ensure_tasplot_on_path() -> None:
    """Find ioc-tasplot repo so ``import tasplot`` works from repo or GUI deploy.

    Phoebus runs scripts from ``…/bob/TAS/R1-0/scripts/``, not ``plotApp/op/scripts``,
    so a fixed ``parents[2]`` is wrong. Search env, walk-up, then common checkouts.
    """
    here = Path(__file__).resolve().parent
    candidates: list[Path] = []
    for key in ("IOC_TASPLOT_ROOT", "TASPLOT_ROOT"):
        val = os.environ.get(key)
        if val:
            candidates.append(Path(val).expanduser().resolve())
    # Repo layout: …/ioc-tasplot/plotApp/op/scripts
    if len(here.parents) >= 3:
        candidates.append(here.parents[2])
    for parent in [here, *here.parents]:
        candidates.append(parent)
    candidates.extend(
        [
            Path.home() / "Documents/src/github/ioc-tasplot",
            Path("/home/kg1/Documents/src/github/ioc-tasplot"),
        ]
    )
    seen: set[str] = set()
    for root in candidates:
        try:
            root = root.resolve()
        except OSError:
            continue
        key = str(root)
        if key in seen:
            continue
        seen.add(key)
        if (root / "tasplot" / "__init__.py").is_file():
            if key not in sys.path:
                sys.path.insert(0, key)
            return
    raise ModuleNotFoundError(
        "tasplot not found (set IOC_TASPLOT_ROOT to the ioc-tasplot checkout)"
    )


def _path_for_pymca(path: str) -> str:
    """Return a SpecFile-friendly path (temp SPEC for SPiCE)."""
    _ensure_tasplot_on_path()
    from tasplot.load import detect_format, load_scan
    from tasplot.export_spec import write_temp_spec

    fmt = detect_format(path)
    if fmt != "spice":
        return path
    scan = load_scan(path)
    tmp = write_temp_spec(scan, source_path=path)
    return str(tmp)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: open_in_pymca.py FILE.dat", file=sys.stderr)
        return 2
    path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(path):
        print(f"open_in_pymca: not a file: {path}", file=sys.stderr)
        return 1

    try:
        open_path = _path_for_pymca(path)
    except Exception as exc:
        print(f"open_in_pymca: prepare failed: {exc}", file=sys.stderr)
        return 1

    # Prefer system pymca CLI when available (opens SpecFile scan window).
    pymca_bin = shutil.which("pymca")
    if pymca_bin:
        os.execv(pymca_bin, [pymca_bin, open_path])

    try:
        from PyMca5.PyMcaGui import PyMcaQt as qt
        from PyMca5.PyMcaGui.pymca.PyMcaMain import PyMcaMain
    except ImportError:
        print(
            "open_in_pymca: install PyMca (apt install python3-pymca5) "
            "or ensure `pymca` is on PATH",
            file=sys.stderr,
        )
        return 1

    app = qt.QApplication([])
    win = PyMcaMain()
    win.show()
    win.sourceWidget.sourceSelector.openSource(open_path)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
