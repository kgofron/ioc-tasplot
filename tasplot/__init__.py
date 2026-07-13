"""TAS scan file loading (SPiCE .dat and CERTIF SPEC)."""

from tasplot.combine import CombineResult, combine_curves, parse_scan_list
from tasplot.dataset import FormatError, ScanDataset
from tasplot.export_spec import dataset_to_spec_text, write_temp_spec
from tasplot.load import detect_format, load_scan, load_spec_file
from tasplot.paths import hb3_scan_path

__all__ = [
    "CombineResult",
    "FormatError",
    "ScanDataset",
    "combine_curves",
    "dataset_to_spec_text",
    "detect_format",
    "hb3_scan_path",
    "load_scan",
    "load_spec_file",
    "parse_scan_list",
    "write_temp_spec",
]

__version__ = "0.1.0"
