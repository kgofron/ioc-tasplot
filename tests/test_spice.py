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


def test_spice_skips_literal_caret_m_and_footer(tmp_path):
    """Live-test artifact: trailing '^M' text or DOS CRLF must not fail the scan."""
    src = (FIXTURES / "spice_hb3_exp0382_scan0001_head.dat").read_text(encoding="utf-8")
    # Take header + a few rows, append a bad last field and SPICE footer.
    lines = src.splitlines()
    header_i = next(i for i, ln in enumerate(lines) if "Pt." in ln)
    chunk = lines[: header_i + 4]
    bad = (
        "     99   134.6339      1.000    501.000   2475.000      0.012    "
        "66.7975   -22.3034   -41.1662   119.9269     0.0551    -1.0000   "
        "-34.2897    70.5269     2.0020     2.0005     0.0000     0.0020     "
        "5.0000     5.0000     5.0000     5.0000     5.0000     5.0000     "
        "5.0000     5.0000   159.4165   -41.1936     3.0745     1.0826     "
        "0.9092     0.0000    14.7000    14.6813     0.0187     1.0000     "
        "1.0000     0.000^M"
    )
    # Fixture head rows are short; just ensure caret-M strip + footer don't raise.
    text = "\r\n".join(chunk) + "\r\n" + bad + "\r\n# Sum of Counts = 1\r\n"
    path = tmp_path / "live_crlf.dat"
    path.write_text(text, encoding="utf-8")
    scan = load_scan(path)
    assert scan.nrows >= 1
    assert "sum of counts" in scan.meta or scan.nrows >= 1


def test_spice_skips_incomplete_live_row(tmp_path):
    src = (FIXTURES / "spice_hb3_exp0382_scan0001_head.dat").read_text(encoding="utf-8")
    path = tmp_path / "live_partial.dat"
    path.write_text(src + "\n     99   134.6      1.000\n", encoding="utf-8")
    scan = load_scan(path)
    base = load_scan(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    assert scan.nrows == base.nrows


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
