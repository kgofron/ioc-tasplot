"""SpICE-style scratch data buffers (X/Y/Error + metadata)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

DEFAULT_N_SLOTS = 8


@dataclass
class DataBuffer:
    """One scratch buffer: plotted curve + labels."""

    x: np.ndarray
    y: np.ndarray
    err: np.ndarray
    description: str = ""
    x_label: str = ""
    y_label: str = ""

    def __post_init__(self) -> None:
        self.x = np.asarray(self.x, dtype=float).ravel()
        self.y = np.asarray(self.y, dtype=float).ravel()
        self.err = np.asarray(self.err, dtype=float).ravel()
        n = len(self.x)
        if len(self.y) != n or len(self.err) != n:
            raise ValueError("x, y, and err must have the same length")

    @property
    def nrows(self) -> int:
        return int(len(self.x))

    @property
    def empty(self) -> bool:
        return self.nrows == 0

    def summary(self, index: int) -> str:
        if self.empty:
            return f"{index}:empty"
        desc = (self.description or "(no desc)").replace(";", ",")[:40]
        return f"{index}:{self.nrows}pts {desc}"


@dataclass
class BufferStore:
    """Fixed slot table of optional :class:`DataBuffer` instances."""

    n_slots: int = DEFAULT_N_SLOTS
    slots: list[Optional[DataBuffer]] = field(init=False)

    def __post_init__(self) -> None:
        if self.n_slots < 1:
            raise ValueError("n_slots must be >= 1")
        self.slots = [None] * int(self.n_slots)

    def get(self, index: int) -> Optional[DataBuffer]:
        return self.slots[self._check(index)]

    def save(self, index: int, buf: DataBuffer) -> None:
        self.slots[self._check(index)] = buf

    def clear(self, index: int) -> None:
        self.slots[self._check(index)] = None

    def set_meta(
        self,
        index: int,
        *,
        description: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
    ) -> None:
        buf = self.get(index)
        if buf is None:
            raise ValueError(f"buffer slot {index} is empty")
        if description is not None:
            buf.description = description.strip()
        if x_label is not None:
            buf.x_label = x_label.strip()
        if y_label is not None:
            buf.y_label = y_label.strip()

    def list_summary(self) -> str:
        parts = []
        for i, slot in enumerate(self.slots):
            if slot is None or slot.empty:
                parts.append(f"{i}:empty")
            else:
                parts.append(slot.summary(i))
        return "; ".join(parts)

    def write_ascii(self, index: int, path: str | Path) -> Path:
        buf = self.get(index)
        if buf is None or buf.empty:
            raise ValueError(f"buffer slot {index} is empty")
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# description = {buf.description}",
            f"# x_label = {buf.x_label}",
            f"# y_label = {buf.y_label}",
            f"# nrows = {buf.nrows}",
            "# X Y Error",
        ]
        for x, y, e in zip(buf.x, buf.y, buf.err):
            lines.append(f"{x:.8g} {y:.8g} {e:.8g}")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return out

    def _check(self, index: int) -> int:
        i = int(index)
        if i < 0 or i >= self.n_slots:
            raise IndexError(f"buffer slot {i} out of range 0..{self.n_slots - 1}")
        return i


def buffer_from_arrays(
    x: Sequence[float],
    y: Sequence[float],
    err: Optional[Sequence[float]] = None,
    *,
    description: str = "",
    x_label: str = "",
    y_label: str = "",
) -> DataBuffer:
    """Build a buffer from sequences; drop trailing NaNs; pad missing err with √|Y|."""
    xa = np.asarray(list(x), dtype=float).ravel()
    ya = np.asarray(list(y), dtype=float).ravel()
    n = _finite_prefix_len(xa, ya)
    xa = xa[:n]
    ya = ya[:n]
    if err is None:
        ea = np.sqrt(np.abs(ya))
    else:
        ea = np.asarray(list(err), dtype=float).ravel()[:n]
        if len(ea) < n:
            pad = np.sqrt(np.abs(ya[len(ea) :]))
            ea = np.concatenate([ea, pad])
    return DataBuffer(
        x=xa,
        y=ya,
        err=ea,
        description=description,
        x_label=x_label,
        y_label=y_label,
    )


def _finite_prefix_len(x: np.ndarray, y: np.ndarray) -> int:
    n = min(len(x), len(y))
    for i in range(n):
        if not (np.isfinite(x[i]) and np.isfinite(y[i])):
            return i
    return n
