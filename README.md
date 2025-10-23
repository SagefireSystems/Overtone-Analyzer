# Psychomantle Overtone Analyzer — Project Skeleton

## 🎯 Goal
Create a sound-reactive tool that visualizes overtone and harmonic structures from throat singing — merging bioacoustics, cymatics, and artistic feedback loops.

## 🧩 Basic Architecture
1. **Input** — Microphone audio stream (`pyaudio`, `sounddevice`)
2. **Processing** — FFT analysis (`numpy`, `scipy`)
3. **Visualization** — Real-time graph (`matplotlib` or Pixelblaze link)
4. **Integration** — Optional Reflex Engine plugin for performance tracking

## 🧪 MVP Plan
- Record sample `.wav` files
- Plot spectral energy bands:  
  - **Bass:** 60–250 Hz  
  - **Formant:** 400–1,500 Hz  
  - **Overtone (air):** 2–8 kHz  
- Save results as JSON and CSV
- Generate spectrum and band charts automatically via batch file

## 🚀 Future Additions
- Real-time LED feedback (Pixelblaze / MIDI reactive)
- Streamlit or Reflex Engine front-end
- Obsidian data logging for reflection analytics

---

## 📊 Real Spectrum Comparison
After analyzing multiple takes, the tool creates a direct frequency overlay:

![Real Comparison](docs/real_comparison.png)

This plot compares the **Demo**, **Bright**, and **Extra-bright** versions of your voice, showing how energy shifts upward through the harmonic bands.

---

### Band Percentages (from your runs)
This chart shows the **energy balance** across bands for each version:

![Band Comparison](docs/band_comparison.png)

Use this to spot whether your **overtones** (2–8 kHz) are actually increasing when you change EQ, mic distance, or vocal technique.

---

## 🧠 Insight
- The analyzer quantifies what your ears perceive as *presence*, *brightness*, and *resonance.*
- Over time, you can build a database of your throat-singing progress — a measurable growth curve for harmonic control.

---

### 📁 Output Folder Structure

