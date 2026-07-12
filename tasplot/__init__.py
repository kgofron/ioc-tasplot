"""TAS scan file loading (SPiCE .dat and CERTIF SPEC)."""

from tasplot.dataset import FormatError, ScanDataset
from tasplot.export_spec import dataset_to_spec_text, write_temp_spec
from tasplot.load import detect_format, load_scan, load_spec_file
from tasplot.paths import hb3_scan_path

__all__ = [
    "FormatError",
    "ScanDataset",
    "dataset_to_spec_text",
    "detect_format",
    "hb3_scan_path",
    "load_scan",
    "load_spec_file",
    "write_temp_spec",
]

__version__ = "0.1.0"
