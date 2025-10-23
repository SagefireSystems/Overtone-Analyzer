@echo off
REM =============== Overtone Analyzer — Batch Runner ===============
REM Folder
cd /d "C:\Users\gabri\iCloudDrive\Overtone Analyzer Project"

REM Activate venv (batch version)
call ".\.venv\Scripts\activate.bat"

REM Ensure dependencies
pip install --quiet numpy matplotlib soundfile scipy

REM If brighten.py exists and bright WAV exists, generate extra-bright
if exist "brighten.py" if exist "samples_gabo_voice_bright.wav" (
    echo Generating extra-bright file...
    python brighten.py
) else (
    echo brighten.py or samples_gabo_voice_bright.wav not found — skipping brightening.
)

REM Analyze available WAVs with your preferred flags
set FLAGS=--save --air-low 2000 --air-high 8000 --decimals 3

if exist "samples_gabo_voice_demo.wav" (
    echo Analyzing samples_gabo_voice_demo.wav ...
    python overtone_analyzer.py "samples_gabo_voice_demo.wav" %FLAGS%
) else (
    echo samples_gabo_voice_demo.wav not found — skipping.
)

if exist "samples_gabo_voice_bright.wav" (
    echo Analyzing samples_gabo_voice_bright.wav ...
    python overtone_analyzer.py "samples_gabo_voice_bright.wav" %FLAGS%
) else (
    echo samples_gabo_voice_bright.wav not found — skipping.
)

if exist "samples_gabo_voice_extra_bright.wav" (
    echo Analyzing samples_gabo_voice_extra_bright.wav ...
    python overtone_analyzer.py "samples_gabo_voice_extra_bright.wav" %FLAGS%
) else (
    echo samples_gabo_voice_extra_bright.wav not found — skipping.
)

echo.
echo ✅ All done. Check for *_spectrum.png, *_bands.png, *_summary.json, *_spectrum.csv
REM Make real comparison plot (requires *_spectrum.csv files)
if exist "compare_spectra.py" (
    echo Creating real comparison plot...
    python compare_spectra.py
) else (
    echo compare_spectra.py not found — skipping plot export.
)
REM Make band-comparison bars (requires *_summary.json files)
if exist "compare_bands.py" (
    echo Creating band comparison chart...
    python compare_bands.py
) else (
    echo compare_bands.py not found — skipping band chart.
)

pause
