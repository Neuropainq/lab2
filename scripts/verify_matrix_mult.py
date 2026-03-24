from pathlib import Path
import re

import numpy as np


path_data = Path.cwd() / "data"
ok_all = True

files = sorted(
    path_data.glob("C_*.txt"),
    key=lambda path: int(re.search(r"C_(\d+)\.txt", path.name).group(1)),
)

for c_file in files:
    n = int(re.search(r"C_(\d+)\.txt", c_file.name).group(1))

    a = np.loadtxt(path_data / f"A_{n}.txt", dtype=np.int64)
    b = np.loadtxt(path_data / f"B_{n}.txt", dtype=np.int64)
    c = np.loadtxt(path_data / f"C_{n}.txt", dtype=np.int64)

    ok = np.array_equal(a @ b, c)
    ok_all = ok_all and ok
    print(f"n={n}: {ok}")

if not ok_all:
    raise SystemExit(1)
