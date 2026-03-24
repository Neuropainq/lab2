from pathlib import Path
import subprocess
import re
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
lab2_root = root.parent
repo_root = lab2_root.parent

lab1_exe = repo_root / "lab1" / "matrixmult" / "matrixmult.exe"
lab2_csv = lab2_root / "results" / "openmp_results.csv"
out_png = lab2_root / "results" / "compare_lab1_lab2.png"

sizes = [200, 400, 800, 1200, 1600, 2000]
chosen_threads = 4
chosen_cores = 4

if not lab1_exe.exists():
    print("File not found:", lab1_exe)
    raise SystemExit(1)

if not lab2_csv.exists():
    print("File not found:", lab2_csv)
    raise SystemExit(1)

result = subprocess.run([str(lab1_exe)], capture_output=True, text=True)
if result.returncode != 0:
    print(result.stdout)
    print(result.stderr)
    raise SystemExit(1)

lab1_times = {}
pattern = re.compile(r"N=(\d+)\s+\|\s+Time:\s+(\d+)\s+ms")

for line in result.stdout.splitlines():
    match = pattern.search(line)
    if match:
        n, t = match.groups()
        n = int(n)
        t = int(t)
        if n in sizes:
            lab1_times[n] = t

lab2_times = {}
with lab2_csv.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        n = int(row["size"])
        threads = int(row["threads"])
        cores = int(row["cores"])
        time_ms = int(row["time_ms"])

        if threads == chosen_threads and cores == chosen_cores and n in sizes:
            lab2_times[n] = time_ms

x = [n for n in sizes if n in lab1_times and n in lab2_times]
y1 = [lab1_times[n] for n in x]
y2 = [lab2_times[n] for n in x]

if not x:
    print("No common data points found for comparison")
    raise SystemExit(1)

plt.figure(figsize=(9, 5))
plt.plot(x, y1, marker="o", label="Lab1 sequential")
plt.plot(
    x,
    y2,
    marker="o",
    label=f"Lab2 OpenMP ({chosen_threads} threads, {chosen_cores} cores)",
)
plt.title("Lab1 vs Lab2")
plt.xlabel("Matrix size N")
plt.ylabel("Time (ms)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(out_png, dpi=150)

print("Saved:", out_png)
