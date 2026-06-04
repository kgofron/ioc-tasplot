"""Cross-format checks for concurrent SPiCE + SPEC support."""

from pathlib import Path

from tasplot import ScanDataset, load_scan

FIXTURES = Path(__file__).parent / "fixtures"


def _assert_common_api(scan: ScanDataset) -> None:
    assert scan.format in ("spice", "spec")
    assert scan.columns
    assert scan.default_x in scan.columns
    assert scan.default_y in scan.columns
    x = scan.axis(scan.default_x)
    y = scan.axis(scan.default_y)
    err = scan.poisson_errors()
    assert len(x) == scan.nrows
    assert len(y) == scan.nrows
    assert len(err) == scan.nrows
    s = scan.summary()
    assert s["format"] == scan.format


def test_spice_and_spec_share_api():
    spice = load_scan(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    spec = load_scan(FIXTURES / "spec_yongcai_sample.spec")
    _assert_common_api(spice)
    _assert_common_api(spec)
    assert spice.format != spec.format
