"""TAS scan file loading (SPiCE .dat and CERTIF SPEC)."""

from tasplot.dataset import FormatError, ScanDataset
from tasplot.load import detect_format, load_scan, load_spec_file
from tasplot.paths import hb3_scan_path

__all__ = [
    "FormatError",
    "ScanDataset",
    "detect_format",
    "load_scan",
    "load_spec_file",
    "hb3_scan_path",
]

__version__ = "0.1.0"
