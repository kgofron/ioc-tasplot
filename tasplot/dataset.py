from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np


class FormatError(ValueError):
    """File content is not a recognized SPiCE or SPEC scan format."""


@dataclass
class ScanDataset:
    """Normalized scan table for plotting."""

    format: str  # "spice" or "spec"
    path: str
    meta: dict[str, str] = field(default_factory=dict)
    columns: list[str] = field(default_factory=list)
    data: np.ndarray = field(default_factory=lambda: np.zeros((0, 0)))
    default_x: Optional[str] = None
    default_y: Optional[str] = None
    scan_number: Optional[int] = None
    command: Optional[str] = None
    file_meta: dict[str, str] = field(default_factory=dict)

    @property
    def nrows(self) -> int:
        return int(self.data.shape[0]) if self.data.size else 0

    @property
    def ncols(self) -> int:
        return int(self.data.shape[1]) if self.data.size else 0

    def column(self, name: str) -> np.ndarray:
        try:
            idx = self.columns.index(name)
        except ValueError as exc:
            raise KeyError(name) from exc
        return self.data[:, idx]

    def axis(self, name: Optional[str]) -> np.ndarray:
        if name is None:
            raise ValueError("axis name is required")
        return self.column(name)

    def poisson_errors(self, y_column: Optional[str] = None) -> np.ndarray:
        """Square-root errors for count-like Y (negative values -> 0 error)."""
        y = self.axis(y_column or self.default_y or self.columns[-1])
        out = np.zeros_like(y, dtype=float)
        positive = y > 0
        out[positive] = np.sqrt(y[positive])
        return out

    def summary(self) -> dict[str, Any]:
        return {
            "format": self.format,
            "path": self.path,
            "scan_number": self.scan_number,
            "command": self.command,
            "nrows": self.nrows,
            "ncols": self.ncols,
            "default_x": self.default_x,
            "default_y": self.default_y,
            "columns": self.columns,
        }
