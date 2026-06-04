from pathlib import Path

import pytest

from tasplot import detect_format, load_scan, load_spec_file
from tasplot.spec import list_spec_scans

FIXTURES = Path(__file__).parent / "fixtures"
YONG_CAI = Path("/home/kg1/Documents/src/PyMCA/YongCai/20240530")


def test_detect_spec():
    p = FIXTURES / "spec_yongcai_sample.spec"
    assert detect_format(p) == "spec"


def test_parse_yongcai_fixture_scan2():
    scan = load_spec_file(FIXTURES / "spec_yongcai_sample.spec", scan_number=2)
    assert scan.format == "spec"
    assert scan.scan_number == 2
    assert "ascan" in (scan.command or "")
    assert scan.default_x == "UGap"
    assert scan.default_y == "Detector"
    assert scan.nrows == 11
    assert scan.ncols == 47
    ugap = scan.column("UGap")
    assert ugap[0] == pytest.approx(23536.0)
    det = scan.column("Detector")
    assert det[0] == pytest.approx(0.0)


def test_spec_scan1_aborted_zero_points():
    scan = load_spec_file(FIXTURES / "spec_yongcai_sample.spec", scan_number=1)
    assert scan.scan_number == 1
    assert scan.nrows == 0
    assert "aborted" in scan.meta.get("comments", "").lower()


def test_load_scan_auto_spec():
    scan = load_scan(FIXTURES / "spec_yongcai_sample.spec")
    assert scan.format == "spec"
    assert scan.scan_number == 2


def test_list_spec_scans_fixture():
    summary = list_spec_scans(FIXTURES / "spec_yongcai_sample.spec")
    assert len(summary) == 2
    assert summary[0]["nrows"] == 0
    assert summary[1]["nrows"] == 11


@pytest.mark.skipif(not YONG_CAI.exists(), reason="Yong Cai SPEC file not on disk")
def test_yongcai_full_file_many_scans():
    summary = list_spec_scans(YONG_CAI)
    assert len(summary) > 10
    first_with_data = next(s for s in summary if s["nrows"] > 0)
    scan = load_spec_file(YONG_CAI, scan_number=first_with_data["scan_number"])
    assert scan.nrows == first_with_data["nrows"]
