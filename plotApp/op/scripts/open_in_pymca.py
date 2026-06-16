#!/usr/bin/env python3
"""Open a scan file in PyMca (optional; requires python3-pymca5 / PyMca5)."""
from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: open_in_pymca.py FILE.dat", file=sys.stderr)
        return 2
    path = sys.argv[1]
    try:
        from PyMca5.PyMcaGui import PyMcaQt as qt
        from PyMca5.PyMcaGui.pymca.PyMcaMain import PyMcaMain
    except ImportError:
        print(
            "open_in_pymca: PyMca5 not installed (try: apt install python3-pymca5)",
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
