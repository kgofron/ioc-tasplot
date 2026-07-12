"""
EPICS PyDevice backend for Graffiti scan plotting.

Invoked from database links, e.g. field(OUT, "@graffiti_plot.acquire()").
Instantiate once from st.cmd: pydev("from graffiti_app import graffiti_plot")
"""

from __future__ import annotations

import math
import os
import re
from typing import Optional, Union

import numpy as np

from tasplot import FormatError, ScanDataset, load_scan, load_spec_file
from tasplot.paths import hb3_scan_path

MAX_WAVEFORM_POINTS = 4000
DATA_FILE_TEXT_MAX = 65536
NORM_NONE = 0
NORM_COLUMN = 1
NORM_FIXED = 2


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
        self._overlay_scan: Optional[ScanDataset] = None
        self._last_error = ""
        self._data_file_text = ""
        self._file_stat: Optional[tuple[int, int]] = None
        self.auto_reload = 0
        self.overlay_enable = 0
        self.overlay_file_number = 0
        self.show_errors = 1
        self.x_col = ""
        self.y_col = ""
        self.norm_mode = NORM_NONE
        self.norm_col = "monitor"
        self.norm_value = 1.0

    def _full_path(self) -> str:
        return self._path_for_scan_number(self.file_number, prefer_explicit=True)

    def _path_for_scan_number(
        self, number: int, *, prefer_explicit: bool = False
    ) -> str:
        if prefer_explicit and self._explicit_file and int(number) == int(self.file_number):
            return self._explicit_file
        if "%04d" in self.file_template:
            name = self.file_template % (
                self.file_name,
                int(number),
                self.file_extension,
            )
        else:
            name = self.file_template % (self.file_name, self.file_extension)
        return os.path.join(self.file_path, name)

    def _update_file_stat(self) -> None:
        path = self._full_path()
        try:
            st = os.stat(path)
            self._file_stat = (st.st_mtime_ns, st.st_size)
        except OSError:
            self._file_stat = None

    def set_file_path(self, path: str) -> None:
        self._explicit_file = None
        self.file_path = path.rstrip("/")

    def set_file_name(self, name: str) -> None:
        self._explicit_file = None
        self.file_name = name

    def set_file_number(self, number: int) -> None:
        self._explicit_file = None
        self.file_number = int(number)
        self._load_scan(preserve_axes=False)

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
        self._load_scan(preserve_axes=False)

    def set_spec_scan_number(self, number: int) -> None:
        self.spec_scan_number = int(number)
        if self.format_rbv() == "spec":
            self._load_scan(preserve_axes=False)

    def set_auto_reload(self, enabled: int) -> None:
        self.auto_reload = 1 if int(enabled) else 0
        if self.auto_reload:
            self._update_file_stat()

    def set_overlay_enable(self, enabled: int) -> None:
        self.overlay_enable = 1 if int(enabled) else 0
        if self.overlay_enable:
            self._load_overlay()
        else:
            self._overlay_scan = None

    def set_overlay_file_number(self, number: int) -> None:
        self.overlay_file_number = int(number)
        if self.overlay_enable:
            self._load_overlay()

    def set_show_errors(self, enabled: int) -> None:
        """Enable Poisson √N error bars on Y (Phoebus err_pv)."""
        self.show_errors = 1 if int(enabled) else 0

    def set_x_col(self, name: str) -> None:
        self.x_col = name.strip()

    def set_y_col(self, name: str) -> None:
        self.y_col = name.strip()

    def set_norm_mode(self, mode: int) -> None:
        self.norm_mode = int(mode)

    def set_norm_col(self, name: str) -> None:
        self.norm_col = name.strip()

    def set_norm_value(self, value: float) -> None:
        self.norm_value = float(value)

    def norm_mode_rbv(self) -> int:
        return int(self.norm_mode)

    def norm_col_rbv(self) -> str:
        return self.norm_col

    def col_headers_rbv(self) -> str:
        if self._scan is None or not self._scan.columns:
            return ""
        return "; ".join(self._scan.columns)

    def x_col_rbv(self) -> str:
        return self.x_col or self.det_x_rbv()

    def y_col_rbv(self) -> str:
        return self.y_col or self.det_y_rbv()

    def plot_axis_label_rbv(self) -> str:
        """Y-axis label for Phoebus xyplot (includes normalization suffix)."""
        y = self.y_col_rbv()
        if not y:
            return ""
        mode = int(self.norm_mode)
        if mode == NORM_COLUMN:
            col = self.norm_col or "monitor"
            return f"{y}/{col}"
        if mode == NORM_FIXED:
            val = float(self.norm_value)
            if val == 1.0:
                return y
            if val == int(val):
                return f"{y}/{int(val)}"
            return f"{y}/{val:g}"
        return y

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
        """Reload current file (Reload button); preserve X/Y if still valid."""
        return self._load_scan(preserve_axes=True)

    def poll_file(self) -> int:
        """If AutoReload on and file mtime/size changed, re-acquire. Returns 1 if reloaded."""
        if not self.auto_reload:
            return 0
        path = self._full_path()
        try:
            st = os.stat(path)
            key = (st.st_mtime_ns, st.st_size)
        except OSError:
            return 0
        if self._file_stat is None:
            self._file_stat = key
            return 0
        if key == self._file_stat:
            return 0
        return self._load_scan(preserve_axes=True)

    def _load_scan(self, *, preserve_axes: bool) -> int:
        """Load scan from configured path (SPiCE or SPEC). Returns 1 on success."""
        path = self._full_path()
        try:
            from tasplot.load import detect_format

            fmt = detect_format(path)
            if fmt == "spec" and self.spec_scan_number is not None:
                self._scan = load_spec_file(path, scan_number=self.spec_scan_number)
            else:
                self._scan = load_scan(path)
            if preserve_axes:
                self._preserve_or_sync_axes()
            else:
                self._sync_axes_from_scan()
            self._last_error = ""
            self._data_file_text = _read_data_file_text(
                path, spec_scan_number=self.spec_scan_number
            )
            self._update_file_stat()
            self._publish_data_file_text()
            if self.overlay_enable:
                self._load_overlay()
            return 1
        except Exception as exc:
            self._scan = None
            self.x_col = ""
            self.y_col = ""
            self._data_file_text = ""
            self._file_stat = None
            self._last_error = str(exc)
            self._publish_data_file_text()
            return 0

    def load_hb3(self, experiment: int, scan: int) -> int:
        """Convenience: HB3 User tree layout."""
        path = hb3_scan_path(self.file_path, experiment, scan)
        self.set_selected_file(path)
        return 1 if self._scan is not None else 0

    def _load_overlay(self) -> int:
        """Load overlay scan from OverlayFileNumber in the same directory."""
        if not self.overlay_enable or self.overlay_file_number <= 0:
            self._overlay_scan = None
            return 0
        path = self._path_for_scan_number(self.overlay_file_number)
        try:
            from tasplot.load import detect_format

            fmt = detect_format(path)
            if fmt == "spec" and self.spec_scan_number is not None:
                self._overlay_scan = load_spec_file(
                    path, scan_number=self.spec_scan_number
                )
            else:
                self._overlay_scan = load_scan(path)
            return 1
        except Exception as exc:
            self._overlay_scan = None
            self._last_error = f"overlay: {exc}"
            return 0

    def _publish_data_file_text(self) -> None:
        """Notify DataFileText waveform (I/O Intr; avoids Phoebus scroll reset)."""
        try:
            import pydev

            pydev.iointr("data_file_text", self.data_file_text())
        except Exception:
            pass

    def data_file_text(self) -> list[int]:
        """CHAR waveform text (pcaspy SpecFile pattern) for Phoebus multi-line display."""
        text = self._data_file_text
        if not text:
            path = self._full_path()
            if os.path.isfile(path) and os.access(path, os.R_OK):
                text = _read_data_file_text(
                    path, spec_scan_number=self.spec_scan_number
                )
        return _encode_text_waveform(text, DATA_FILE_TEXT_MAX)

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

    def _preserve_or_sync_axes(self) -> None:
        """Keep user X/Y on reload when columns still exist; else take file defaults."""
        if self._scan is None:
            return
        cols = {c.lower(): c for c in self._scan.columns}
        if self.x_col and self.x_col.lower() in cols:
            self.x_col = cols[self.x_col.lower()]
        else:
            self.x_col = self._scan.default_x or (
                self._scan.columns[0] if self._scan.columns else ""
            )
        if self.y_col and self.y_col.lower() in cols:
            self.y_col = cols[self.y_col.lower()]
        else:
            self.y_col = self._scan.default_y or (
                self._scan.columns[-1] if self._scan.columns else ""
            )

    def _resolve_column(self, name: str) -> str:
        return _resolve_column_name(self._require_scan(), name)

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

    def overlay_xdata(self) -> list[float]:
        if not self.overlay_enable or self._overlay_scan is None:
            return _empty_waveform()
        try:
            col = _resolve_column_name(
                self._overlay_scan, self.x_col or self._overlay_scan.default_x or ""
            )
            return _clip_waveform(self._overlay_scan.column(col))
        except (KeyError, ValueError):
            return _empty_waveform()

    def overlay_ydata(self) -> list[float]:
        y, _ = self._overlay_ydata_and_errors()
        return y if y else _empty_waveform()

    def overlay_ydata_err(self) -> list[float]:
        if not self.show_errors:
            return _empty_waveform()
        _, err = self._overlay_ydata_and_errors()
        return err if err else _empty_waveform()

    def _ydata_and_errors(self) -> tuple[list[float], list[float]]:
        if self._scan is None:
            return _empty_waveform(), _empty_waveform()
        try:
            scan = self._scan
            col = _resolve_column_name(scan, self.y_col or scan.default_y or "")
            y = scan.column(col)
            err = scan.poisson_errors(y_column=col)
            y, err = _apply_normalization(
                y,
                err,
                int(self.norm_mode),
                scan,
                self.norm_col,
                self.norm_value,
                lambda n: _resolve_column_name(scan, n),
            )
            return _clip_waveform(y), _clip_waveform(err)
        except (KeyError, ValueError):
            return _empty_waveform(), _empty_waveform()

    def _overlay_ydata_and_errors(self) -> tuple[list[float], list[float]]:
        if not self.overlay_enable or self._overlay_scan is None:
            return [], []
        try:
            scan = self._overlay_scan
            col = _resolve_column_name(scan, self.y_col or scan.default_y or "")
            y = scan.column(col)
            err = scan.poisson_errors(y_column=col)
            y, err = _apply_normalization(
                y,
                err,
                int(self.norm_mode),
                scan,
                self.norm_col,
                self.norm_value,
                lambda n: _resolve_column_name(scan, n),
            )
            return _clip_waveform(y), _clip_waveform(err)
        except (KeyError, ValueError):
            return [], []

    def xdata(self) -> list[float]:
        if self._scan is None:
            return _empty_waveform()
        try:
            col = self._resolve_column(self.x_col or self._scan.default_x or "")
            return _clip_waveform(self._scan.column(col))
        except (KeyError, ValueError):
            return _empty_waveform()

    def ydata(self) -> list[float]:
        y, _ = self._ydata_and_errors()
        return y

    def ydata_err(self) -> list[float]:
        if not self.show_errors:
            return _empty_waveform()
        _, err = self._ydata_and_errors()
        return err

    def column(self, name: str) -> list[float]:
        return _clip_waveform(self._require_scan().column(name))


_SCAN_START = re.compile(r"^#S\s+(\d+)\b")


def _resolve_column_name(scan: ScanDataset, name: str) -> str:
    if not name:
        raise KeyError("column name is empty")
    if name in scan.columns:
        return name
    lower_map = {col.lower(): col for col in scan.columns}
    resolved = lower_map.get(name.lower())
    if resolved is None:
        raise KeyError(name)
    return resolved


def _apply_normalization(
    y: np.ndarray,
    err: np.ndarray,
    mode: int,
    scan: ScanDataset,
    norm_col: str,
    norm_value: float,
    resolve_column,
) -> tuple[np.ndarray, np.ndarray]:
    """SPiCE-style Y normalization: none, divide by column, or fixed value."""
    if mode == NORM_NONE:
        return y, err
    if mode == NORM_COLUMN:
        col = resolve_column(norm_col or "monitor")
        divisor = scan.column(col)
        return _divide_by(divisor, y, err)
    if mode == NORM_FIXED:
        divisor = float(norm_value)
        if divisor <= 0:
            return y, err
        return y / divisor, err / divisor
    return y, err


def _divide_by(
    divisor: Union[np.ndarray, float], y: np.ndarray, err: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    out_y = np.zeros_like(y, dtype=float)
    out_err = np.zeros_like(err, dtype=float)
    if isinstance(divisor, np.ndarray):
        valid = divisor > 0
        out_y[valid] = y[valid] / divisor[valid]
        out_err[valid] = err[valid] / divisor[valid]
    else:
        out_y = y / divisor
        out_err = err / divisor
    return out_y, out_err


def _encode_text_waveform(text: str, max_bytes: int) -> list[int]:
    if not text:
        return [0]
    data = text.encode("utf-8", errors="replace")[:max_bytes]
    return list(data) if data else [0]


def _read_data_file_text(
    path: str,
    spec_scan_number: Optional[int] = None,
) -> str:
    """Read file text for CHAR waveform, truncated to DATAFILETEXT NELM."""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            lines = [line.rstrip("\n\r") for line in handle.readlines()]
    except OSError as exc:
        return str(exc)

    try:
        from tasplot.load import detect_format

        fmt = detect_format(path)
    except (FormatError, OSError):
        fmt = "unknown"

    if fmt == "spec":
        text = _read_spec_file_text(lines, spec_scan_number)
    else:
        text = "\n".join(lines)

    return _truncate_data_file_text(text)


def _read_spec_file_text(lines: list[str], scan_number: Optional[int]) -> str:
    """Whole SPEC file, or one scan block when scan_number is set."""
    if scan_number is None:
        return "\n".join(lines)

    scan_start = _find_spec_scan_start(lines, scan_number)
    if scan_start is None:
        return "\n".join(lines)

    out: list[str] = []
    for raw in lines[:scan_start]:
        if raw.strip().startswith("#"):
            out.append(raw)

    for i in range(scan_start, len(lines)):
        raw = lines[i]
        if i > scan_start and _SCAN_START.match(raw.strip()):
            break
        out.append(raw)

    return "\n".join(out)


def _truncate_data_file_text(
    text: str, max_bytes: int = DATA_FILE_TEXT_MAX
) -> str:
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= max_bytes:
        return text
    note = "\n… (truncated)"
    keep = max(0, max_bytes - len(note.encode("utf-8")))
    return encoded[:keep].decode("utf-8", errors="ignore") + note


def _find_spec_scan_start(lines: list[str], scan_number: Optional[int]) -> Optional[int]:
    last_match: Optional[int] = None
    for i, raw in enumerate(lines):
        match = _SCAN_START.match(raw.strip())
        if not match:
            continue
        if scan_number is None or int(match.group(1)) == scan_number:
            last_match = i
    return last_match


def _empty_waveform() -> list[float]:
    """Full-NELM NaN trace so disabled/empty overlays do not inject log(0) zeros."""
    return [float("nan")] * MAX_WAVEFORM_POINTS


def _clip_waveform(arr) -> list[float]:
    """Return up to MAX_WAVEFORM_POINTS; pad with NaN.

    PyDevice copies only ``len(result)`` into the waveform buffer and sets NORD,
    but some CA/Phoebus paths still observe the full NELM buffer. Trailing zeros
    from record init break Log X/Y (log(0) → ~1E-323). NaN padding keeps NORD
    aligned with NELM for those clients and is skipped by Phoebus xyplot.
    """
    data = [float(v) for v in arr]
    if len(data) > MAX_WAVEFORM_POINTS:
        return data[:MAX_WAVEFORM_POINTS]
    if len(data) == 0:
        return _empty_waveform()
    if len(data) < MAX_WAVEFORM_POINTS:
        data = data + [float("nan")] * (MAX_WAVEFORM_POINTS - len(data))
    return data


# Singleton for PyDevice @graffiti_plot.*
graffiti_plot = GraffitiPlotEngine()
