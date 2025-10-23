# Psychomantle Overtone Analyzer — Project Skeleton

## Goal
Create a sound‑reactive tool that visualizes overtone and harmonic structures from throat singing.

## Basic Architecture
1. **Input** — microphone audio stream (`pyaudio`, `sounddevice`)  
2. **Processing** — FFT analysis (`numpy`, `scipy`)  
3. **Visualization** — real‑time graph (`matplotlib`, or Pixelblaze link)  
4. **Integration** — optional Reflex Engine plugin for tracking improvements.

## MVP Plan
- Record sample .wav files.  
- Plot spectral energy bands: bass (60–250 Hz), formant (400–1,500 Hz), overtone (3–8 kHz).  
- Save results to `/data/` as timestamped JSON or CSV.

## Future Additions
- Real‑time visual interface (Streamlit or Processing).  
- Link to LED or Pixelblaze reactive lighting.  
- Combine with Obsidian reflection logs for performance analytics.
