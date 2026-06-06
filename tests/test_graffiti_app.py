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


def test_set_selected_file_parses_hb3_scan():
    eng = GraffitiPlotEngine()
    eng.set_selected_file("/data/exp382/HB3_exp0382_scan0003.dat")
    assert eng.file_path == "/data/exp382"
    assert eng.file_name == "HB3_exp0382_scan"
    assert eng.file_number == 3
    assert eng.full_file_name_rbv() == "/data/exp382/HB3_exp0382_scan0003.dat"


def test_set_selected_file_acquire_fixture():
    eng = GraffitiPlotEngine()
    path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    eng.set_selected_file(path)
    assert eng.full_file_name_rbv() == path
    assert eng.acquire() == 1


def test_set_file_number_rebuilds_template_path():
    eng = GraffitiPlotEngine()
    eng.set_selected_file(str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"))
    eng.file_template = "%s%s"
    eng.file_extension = ".dat"
    eng.set_file_number(0)
    assert eng.full_file_name_rbv() == str(
        FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"
    )


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
