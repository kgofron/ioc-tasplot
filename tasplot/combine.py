"""Combine / subtract scans with SpICE-style bin tolerance and renorm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from tasplot.dataset import ScanDataset


@dataclass(frozen=True)
class CombineCurve:
    """One scan contribution to a combine operation."""

    x: np.ndarray
    y: np.ndarray
    weight: np.ndarray  # monitor / time / mcu (positive)
    sign: int  # +1 add, -1 subtract


@dataclass(frozen=True)
class CombineResult:
    x: np.ndarray
    y: np.ndarray
    err: np.ndarray
    description: str = ""


def parse_scan_list(text: str) -> list[int]:
    """Parse ``\"1, 2, 5\"`` or whitespace-separated scan numbers."""
    out: list[int] = []
    for part in (text or "").replace(";", ",").replace(" ", ",").split(","):
        part = part.strip()
        if not part:
            continue
        out.append(int(part))
    return out


def curve_from_scan(
    scan: ScanDataset,
    *,
    x_col: str,
    y_col: str,
    weight_col: str,
    sign: int,
) -> CombineCurve:
    """Extract X/Y/weight arrays for combine (raw counts; renorm after binning)."""
    if sign not in (-1, 1):
        raise ValueError("sign must be +1 or -1")
    x = np.asarray(scan.column(x_col), dtype=float)
    y = np.asarray(scan.column(y_col), dtype=float)
    w = np.asarray(scan.column(weight_col), dtype=float)
    if x.shape != y.shape or x.shape != w.shape:
        raise ValueError("x/y/weight length mismatch")
    if np.any(w <= 0):
        # Zero-weight points cannot renorm; drop them.
        ok = w > 0
        x, y, w = x[ok], y[ok], w[ok]
    return CombineCurve(x=x, y=y, weight=w, sign=int(sign))


def combine_curves(
    curves: Sequence[CombineCurve],
    *,
    bin_tol: float,
    norm_value: float = 1.0,
    description: str = "",
) -> CombineResult:
    """
    SpICE-like combine: accumulate signed Y and weights into X bins of width ``bin_tol``.

    For each bin::

        y_out = (Σ sign·y) / (Σ weight) * norm_value
        err   = √(Σ y) / (Σ weight) * norm_value   # Poisson on raw counts before sign

    If ``bin_tol <= 0``, all curves must share identical X (within 1e-9 relative);
    then combine is element-wise.
    """
    if not curves:
        raise ValueError("no curves to combine")
    norm_value = float(norm_value)
    if norm_value <= 0:
        raise ValueError("norm_value must be > 0")

    if float(bin_tol) <= 0:
        return _combine_exact_x(curves, norm_value=norm_value, description=description)
    return _combine_binned(
        curves, bin_tol=float(bin_tol), norm_value=norm_value, description=description
    )


def _combine_exact_x(
    curves: Sequence[CombineCurve], *, norm_value: float, description: str
) -> CombineResult:
    ref = curves[0].x
    for c in curves[1:]:
        if c.x.shape != ref.shape or not np.allclose(c.x, ref, rtol=0, atol=1e-9):
            raise ValueError(
                "bin_tol=0 requires identical X arrays; set Bin Tolerance > 0 to rebin"
            )
    y_sum = np.zeros_like(ref, dtype=float)
    w_sum = np.zeros_like(ref, dtype=float)
    var = np.zeros_like(ref, dtype=float)
    for c in curves:
        y_sum += c.sign * c.y
        w_sum += c.weight
        var += c.y  # variance of counts (unsigned)
    if np.any(w_sum <= 0):
        raise ValueError("combined weight is zero at one or more X points")
    y = y_sum / w_sum * norm_value
    err = np.sqrt(np.maximum(var, 0.0)) / w_sum * norm_value
    return CombineResult(x=ref.copy(), y=y, err=err, description=description)


def _combine_binned(
    curves: Sequence[CombineCurve],
    *,
    bin_tol: float,
    norm_value: float,
    description: str,
) -> CombineResult:
    xs = np.concatenate([c.x for c in curves])
    x_min = float(np.min(xs))
    x_max = float(np.max(xs))
    step = float(bin_tol)
    zero = step / 100.0
    nbin = int(np.floor((x_max + zero - x_min) / step)) + 1
    if nbin < 1:
        raise ValueError("invalid bin grid")
    # Bin centers from x_min .. x_min + (nbin-1)*step; edges ± step/2
    edges = np.linspace(x_min - step / 2.0, x_min + step * (nbin - 0.5), nbin + 1)

    y_acc = np.zeros(nbin, dtype=float)
    w_acc = np.zeros(nbin, dtype=float)
    x_acc = np.zeros(nbin, dtype=float)
    var_acc = np.zeros(nbin, dtype=float)

    for c in curves:
        for i, x0 in enumerate(c.x):
            # First edge strictly greater than x0 (TAVI-style).
            idx = int(np.nanargmax(edges - zero > x0))
            if idx <= 0 or idx > nbin:
                continue
            b = idx - 1
            y_acc[b] += c.sign * c.y[i]
            w_acc[b] += c.weight[i]
            x_acc[b] += c.x[i] * c.weight[i]
            var_acc[b] += c.y[i]

    used = w_acc > 0
    if not np.any(used):
        raise ValueError("no points fell into bins")
    x_out = x_acc[used] / w_acc[used]
    y_out = y_acc[used] / w_acc[used] * norm_value
    err_out = np.sqrt(np.maximum(var_acc[used], 0.0)) / w_acc[used] * norm_value
    order = np.argsort(x_out)
    return CombineResult(
        x=x_out[order],
        y=y_out[order],
        err=err_out[order],
        description=description,
    )


def resolve_column(scan: ScanDataset, name: str) -> str:
    if not name:
        raise KeyError("column name is empty")
    if name in scan.columns:
        return name
    lower = {c.lower(): c for c in scan.columns}
    if name.lower() not in lower:
        raise KeyError(name)
    return lower[name.lower()]


def iter_signed_scan_numbers(
    add: Iterable[int], sub: Iterable[int]
) -> list[tuple[int, int]]:
    """Return ``(scan_number, sign)`` pairs."""
    out: list[tuple[int, int]] = []
    for n in add:
        out.append((int(n), 1))
    for n in sub:
        out.append((int(n), -1))
    return out
