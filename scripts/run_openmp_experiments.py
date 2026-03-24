from pathlib import Path
import csv
import re
import subprocess


root = Path(__file__).resolve().parents[1]
exe = root / "matrixmult" / "matrixmult.exe"
results_dir = root / "results"
results_dir.mkdir(exist_ok=True)
results_csv = results_dir / "openmp_results.csv"

sizes = [200, 400, 800, 1200, 1600, 2000]
thread_counts = [1, 2, 4, 8]
core_counts = [1, 2, 4, 8]

line_re = re.compile(
    r"N=(\d+)\s+\|\s+Threads:\s+(\d+)\s+\|\s+Cores:\s+(\d+)\s+\|\s+Time:\s+(\d+)\s+ms"
)


with results_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["size", "threads", "cores", "time_ms"])

    for cores in core_counts:
        for threads in thread_counts:
            cmd = [
                str(exe),
                "--threads",
                str(threads),
                "--cores",
                str(cores),
                "--sizes",
                ",".join(str(n) for n in sizes),
                "--no-save",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("Experiment failed")
                print(" ".join(cmd))
                print(result.stdout)
                print(result.stderr)
                raise SystemExit(result.returncode)

            for line in result.stdout.splitlines():
                match = line_re.search(line)
                if match:
                    size, thr, used_cores, time_ms = match.groups()
                    writer.writerow([size, thr, used_cores, time_ms])
                    print(
                        f"size={size}, threads={thr}, cores={used_cores}, time_ms={time_ms}"
                    )

print(f"Saved results: {results_csv}")
