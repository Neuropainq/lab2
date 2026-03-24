from pathlib import Path
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


root = Path(__file__).resolve().parents[1]
results_csv = root / "results" / "openmp_results.csv"
out_png = root / "results" / "openmp_time_plot.png"

rows = []
with results_csv.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(
            {
                "size": int(row["size"]),
                "threads": int(row["threads"]),
                "cores": int(row["cores"]),
                "time_ms": int(row["time_ms"]),
            }
        )

if not rows:
    print("No experiment results found")
    raise SystemExit(1)

cores_values = sorted({row["cores"] for row in rows})
thread_values = sorted({row["threads"] for row in rows})

plt.figure(figsize=(10, 6))

for cores in cores_values:
    for threads in thread_values:
        points = [
            row for row in rows
            if row["cores"] == cores and row["threads"] == threads
        ]
        points.sort(key=lambda row: row["size"])
        if not points:
            continue

        sizes = [row["size"] for row in points]
        times = [row["time_ms"] for row in points]
        label = f"cores={cores}, threads={threads}"
        plt.plot(sizes, times, marker="o", label=label)

plt.title("OpenMP: time vs matrix size")
plt.xlabel("Matrix size N")
plt.ylabel("Time (ms)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(out_png, dpi=150)

print("Saved:", out_png)
