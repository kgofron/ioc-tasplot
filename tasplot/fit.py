"""1D peak fit: Gaussian + linear background (control-room MVP)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

try:
    from scipy.optimize import curve_fit
except ImportError:  # pragma: no cover - exercised when scipy absent
    curve_fit = None  # type: ignore[assignment]


@dataclass
class FitResult:
    """Parameters for ``amp * exp(-0.5*((x-cen)/sigma)^2) + slope*x + intercept``."""

    x: np.ndarray
    y_model: np.ndarray
    amp: float
    cen: float
    sigma: float
    slope: float
    intercept: float
    chi2: float
    npts: int

    @property
    def background_at_cen(self) -> float:
        return float(self.slope * self.cen + self.intercept)


def gaussian_plus_linear(
    x: np.ndarray,
    amp: float,
    cen: float,
    sigma: float,
    slope: float,
    intercept: float,
) -> np.ndarray:
    sig = max(float(sigma), 1e-12)
    return amp * np.exp(-0.5 * ((x - cen) / sig) ** 2) + slope * x + intercept


def gaussian_plus_const(
    x: np.ndarray,
    amp: float,
    cen: float,
    sigma: float,
    bg: float,
) -> np.ndarray:
    sig = max(float(sigma), 1e-12)
    return amp * np.exp(-0.5 * ((x - cen) / sig) ** 2) + bg


def fit_gaussian_bg(
    x: Sequence[float],
    y: Sequence[float],
    err: Optional[Sequence[float]] = None,
    *,
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
    amp_positive: bool = True,
    bg_nonneg_at_cen: bool = False,
) -> FitResult:
    """
    Fit Gaussian + linear background to finite (x, y) points.

    Optional ``x_min`` / ``x_max`` restrict the fit window (multi-peak ROI).
    If ``bg_nonneg_at_cen``, fit Gaussian + **constant** bg ≥ 0 (slope = 0).

    Requires ``scipy``. Raises ``ValueError`` / ``RuntimeError`` on bad input or failure.
    """
    if curve_fit is None:
        raise RuntimeError("scipy is required for Fit MVP (pip/apt install scipy)")

    xa = np.asarray(x, dtype=float).ravel()
    ya = np.asarray(y, dtype=float).ravel()
    if xa.size != ya.size:
        raise ValueError("x and y must have the same length")
    mask = np.isfinite(xa) & np.isfinite(ya)
    if x_min is not None and np.isfinite(x_min):
        mask &= xa >= float(x_min)
    if x_max is not None and np.isfinite(x_max):
        mask &= xa <= float(x_max)
    xa = xa[mask]
    ya = ya[mask]
    if xa.size < 5:
        raise ValueError(
            f"need at least 5 finite points in fit window (got {xa.size}"
            + (
                f"; x in [{x_min}, {x_max}]"
                if x_min is not None or x_max is not None
                else ""
            )
            + ")"
        )

    sigma_y = None
    if err is not None:
        ea = np.asarray(err, dtype=float).ravel()
        if ea.size == np.asarray(x, dtype=float).ravel().size:
            ea = ea[mask]
            good = np.isfinite(ea) & (ea > 0)
            if np.any(good):
                med = float(np.median(ea[good]))
                sigma_y = np.where(good, ea, med)

    p0 = _initial_guess(xa, ya)
    x_lo, x_hi = float(np.min(xa)), float(np.max(xa))
    span = max(x_hi - x_lo, 1e-9)
    amp_lo = 0.0 if amp_positive else -np.inf

    try:
        if bg_nonneg_at_cen:
            p0c = [p0[0], p0[1], p0[2], max(0.0, float(np.min(ya)))]
            bounds_c = (
                [amp_lo, x_lo, span * 0.01, 0.0],
                [np.inf, x_hi, span * 2.0, np.inf],
            )
            for i, (lo, hi) in enumerate(zip(bounds_c[0], bounds_c[1])):
                p0c[i] = float(np.clip(p0c[i], lo, hi if np.isfinite(hi) else p0c[i]))
            popt, _pcov = curve_fit(
                gaussian_plus_const,
                xa,
                ya,
                p0=p0c,
                sigma=sigma_y,
                absolute_sigma=sigma_y is not None,
                bounds=bounds_c,
                maxfev=8000,
            )
            amp, cen, sigma, intercept = (float(v) for v in popt)
            slope = 0.0
        else:
            bounds = (
                [amp_lo, x_lo, span * 0.01, -np.inf, -np.inf],
                [np.inf, x_hi, span * 2.0, np.inf, np.inf],
            )
            for i, (lo, hi) in enumerate(zip(bounds[0], bounds[1])):
                p0[i] = float(
                    np.clip(
                        p0[i],
                        lo if np.isfinite(lo) else p0[i],
                        hi if np.isfinite(hi) else p0[i],
                    )
                )
            popt, _pcov = curve_fit(
                gaussian_plus_linear,
                xa,
                ya,
                p0=p0,
                sigma=sigma_y,
                absolute_sigma=sigma_y is not None,
                bounds=bounds,
                maxfev=8000,
            )
            amp, cen, sigma, slope, intercept = (float(v) for v in popt)
    except Exception as exc:  # scipy raises various OptimizeWarning/RuntimeError
        raise RuntimeError(f"curve_fit failed: {exc}") from exc

    if abs(sigma) < 1e-12:
        raise RuntimeError("fitted sigma is degenerate")

    y_model = gaussian_plus_linear(xa, amp, cen, abs(sigma), slope, intercept)
    resid = ya - y_model
    if sigma_y is not None:
        chi2 = float(np.sum((resid / sigma_y) ** 2))
    else:
        chi2 = float(np.sum(resid**2))

    return FitResult(
        x=xa.copy(),
        y_model=y_model,
        amp=amp,
        cen=cen,
        sigma=abs(sigma),
        slope=slope,
        intercept=intercept,
        chi2=chi2,
        npts=int(xa.size),
    )


def _initial_guess(x: np.ndarray, y: np.ndarray) -> list[float]:
    i_max = int(np.argmax(y))
    cen = float(x[i_max])
    y_edge = float(0.5 * (y[0] + y[-1]))
    amp = float(y[i_max] - y_edge)
    if amp == 0:
        amp = float(np.ptp(y)) or 1.0
    half = y_edge + 0.5 * amp
    above = y >= half
    if np.any(above):
        x_hi = x[above]
        width = float(x_hi.max() - x_hi.min())
        sigma = max(width / 2.355, float(np.ptp(x)) * 0.02, 1e-6)
    else:
        sigma = max(float(np.ptp(x)) * 0.05, 1e-6)
    return [amp, cen, sigma, 0.0, y_edge]
