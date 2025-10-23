# compare_bands.py — build a side-by-side bar chart from *_summary.json
# Saves: docs/band_comparison.png

import os, json
import matplotlib.pyplot as plt
import numpy as np

# Files to include (label, summary.json filename)
FILES = [
    ("Demo (natural)", "samples_gabo_voice_demo_summary.json"),
    ("Bright", "samples_gabo_voice_bright_summary.json"),
    ("Extra-bright", "samples_gabo_voice_extra_bright_summary.json"),
]

os.makedirs("docs", exist_ok=True)

def load_bands(summary_path):
    with open(summary_path, "r") as f:
        data = json.load(f)
    # Expect "bands" like [{"band":"Bass 60–250 Hz","pct":67.665}, ...]
    rows = data.get("bands", [])
    # robust: map by band name contains "Bass", "Formant", "Overtones"
    out = {"Bass": None, "Formant": None, "Overtones": None}
    for r in rows:
        name = r.get("band","")
        pct = r.get("pct", 0.0)
        if "Bass" in name:
            out["Bass"] = pct
        elif "Formant" in name:
            out["Formant"] = pct
        elif "Overtones" in name:
            out["Overtones"] = pct
    return out

# Gather data
labels = []
bass = []
form = []
overt = []
missing = []

for label, fname in FILES:
    if os.path.exists(fname):
        bands = load_bands(fname)
        labels.append(label)
        bass.append(bands["Bass"] or 0.0)
        form.append(bands["Formant"] or 0.0)
        overt.append(bands["Overtones"] or 0.0)
    else:
        missing.append(fname)

if missing and len(labels) == 0:
    raise SystemExit("No *_summary.json files found. Run the analyzer with --save first.")

# Plot
x = np.arange(len(labels))
w = 0.25

plt.figure(figsize=(10,5))
plt.bar(x - w, bass, width=w, label="Bass 60–250 Hz")
plt.bar(x,      form, width=w, label="Formant 400–1500 Hz")
plt.bar(x + w,  overt, width=w, label="Overtones (air)")

plt.xticks(x, labels, rotation=0)
plt.ylabel("Energy (%)")
plt.title("Band Energy Comparison — Demo vs Bright vs Extra-bright")
plt.grid(axis="y", linestyle=":", alpha=0.5)
plt.legend()
plt.tight_layout()

out_path = os.path.join("docs", "band_comparison.png")
plt.savefig(out_path, dpi=160)
print(f"✓ Saved {out_path}")

if missing:
    print("[info] Missing summaries were skipped:")
    for m in missing:
        print("  -", m)
