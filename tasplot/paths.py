from __future__ import annotations

import os


def hb3_scan_path(user_root: str, experiment: int, scan: int) -> str:
    """
    HB3 SPiCE data file path.

    Example: user_root/exp382/Datafiles/HB3_exp0382_scan0001.dat
    """
    return os.path.join(
        user_root,
        f"exp{experiment}",
        "Datafiles",
        f"HB3_exp{experiment:04d}_scan{scan:04d}.dat",
    )
