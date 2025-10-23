#!/usr/bin/env python3
"""
Overtone Analyzer (simple + practical)

Usage:
  python overtone_analyzer.py <path_to_wav> [--save]

What it does:
- Reads a WAV (16/24/32-bit PCM or float) and converts to mono
- Computes a spectrum (Welch if SciPy is available; otherwise a Hann + FFT fallback)
- Reports percentage energy in bands:
    Bass:   60–250 Hz
    Formant:400–1500 Hz
    Air:    3000–8000 Hz
- Estimates peak fundamental in 60–300 Hz
- Prints a compact report
- If --save is given, writes:
    *_spectrum.png, *_bands.png, *_summary.json, *_spectrum.csv

Dependencies:
  - Required: numpy, matplotlib
  - Optional: soundfile or scipy (for more robust WAV reading / PSD)
Install:
  pip install numpy matplotlib soundfile scipy
"""

import argparse
import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt

def read_audio(path):
    """Try reading audio with soundfile, then scipy, then wave (PCM only). Returns (y, sr)."""
    # 1) Try soundfile (best for diverse formats)
    try:
        import soundfile as sf
        y, sr = sf.read(path, always_2d=False)
        if y.ndim > 1:
            y = y.mean(axis=1)
        y = y.astype(np.float64, copy=False)
        return y, int(sr)
    except Exception:
        pass

    # 2) Try scipy.io.wavfile
    try:
        from scipy.io import wavfile
        sr, y = wavfile.read(path)
        # Convert to float [-1, 1] if integer
        if np.issubdtype(y.dtype, np.integer):
            max_int = np.iinfo(y.dtype).max
            y = y.astype(np.float64) / max_int
        else:
            y = y.astype(np.float64, copy=False)
        if y.ndim > 1:
            y = y.mean(axis=1)
        return y, int(sr)
    except Exception:
        pass

    # 3) Fallback: python wave (PCM 8/16/24/32)
    try:
        import wave, struct
        with wave.open(path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth  = wf.getsampwidth()
            sr         = wf.getframerate()
            n_frames   = wf.getnframes()
            raw = wf.readframes(n_frames)

        # Interpret raw bytes by sample width
        if sampwidth == 1:
            dtype = np.uint8   # 8-bit unsigned PCM
            data = np.frombuffer(raw, dtype=dtype).astype(np.float64)
            data = (data - 128.0) / 128.0
        elif sampwidth == 2:
            dtype = np.int16
            data = np.frombuffer(raw, dtype=dtype).astype(np.float64) / 32768.0
        elif sampwidth == 3:
            # 24-bit little-endian PCM -> convert manually
            a = np.frombuffer(raw, dtype=np.uint8)
            a = a.reshape(-1, 3)
            # sign-extend from 24-bit to 32-bit
            b = (a[:,0].astype(np.uint32) |
                 (a[:,1].astype(np.uint32) << 8) |
                 (a[:,2].astype(np.uint32) << 16))
            mask = b & 0x800000
            b = b | (0xFF000000 * (mask > 0))
            data = b.view(np.int32).astype(np.float64) / 8388608.0
        elif sampwidth == 4:
            dtype = np.int32
            data = np.frombuffer(raw, dtype=dtype).astype(np.float64) / 2147483648.0
        else:
            raise RuntimeError("Unsupported sample width in fallback reader.")

        if n_channels > 1:
            data = data.reshape(-1, n_channels).mean(axis=1)
        return data, int(sr)
    except Exception as e:
        raise RuntimeError(f"Could not read audio file '{path}'. Install 'soundfile' or 'scipy'. Error: {e}")

def compute_psd(y, sr):
    """Return frequency (Hz) and power spectral density using Welch if available, else FFT fallback."""
    # Remove DC offset
    y = y - np.mean(y)
    # Prefer Welch (smoother) if scipy is available
    try:
        from scipy.signal import welch, get_window
        nperseg = min(len(y), 8192)
        if nperseg < 256:
            nperseg = 256
        f, Pxx = welch(y, fs=sr, window='hann', nperseg=nperseg, noverlap=nperseg//2, detrend='constant', scaling='spectrum')
        return f, Pxx
    except Exception:
        pass

    # Fallback: simple Hann + FFT (one shot)
    n = len(y)
    n_fft = 1
    while n_fft < n:
        n_fft <<= 1
    win = np.hanning(n)
    Y = np.fft.rfft(y[:n] * win, n=n_fft)
    Pxx = (np.abs(Y) ** 2) / (np.sum(win**2) * sr)
    f = np.fft.rfftfreq(n_fft, d=1.0/sr)
    return f, Pxx

def band_energy(f, Pxx, f_lo, f_hi):
    idx = np.where((f >= f_lo) & (f < f_hi))[0]
    if idx.size == 0:
        return 0.0
    return float(np.trapz(Pxx[idx], f[idx]))

def summarize_bands(f, Pxx):
    # Ignore < 20 Hz (rumble)
    total = float(np.trapz(Pxx[f >= 20], f[f >= 20]))
    if total <= 0:
        total = 1e-12

    bands = [
        ("Bass 60–250 Hz", 60, 250),
        ("Formant 400–1500 Hz", 400, 1500),
        ("Overtones 3–8 kHz", 3000, 8000),
    ]

    out = []
    for name, lo, hi in bands:
        e = band_energy(f, Pxx, lo, hi)
        pct = 100.0 * e / total
        out.append({"band": name, "lo_hz": lo, "hi_hz": hi, "energy": e, "pct": pct})
    return out, total

def estimate_fundamental(f, Pxx, lo=60, hi=300):
    idx = np.where((f >= lo) & (f <= hi))[0]
    if idx.size == 0:
        return None
    sub_f = f[idx]; sub_p = Pxx[idx]
    if sub_p.max() <= 0:
        return None
    return float(sub_f[np.argmax(sub_p)])

def save_spectrum_plot(out_path, f, Pxx, title="Spectrum"):
    plt.figure()
    plt.semilogx(f, 10*np.log10(Pxx + 1e-20))
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power (dB)")
    plt.title(title)
    plt.grid(True, which='both', ls=':')
    plt.tight_layout()
    plt.savefig(out_path, dpi=140)
    plt.close()

def save_bars_plot(out_path, bands):
    labels = [b["band"] for b in bands]
    vals = [b["pct"] for b in bands]
    plt.figure()
    plt.bar(labels, vals)
    plt.ylabel("Energy (%)")
    plt.title("Band Energy Distribution")
    for i, v in enumerate(vals):
        plt.text(i, v + 1, f"{v:.1f}%", ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=140)
    plt.close()

def save_csv(out_path, f, Pxx):
    with open(out_path, 'w', newline='') as fp:
        w = csv.writer(fp)
        w.writerow(["freq_hz", "power"])
        for fi, pi in zip(f, Pxx):
            w.writerow([fi, pi])

def main():
    ap = argparse.ArgumentParser(description="Simple Overtone Analyzer")
    ap.add_argument("wav", help="Path to WAV file")
    ap.add_argument("--save", action="store_true", help="Save plots and summary files")
    args = ap.parse_args()

    path = args.wav
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        raise SystemExit(1)

    y, sr = read_audio(path)
    duration = len(y) / sr

    f, Pxx = compute_psd(y, sr)
    bands, total = summarize_bands(f, Pxx)
    f0 = estimate_fundamental(f, Pxx)

    print("\n=== Overtone Analyzer ===")
    print(f"File: {os.path.basename(path)}")
    print(f"Duration: {duration:.2f} s   Sample Rate: {sr} Hz")
    if f0 is not None:
        print(f"Estimated peak fundamental (60–300 Hz): {f0:.1f} Hz")
    else:
        print("Estimated peak fundamental: n/a")

    for b in bands:
        print(f"- {b['band']}: {b['pct']:.2f}%")

    if args.save:
        base = os.path.splitext(path)[0]
        spec_png = base + "_spectrum.png"
        bars_png = base + "_bands.png"
        csv_path = base + "_spectrum.csv"
        json_path = base + "_summary.json"

        save_spectrum_plot(spec_png, f, Pxx, title=f"Spectrum — {os.path.basename(path)}")
        save_bars_plot(bars_png, bands)
        save_csv(csv_path, f, Pxx)

        summary = {
            "file": os.path.basename(path),
            "sample_rate": sr,
            "duration_sec": duration,
            "estimated_fundamental_hz": f0,
            "bands": bands,
            "total_power": total,
        }
        with open(json_path, 'w') as fp:
            json.dump(summary, fp, indent=2)

        print(f"\nSaved: {os.path.basename(spec_png)}, {os.path.basename(bars_png)},")
        print(f"       {os.path.basename(csv_path)}, {os.path.basename(json_path)}")

if __name__ == "__main__":
    main()
