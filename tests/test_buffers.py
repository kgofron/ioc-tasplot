from pathlib import Path

import numpy as np
import pytest

from tasplot.buffers import BufferStore, buffer_from_arrays


def test_buffer_from_arrays_strips_nan_pad():
    buf = buffer_from_arrays(
        [1.0, 2.0, float("nan")],
        [10.0, 20.0, float("nan")],
        description="scan1",
        x_label="s1",
        y_label="detector",
    )
    assert buf.nrows == 2
    assert buf.description == "scan1"
    np.testing.assert_allclose(buf.err, np.sqrt([10.0, 20.0]))


def test_buffer_store_save_clear_list():
    store = BufferStore(n_slots=4)
    store.save(1, buffer_from_arrays([0.0, 1.0], [2.0, 3.0], description="A"))
    assert store.get(0) is None
    assert store.get(1).nrows == 2
    assert "1:2pts A" in store.list_summary()
    store.clear(1)
    assert store.get(1) is None
    assert "1:empty" in store.list_summary()


def test_buffer_store_meta_and_write(tmp_path: Path):
    store = BufferStore(n_slots=2)
    store.save(0, buffer_from_arrays([1.0], [4.0], [0.5], description="d", x_label="x"))
    store.set_meta(0, description="updated", y_label="y")
    buf = store.get(0)
    assert buf.description == "updated"
    assert buf.y_label == "y"
    path = store.write_ascii(0, tmp_path / "buf0.txt")
    text = path.read_text()
    assert "updated" in text
    assert "1 4 0.5" in text


def test_buffer_slot_bounds():
    store = BufferStore(n_slots=2)
    with pytest.raises(IndexError):
        store.save(2, buffer_from_arrays([1.0], [1.0]))
    with pytest.raises(ValueError):
        store.set_meta(0, description="x")
