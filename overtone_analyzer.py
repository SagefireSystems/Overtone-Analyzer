#!/usr/bin/env python3
"""
Overtone Analyzer — patched
- Fix: np.trapz -> np.trapezoid (deprecation)
- New: --air-low / --air-high to tune “overtones” band (default 2000–8000 Hz)
- New: --decimals to control print/label precision (default 2)
Usage:
  python overtone_analyzer.py <path_to_wav> [--save] [--air-low 2000] [--air-high 8000] [--decimals 2]
"""

import argparse
import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt

def read_audio(path):
    """Try reading audio with soundfile, then scipy, then wave (PCM only). Returns (y, sr)."""
    # 1) soundfile (best for diverse formats)
    try:
        import soundfile as sf
        y, sr = sf.read(path, always_2d=False)
        if y.ndim > 1:
            y = y.mean(axis=1)
        y = y.astype(np.float64, copy=False)
        return y, int(sr)
    except Exception:
        pass

    # 2) scipy.io.wavfile
    try:
        from scipy.io import wavfile
        sr, y = wavfile.read(path)
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

    # 3) wave fallback (PCM 8/16/24/32)
    try:
        import wave
        with wave.open(path, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth  = wf.getsampwidth()
            sr         = wf.getframerate()
            n_frames   = wf.getnframes()
            raw = wf.readframes(n_frames)

        if sampwidth == 1:
            data = (np.frombuffer(raw, np.uint8).astype(np.float64) - 128.0) / 128.0
        elif sampwidth == 2:
            data = np.frombuffer(raw, np.int16).astype(np.float64) / 32768.0
        elif sampwidth == 3:
            a = np.frombuffer(raw, np.uint8).reshape(-1, 3)
            b = (a[:,0].astype(np.uint32) |
                 (a[:,1].astype(np.uint32) << 8) |
                 (a[:,2].astype(np.uint32) << 16))
            mask = b & 0x800000
            b = b | (0xFF000000 * (mask > 0))
            data = b.view(np.int32).astype(np.float64) / 8388608.0
        elif sampwidth == 4:
            data = np.frombuffer(raw, np.int32).astype(np.float64) / 2147483648.0
        else:
            raise RuntimeError("Unsupported sample width in fallback reader.")

        if n_channels > 1:
            data = data.reshape(-1, n_channels).mean(axis=1)
        return data, int(sr)
    except Exception as e:
        raise RuntimeError(f"Could not read audio file '{path}'. Install 'soundfile' or 'scipy'. Error: {e}")

def compute_psd(y, sr):
    """Return frequency (Hz) and power spectral density using Welch if available, else FFT fallback."""
    y = y - np.mean(y)
    try:
        from scipy.signal import welch
        nperseg = min(len(y), 8192)
        nperseg = max(nperseg, 256)
        f, Pxx = welch(y, fs=sr, window='hann', nperseg=nperseg,
                       noverlap=nperseg//2, detrend='constant', scaling='spectrum')
        return f, Pxx
    except Exception:
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
    # np.trapz -> np.trapezoid
    return float(np.trapezoid(Pxx[idx], f[idx]))

def summarize_bands(f, Pxx, air_lo, air_hi):
    # Ignore <20 Hz
    mask = f >= 20
    total = float(np.trapezoid(Pxx[mask], f[mask]))
    if total <= 0:
        total = 1e-12

    bands = [
        ("Bass 60–250 Hz", 60, 250),
        ("Formant 400–1500 Hz", 400, 1500),
        (f"Overtones {int(air_lo/1000)}–{int(air_hi/1000)} kHz" if air_lo>=1000 else f"Overtones {int(air_lo)}–{int(air_hi/1000)} kHz",
         air_lo, air_hi),
    ]

    out = []
    for name, lo, hi in bands:
        e = band_energy(f, Pxx, lo, hi)
        pct = 100.0 * e / total
        out.append({"band": name, "lo_hz": lo, "hi_hz": hi, "energy": e, "pct": pct})
    return out, total, bands

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

def save_bars_plot(out_path, bands, decimals=2):
    labels = [b["band"] for b in bands]
    vals = [b["pct"] for b in bands]
    plt.figure()
    plt.bar(labels, vals)
    plt.ylabel("Energy (%)")
    plt.title("Band Energy Distribution")
    for i, v in enumerate(vals):
        plt.text(i, v + 1, f"{v:.{decimals}f}%", ha='center', va='bottom', fontsize=9)
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
    ap.add_argument("--air-low", type=float, default=2000.0, help="Overtones band low edge in Hz (default 2000)")
    ap.add_argument("--air-high", type=float, default=8000.0, help="Overtones band high edge in Hz (default 8000)")
    ap.add_argument("--decimals", type=int, default=2, help="Decimal places for printed/label percentages (default 2)")
    args = ap.parse_args()

    path = args.wav
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        raise SystemExit(1)

    y, sr = read_audio(path)
    duration = len(y) / sr

    f, Pxx = compute_psd(y, sr)
    band_rows, total, band_defs = summarize_bands(f, Pxx, args.air_low, args.air_high)
    f0 = estimate_fundamental(f, Pxx)

    # Output
    print("\n=== Overtone Analyzer ===")
    print(f"File: {os.path.basename(path)}")
    print(f"Duration: {duration:.2f} s   Sample Rate: {sr} Hz")
    if f0 is not None:
        print(f"Estimated peak fundamental (60–300 Hz): {f0:.1f} Hz")
    else:
        print("Estimated peak fundamental: n/a")

    for b in band_rows:
        print(f"- {b['band']}: {b['pct']:.{args.decimals}f}%")

    if args.save:
        base = os.path.splitext(path)[0]
        spec_png = base + "_spectrum.png"
        bars_png = base + "_bands.png"
        csv_path = base + "_spectrum.csv"
        json_path = base + "_summary.json"

        save_spectrum_plot(spec_png, f, Pxx, title=f"Spectrum — {os.path.basename(path)}")
        save_bars_plot(bars_png, band_rows, decimals=args.decimals)
        save_csv(csv_path, f, Pxx)

        summary = {
            "file": os.path.basename(path),
            "sample_rate": sr,
            "duration_sec": duration,
            "estimated_fundamental_hz": f0,
            "bands": band_rows,
            "total_power": total,
            "air_band_hz": [args.air_low, args.air_high],
            "decimals": args.decimals,
        }
        with open(json_path, 'w') as fp:
            json.dump(summary, fp, indent=2)

        print(f"\nSaved: {os.path.basename(spec_png)}, {os.path.basename(bars_png)},")
        print(f"       {os.path.basename(csv_path)}, {os.path.basename(json_path)}")

if __name__ == "__main__":
    main()
