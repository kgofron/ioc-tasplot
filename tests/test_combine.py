"""Tests for SpICE-style scan combine."""

from pathlib import Path

import numpy as np
import pytest

from tasplot.combine import (
    CombineCurve,
    combine_curves,
    curve_from_scan,
    parse_scan_list,
)
from tasplot import load_scan

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_scan_list():
    assert parse_scan_list("1, 2,5") == [1, 2, 5]
    assert parse_scan_list("1 3;4") == [1, 3, 4]
    assert parse_scan_list("") == []
    assert parse_scan_list("0,1") == [1]


def test_combine_exact_add_subtract():
    x = np.array([1.0, 2.0, 3.0])
    a = CombineCurve(x=x, y=np.array([10.0, 20.0, 30.0]), weight=np.array([2.0, 2.0, 2.0]), sign=1)
    b = CombineCurve(x=x, y=np.array([4.0, 4.0, 4.0]), weight=np.array([2.0, 2.0, 2.0]), sign=-1)
    r = combine_curves([a, b], bin_tol=0.0, norm_value=2.0)
    # (10-4)/(2+2)*2 = 3, etc.
    assert r.y[0] == pytest.approx(3.0)
    assert r.y[1] == pytest.approx(8.0)
    assert r.err[0] == pytest.approx(np.sqrt(14.0) / 4.0 * 2.0)


def test_combine_binned_merges_nearby_x():
    a = CombineCurve(
        x=np.array([1.000, 2.000]),
        y=np.array([100.0, 200.0]),
        weight=np.array([10.0, 10.0]),
        sign=1,
    )
    b = CombineCurve(
        x=np.array([1.002, 2.001]),
        y=np.array([50.0, 50.0]),
        weight=np.array([10.0, 10.0]),
        sign=1,
    )
    r = combine_curves([a, b], bin_tol=0.01, norm_value=1.0)
    assert len(r.x) == 2
    # First bin: y=(100+50)/(10+10)=7.5
    assert r.y[0] == pytest.approx(7.5)


def test_combine_from_spice_fixture():
    scan = load_scan(FIXTURES / "spice_hb3_exp0382_scan0001_head.dat")
    c = curve_from_scan(scan, x_col="s1", y_col="detector", weight_col="monitor", sign=1)
    r = combine_curves([c], bin_tol=0.05, norm_value=1.0)
    assert len(r.x) == len(r.y) == len(r.err)
    assert len(r.x) >= 1
    assert np.all(np.isfinite(r.y))
