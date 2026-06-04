from pathlib import Path

from graffiti_app import GraffitiPlotEngine

FIXTURES = Path(__file__).parent / "fixtures"
HB3_USER = Path("/home/kg1/Documents/Detector/HB3/HB3_data/User")


def test_acquire_spice_fixture():
    eng = GraffitiPlotEngine()
    eng.set_file_path(str(FIXTURES))
    eng.set_file_name("spice_hb3_exp0382_scan0001_head")
    eng.set_file_number(0)
    eng.file_extension = ".dat"
    eng.file_template = "%s%s"
    assert eng.acquire() == 1
    assert eng.format_rbv() == "spice"
    assert eng.nrows_rbv() >= 10
    x = eng.xdata()
    y = eng.ydata()
    assert len(x) == len(y) == eng.nrows_rbv()


def test_acquire_spec_fixture():
    eng = GraffitiPlotEngine()
    eng.set_file_path(str(FIXTURES))
    eng.set_file_name("spec_yongcai_sample")
    eng.file_number = 0
    eng.file_extension = ".spec"
    eng.file_template = "%s%s"
    eng.set_spec_scan_number(2)
    assert eng.acquire() == 1
    assert eng.format_rbv() == "spec"
    assert eng.nrows_rbv() == 11
    assert eng.det_y_rbv() == "Detector"
