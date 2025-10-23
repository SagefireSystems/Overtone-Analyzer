# brighten.py — makes an “extra-bright” version of your bright sample
import numpy as np
import soundfile as sf
from scipy.signal import iirfilter, lfilter

IN_FILE  = "samples_gabo_voice_bright.wav"
OUT_FILE = "samples_gabo_voice_extra_bright.wav"

y, sr = sf.read(IN_FILE)
if y.ndim > 1:
    y = y.mean(axis=1)

# 3 kHz high-pass-ish filter -> blend for high-shelf effect
b, a = iirfilter(2, 3000/(sr/2), btype="high", ftype="butter")
y_hp = lfilter(b, a, y)

blend = 2.5  # raise for more sparkle
y_out = y + blend * y_hp

# soft clip + normalize
y_out = np.tanh(1.2 * y_out)
y_out /= (np.max(np.abs(y_out)) + 1e-12)

sf.write(OUT_FILE, y_out, sr)
print(f"✓ Saved {OUT_FILE} at {sr} Hz")
