from pathlib import Path

import pytest

from tasplot import FormatError, detect_format, load_scan
from tasplot.paths import hb3_scan_path

FIXTURES = Path(__file__).parent / "fixtures"
HB3_USER = Path("/home/kg1/Documents/Detector/HB3/HB3_data/User")


def test_detect_spice():
    p = FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"
    assert detect_format(p) == "spice"


def test_parse_spice_fixture():
    scan = load_scan(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    assert scan.format == "spice"
    assert scan.scan_number == 1
    assert scan.default_x == "s1"
    assert scan.default_y == "detector"
    assert "detector" in scan.columns
    assert scan.nrows >= 10
    y = scan.column("detector")
    assert y[0] == pytest.approx(13428.0)


@pytest.mark.skipif(
    not (HB3_USER / "exp382/Datafiles/HB3_exp0382_scan0001.dat").exists(),
    reason="HB3 archive not on this machine",
)
def test_hb3_full_scan_on_disk():
    path = hb3_scan_path(str(HB3_USER), 382, 1)
    scan = load_scan(path)
    assert scan.nrows > 50
    assert "h" in scan.columns and "k" in scan.columns


def test_hb3_path_helper():
    assert hb3_scan_path("/data/User", 382, 1).endswith(
        "exp382/Datafiles/HB3_exp0382_scan0001.dat"
    )
