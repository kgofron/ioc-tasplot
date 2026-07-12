#!/usr/bin/env python3
"""Open a scan file in PyMca for peak fit / overlay (optional Phase 6 path).

Requires ``python3-pymca5`` / PyMca5, or a ``pymca`` binary on PATH.
"""
from __future__ import annotations

import os
import shutil
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: open_in_pymca.py FILE.dat", file=sys.stderr)
        return 2
    path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(path):
        print(f"open_in_pymca: not a file: {path}", file=sys.stderr)
        return 1

    # Prefer system pymca CLI when available (opens SpecFile scan window).
    pymca_bin = shutil.which("pymca")
    if pymca_bin:
        os.execv(pymca_bin, [pymca_bin, path])

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
    win.sourceWidget.sourceSelector.openSource(path)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
