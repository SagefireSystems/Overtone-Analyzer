# 🎧 Overtone Analyzer

A lightweight command-line tool that analyzes vocal or instrumental recordings — perfect for overtone singers, sound designers, and anyone exploring the harmonic layers of sound.

---

## 🧠 Overview

**Overtone Analyzer** reads a `.wav` file and measures the energy distribution across key frequency bands:

| Band | Range (Hz) | Meaning |
|------|-------------|---------|
| **Bass** | 60 – 250 | Fundamental & chest resonance |
| **Formant** | 400 – 1500 | Mouth/throat shaping |
| **Overtones** | 3000 – 8000 | Brightness & harmonic “air” |

It also estimates the **peak fundamental frequency** (60–300 Hz) and can save detailed plots and data files.

---

## ⚙️ Features

- 🔍 Fast spectrum & band-energy analysis  
- 📈 Optional PNG/CSV/JSON outputs (`--save`)  
- 🎛 Works with mono/stereo WAV (16/24/32-bit or float)  
- 🧠 Only needs `numpy` + `matplotlib` (and optionally `soundfile` / `scipy`)  

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/overtone-analyzer.git
cd overtone-analyzer
pip install numpy matplotlib soundfile scipy
