"""SPiCE → SPEC export for PyMca SpecFile."""

from pathlib import Path

import pytest

from tasplot import load_scan
from tasplot.export_spec import dataset_to_spec_text, write_temp_spec
from tasplot.load import detect_format
from tasplot.spec import parse_spec_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_spice_to_spec_preserves_columns_and_data():
    spice = load_scan(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    text = dataset_to_spec_text(spice)
    assert text.startswith("#F ")
    assert "#S " in text
    assert "#L " in text
    assert "  s1  " in text or text.split("#L ", 1)[1].splitlines()[0].startswith("Pt.")
    assert "detector" in text

    tmp = write_temp_spec(spice)
    try:
        assert detect_format(tmp) == "spec"
        back = parse_spec_file(tmp)
        assert back.columns == spice.columns
        assert back.nrows == spice.nrows
        assert back.column("detector")[0] == pytest.approx(spice.column("detector")[0])
        assert back.column("s1")[0] == pytest.approx(spice.column("s1")[0])
    finally:
        tmp.unlink(missing_ok=True)


def test_open_in_pymca_path_helper_converts_spice_only(tmp_path, monkeypatch):
    # Import helper from scripts/ without requiring pymca GUI.
    import importlib.util

    script = (
        Path(__file__).resolve().parents[1]
        / "plotApp"
        / "op"
        / "scripts"
        / "open_in_pymca.py"
    )
    spec = importlib.util.spec_from_file_location("open_in_pymca", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    spice_path = str(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    out = mod._path_for_pymca(spice_path)
    assert out != spice_path
    assert out.endswith(".spec")
    assert detect_format(out) == "spec"
    Path(out).unlink(missing_ok=True)
