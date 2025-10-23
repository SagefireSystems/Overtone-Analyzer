# compare_spectra.py — combine your analyzer CSVs into one comparison plot
# Looks for any of these files if they exist:
#   samples_gabo_voice_demo_spectrum.csv
#   samples_gabo_voice_bright_spectrum.csv
#   samples_gabo_voice_extra_bright_spectrum.csv
# Saves: docs/real_comparison.png

import os
import csv
import matplotlib.pyplot as plt
import numpy as np

FILES = [
    ("Demo (natural)", "samples_gabo_voice_demo_spectrum.csv"),
    ("Bright", "samples_gabo_voice_bright_spectrum.csv"),
    ("Extra-bright", "samples_gabo_voice_extra_bright_spectrum.csv"),
]

# Ensure docs/ exists
os.makedirs("docs", exist_ok=True)

def read_csv(path):
    f, p = [], []
    with open(path, "r", newline="") as fp:
        r = csv.reader(fp)
        next(r, None)  # header
        for row in r:
            if len(row) >= 2:
                try:
                    f.append(float(row[0]))
                    p.append(float(row[1]))
                except:
                    pass
    return np.array(f), np.array(p)

def to_db(x):
    x = np.maximum(x, 1e-20)
    return 10*np.log10(x)

plt.figure(figsize=(10, 5))
plotted_any = False

for label, fname in FILES:
    if os.path.exists(fname):
        f, P = read_csv(fname)
        if len(f) > 0:
            plt.semilogx(f, to_db(P), label=label)
            plotted_any = True
    else:
        print(f"[skip] {fname} not found")

if not plotted_any:
    raise SystemExit("No spectrum CSVs found. Run the analyzer with --save first.")

# Optional: draw band guides for quick reading
for x in [60, 250, 400, 1500, 2000, 8000]:
    plt.axvline(x, color="0.85", linewidth=0.8)

plt.xlabel("Frequency (Hz)")
plt.ylabel("Relative Power (dB)")
plt.title("Real Spectrum Comparison — Demo vs Bright vs Extra-bright")
plt.grid(True, which="both", linestyle=":")
plt.legend()
plt.tight_layout()
out_path = os.path.join("docs", "real_comparison.png")
plt.savefig(out_path, dpi=160)
print(f"✓ Saved {out_path}")
