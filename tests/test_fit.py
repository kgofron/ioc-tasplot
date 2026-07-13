import numpy as np
import pytest

from tasplot.fit import fit_gaussian_bg, gaussian_plus_linear


def test_fit_gaussian_recovers_params():
    rng = np.random.default_rng(0)
    x = np.linspace(-5.0, 5.0, 81)
    true = dict(amp=100.0, cen=1.25, sigma=0.8, slope=0.5, intercept=10.0)
    y = gaussian_plus_linear(x, **true) + rng.normal(0.0, 1.0, size=x.size)
    r = fit_gaussian_bg(x, y)
    assert abs(r.cen - true["cen"]) < 0.05
    assert abs(r.amp - true["amp"]) < 5.0
    assert abs(r.sigma - true["sigma"]) < 0.1
    assert r.npts == 81
    assert r.chi2 > 0
    np.testing.assert_allclose(r.x, x)


def test_fit_rejects_too_few_points():
    with pytest.raises(ValueError, match="at least 5"):
        fit_gaussian_bg([1, 2, 3], [1, 2, 3])


def test_fit_with_roi_window():
    x = np.linspace(0, 20, 201)
    y = gaussian_plus_linear(x, 80.0, 5.0, 0.5, 0.0, 3.0)
    y += gaussian_plus_linear(x, 70.0, 15.0, 0.5, 0.0, 0.0)
    # Full window recovers neither cleanly; ROI finds left peak
    left = fit_gaussian_bg(x, y, x_min=2.0, x_max=8.0)
    assert abs(left.cen - 5.0) < 0.1
    right = fit_gaussian_bg(x, y, x_min=12.0, x_max=18.0)
    assert abs(right.cen - 15.0) < 0.1


def test_fit_bg_nonneg_constant():
    x = np.linspace(-3, 3, 61)
    y = gaussian_plus_linear(x, 40.0, 0.0, 0.7, -2.0, 5.0)  # would want negative bg if free
    r = fit_gaussian_bg(x, y, x_min=-2.0, x_max=2.0, bg_nonneg_at_cen=True)
    assert r.slope == 0.0
    assert r.background_at_cen >= -1e-9
    assert r.intercept >= -1e-9
    x = np.linspace(0, 10, 51)
    y = gaussian_plus_linear(x, 50.0, 4.0, 0.6, 0.0, 2.0)
    err = np.full_like(y, 2.0)
    r = fit_gaussian_bg(x, y, err)
    assert abs(r.cen - 4.0) < 0.05
