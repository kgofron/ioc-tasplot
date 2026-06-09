from pathlib import Path

from graffiti_app import NORM_COLUMN, NORM_FIXED, NORM_NONE, GraffitiPlotEngine

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
    assert eng.nrows_rbv() >= 10
    assert eng.format_rbv() == "spice"


def test_set_file_number_rebuilds_template_path():
    eng = GraffitiPlotEngine()
    eng.set_selected_file(str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"))
    eng.file_template = "%s%s"
    eng.file_extension = ".dat"
    eng.set_file_number(0)
    assert eng.full_file_name_rbv() == str(
        FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"
    )


def test_set_file_number_auto_acquires_hb3_scan():
    if not HB3_USER.is_dir():
        return
    data = HB3_USER / "exp382" / "Datafiles"
    if not (data / "HB3_exp0382_scan0001.dat").is_file():
        return
    eng = GraffitiPlotEngine()
    eng.set_selected_file(str(data / "HB3_exp0382_scan0001.dat"))
    rows1 = eng.nrows_rbv()
    eng.set_file_number(2)
    assert "scan0002.dat" in eng.full_file_name_rbv()
    assert eng.nrows_rbv() != rows1


def test_normalize_to_monitor_column():
    eng = GraffitiPlotEngine()
    path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    eng.set_selected_file(path)
    raw = eng.ydata()
    eng.set_norm_mode(NORM_COLUMN)
    eng.set_norm_col("monitor")
    norm = eng.ydata()
    assert raw != norm
    assert len(norm) == len(raw)
    scan = eng._scan
    monitor = scan.column("monitor")
    for r, n, m in zip(raw, norm, monitor):
        if m > 0:
            assert abs(r / m - n) < 1e-6
    assert eng.plot_axis_label_rbv() == "detector/monitor"


def test_normalize_to_fixed_value():
    eng = GraffitiPlotEngine()
    eng.set_selected_file(str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"))
    eng.set_norm_mode(NORM_FIXED)
    eng.set_norm_value(1000.0)
    norm = eng.ydata()
    raw = eng._scan.column("detector")
    for r, n in zip(raw[:5], norm[:5]):
        assert abs(float(r) / 1000.0 - n) < 1e-6
    assert eng.plot_axis_label_rbv() == "detector/1000"


def test_normalize_none_matches_raw():
    eng = GraffitiPlotEngine()
    eng.set_selected_file(str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"))
    eng.set_norm_mode(NORM_NONE)
    y1 = eng.ydata()
    eng.set_norm_mode(NORM_COLUMN)
    eng.set_norm_col("monitor")
    eng.set_norm_mode(NORM_NONE)
    y2 = eng.ydata()
    assert y1 == y2
    assert eng.plot_axis_label_rbv() == "detector"


def test_set_y_col_changes_plot_data():
    eng = GraffitiPlotEngine()
    path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    eng.set_selected_file(path)
    y_det = eng.ydata()
    eng.set_y_col("time")
    y_time = eng.ydata()
    assert y_det != y_time
    assert len(y_time) == eng.nrows_rbv()
    assert eng.col_headers_rbv()
    assert "detector" in eng.col_headers_rbv()
    assert eng.x_col_rbv() == "s1"
    assert eng.y_col_rbv() == "time"


def test_full_file_name_text_waveform():
    eng = GraffitiPlotEngine()
    path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    eng.set_selected_file(path)
    blob = bytes(eng.full_file_name_text()).decode("utf-8", errors="replace")
    assert path in blob
    assert len(eng.full_file_name_text()) <= 512


def test_col_headers_text_waveform():
    eng = GraffitiPlotEngine()
    eng.set_selected_file(str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat"))
    blob = bytes(eng.col_headers_text()).decode("utf-8", errors="replace")
    assert "detector" in blob
    assert "s1" in blob


def test_data_file_text_spice_full_file():
    eng = GraffitiPlotEngine()
    path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    eng.set_selected_file(path)
    blob = bytes(eng.data_file_text()).decode("utf-8", errors="replace")
    assert "# scan = 1" in blob
    assert "# def_x = s1" in blob
    assert "# def_y = detector" in blob
    assert "Pt." in blob
    assert "126.4328" in blob
    assert "scan completed" in blob
    assert len(eng.data_file_text()) <= 65536


def test_selected_file_path_waveform_read_write():
    eng = GraffitiPlotEngine()
    path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    eng.set_selected_file(path)
    blob = bytes(eng.selected_file_path()).decode("utf-8", errors="replace")
    assert path in blob or path.endswith(blob.strip("\x00"))
    eng.selected_file_path(val=list(path.encode("utf-8")), tpro=1)
    assert eng.full_file_name_rbv() == path


def test_command_text_waveform():
    eng = GraffitiPlotEngine()
    path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    eng.set_selected_file(path)
    eng.acquire()
    blob = bytes(eng.command_text()).decode("utf-8", errors="replace")
    assert "scan" in blob.lower()


def test_data_file_text_empty_without_scan():
    eng = GraffitiPlotEngine()
    eng.file_path = "/nonexistent"
    eng.file_name = "missing"
    assert eng.data_file_text() == [0]


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
    blob = bytes(eng.data_file_text()).decode("utf-8", errors="replace")
    assert "#S 2" in blob
    assert "#L" in blob
    assert "Detector" in blob
