"""
EPICS PyDevice backend for Graffiti scan plotting.

Invoked from database links, e.g. field(OUT, "@graffiti_plot.acquire()").
Instantiate once from st.cmd: pydev("from graffiti_app import graffiti_plot")
"""

from __future__ import annotations

import math
import os
import re
from typing import Optional

from tasplot import FormatError, ScanDataset, load_scan, load_spec_file
from tasplot.paths import hb3_scan_path

MAX_WAVEFORM_POINTS = 4000


class GraffitiPlotEngine:
    """Holds last-loaded scan and file-selection state for PyDevice records."""

    def __init__(self) -> None:
        self.file_path = "/home/kg1/Documents/Detector/HB3/HB3_data/User"
        self.file_name = "HB3_exp0382_scan"
        self.file_number = 1
        self.file_extension = ".dat"
        self.file_template = "%s%04d%s"
        self.spec_scan_number: Optional[int] = None
        self._explicit_file: Optional[str] = None
        self._scan: Optional[ScanDataset] = None
        self._last_error = ""
        self.x_col = ""
        self.y_col = ""

    def _full_path(self) -> str:
        if self._explicit_file:
            return self._explicit_file
        if "%04d" in self.file_template:
            name = self.file_template % (
                self.file_name,
                int(self.file_number),
                self.file_extension,
            )
        else:
            name = self.file_template % (self.file_name, self.file_extension)
        return os.path.join(self.file_path, name)

    def set_file_path(self, path: str) -> None:
        self._explicit_file = None
        self.file_path = path.rstrip("/")

    def set_file_name(self, name: str) -> None:
        self._explicit_file = None
        self.file_name = name

    def set_file_number(self, number: int) -> None:
        self._explicit_file = None
        self.file_number = int(number)
        self.acquire()

    def set_selected_file(self, path: str) -> None:
        """Set full file path from Phoebus FileSelector or text entry."""
        path = path.strip()
        if not path:
            self._explicit_file = None
            return
        if os.path.isdir(path):
            self._explicit_file = None
            self.file_path = path.rstrip("/")
            return
        self._explicit_file = path
        self.file_path = os.path.dirname(path)
        base, ext = os.path.splitext(os.path.basename(path))
        if ext:
            self.file_extension = ext
        match = re.match(r"^(.+_scan)(\d+)$", base) or re.match(r"^(.+?)(\d+)$", base)
        if match:
            self.file_name = match.group(1)
            self.file_number = int(match.group(2))
        else:
            self.file_name = base
        self.acquire()

    def set_spec_scan_number(self, number: int) -> None:
        self.spec_scan_number = int(number)
        if self.format_rbv() == "spec":
            self.acquire()

    def set_x_col(self, name: str) -> None:
        self.x_col = name.strip()

    def set_y_col(self, name: str) -> None:
        self.y_col = name.strip()

    def col_headers_rbv(self) -> str:
        if self._scan is None or not self._scan.columns:
            return ""
        return "; ".join(self._scan.columns)

    def x_col_rbv(self) -> str:
        return self.x_col or self.det_x_rbv()

    def y_col_rbv(self) -> str:
        return self.y_col or self.det_y_rbv()

    def plot_axis_label_rbv(self) -> str:
        """Y-axis label for Phoebus (normalization suffix in Phase 2)."""
        return self.y_col_rbv()

    def full_file_name_rbv(self) -> str:
        return self._full_path()

    def file_exists_rbv(self) -> int:
        p = self._full_path()
        return 1 if os.path.isfile(p) and os.access(p, os.R_OK) else 0

    def format_rbv(self) -> str:
        if self._scan is not None:
            return self._scan.format
        try:
            from tasplot.load import detect_format

            return detect_format(self._full_path())
        except (FormatError, OSError):
            return "unknown"

    def acquire(self) -> int:
        """Load scan from configured path (SPiCE or SPEC). Returns 1 on success."""
        path = self._full_path()
        try:
            from tasplot.load import detect_format

            fmt = detect_format(path)
            if fmt == "spec" and self.spec_scan_number is not None:
                self._scan = load_spec_file(path, scan_number=self.spec_scan_number)
            else:
                self._scan = load_scan(path)
            self._sync_axes_from_scan()
            self._last_error = ""
            return 1
        except Exception as exc:
            self._scan = None
            self.x_col = ""
            self.y_col = ""
            self._last_error = str(exc)
            return 0

    def load_hb3(self, experiment: int, scan: int) -> int:
        """Convenience: HB3 User tree layout."""
        path = hb3_scan_path(self.file_path, experiment, scan)
        self.file_extension = ".dat"
        self.spec_scan_number = None
        try:
            self._scan = load_scan(path)
            self._sync_axes_from_scan()
            self._last_error = ""
            return 1
        except Exception as exc:
            self._scan = None
            self.x_col = ""
            self.y_col = ""
            self._last_error = str(exc)
            return 0

    def _require_scan(self) -> ScanDataset:
        if self._scan is None:
            raise RuntimeError(self._last_error or "no scan loaded; browse or reload")
        return self._scan

    def _sync_axes_from_scan(self) -> None:
        if self._scan is None:
            return
        scan = self._scan
        self.x_col = scan.default_x or (scan.columns[0] if scan.columns else "")
        self.y_col = scan.default_y or (scan.columns[-1] if scan.columns else "")

    def _resolve_column(self, name: str) -> str:
        scan = self._require_scan()
        if not name:
            raise KeyError("column name is empty")
        if name in scan.columns:
            return name
        lower_map = {col.lower(): col for col in scan.columns}
        resolved = lower_map.get(name.lower())
        if resolved is None:
            raise KeyError(name)
        return resolved

    def nrows_rbv(self) -> int:
        if self._scan is None:
            return 0
        return self._scan.nrows

    def ncolumns_rbv(self) -> int:
        if self._scan is None:
            return 0
        return self._scan.ncols

    def det_x_rbv(self) -> str:
        if self._scan is None:
            return ""
        return self._scan.default_x or ""

    def det_y_rbv(self) -> str:
        if self._scan is None:
            return ""
        return self._scan.default_y or ""

    def scan_number_rbv(self) -> int:
        if self._scan is None:
            return 0
        s = self._scan.scan_number
        return int(s) if s is not None else 0

    def command_rbv(self) -> str:
        if self._scan is None:
            return ""
        return self._scan.command or ""

    def last_error_rbv(self) -> str:
        return self._last_error

    def xdata(self) -> list[float]:
        if self._scan is None:
            return []
        try:
            col = self._resolve_column(self.x_col or self._scan.default_x or "")
            return _clip_waveform(self._scan.column(col))
        except (KeyError, ValueError):
            return []

    def ydata(self) -> list[float]:
        if self._scan is None:
            return []
        try:
            col = self._resolve_column(self.y_col or self._scan.default_y or "")
            return _clip_waveform(self._scan.column(col))
        except (KeyError, ValueError):
            return []

    def ydata_err(self) -> list[float]:
        if self._scan is None:
            return []
        try:
            col = self._resolve_column(self.y_col or self._scan.default_y or "")
            err = self._scan.poisson_errors(y_column=col)
            return _clip_waveform(err)
        except (KeyError, ValueError):
            return []

    def column(self, name: str) -> list[float]:
        return _clip_waveform(self._require_scan().column(name))


def _clip_waveform(arr) -> list[float]:
    data = [float(v) for v in arr]
    if len(data) > MAX_WAVEFORM_POINTS:
        return data[:MAX_WAVEFORM_POINTS]
    return data


# Singleton for PyDevice @graffiti_plot.*
graffiti_plot = GraffitiPlotEngine()
