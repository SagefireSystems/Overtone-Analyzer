# ================================
# Overtone Analyzer — Auto Runner
# ================================
# Path: C:\Users\gabri\iCloudDrive\Overtone Analyzer Project\run_analysis.ps1

# UTF-8 so emojis/checkmarks render right
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8

$ErrorActionPreference = "Stop"

function Pause-And-Wait($msg) {
  Write-Host ""
  Write-Host $msg -ForegroundColor Green
  Write-Host "Press Enter to close..."
  [void][System.Console]::ReadLine()
}

try {
  # 1) Go to project folder
  Set-Location "C:\Users\gabri\iCloudDrive\Overtone Analyzer Project"
  Write-Host "Folder: $((Get-Location).Path)" -ForegroundColor Cyan

  # 2) Ensure venv exists, then activate (PowerShell uses Activate.ps1)
  if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment .venv ..." -ForegroundColor Yellow
    python -m venv .venv
  }
  Write-Host "Activating virtual environment..." -ForegroundColor Cyan
  & ".\.venv\Scripts\Activate.ps1"

  # 3) Dependencies
  Write-Host "Ensuring dependencies (numpy, matplotlib, soundfile, scipy)..." -ForegroundColor Cyan
  pip install --quiet numpy matplotlib soundfile scipy

  # 4) Ensure brighten.py exists (creates it if missing) — SAFE (no here-string)
  if (-not (Test-Path ".\brighten.py")) {
    $lines = @(
      '# brighten.py — makes an “extra-bright” version of your bright sample',
      'import numpy as np',
      'import soundfile as sf',
      'from scipy.signal import iirfilter, lfilter',
      '',
      'IN_FILE  = "samples_gabo_voice_bright.wav"',
      'OUT_FILE = "samples_gabo_voice_extra_bright.wav"',
      '',
      'y, sr = sf.read(IN_FILE)',
      'if y.ndim > 1:',
      '    y = y.mean(axis=1)',
      '',
      '# 3 kHz high-pass-ish filter -> blend for high-shelf effect',
      'b, a = iirfilter(2, 3000/(sr/2), btype="high", ftype="butter")',
      'y_hp = lfilter(b, a, y)',
      '',
      'blend = 2.5  # raise for more sparkle',
      'y_out = y + blend * y_hp',
      '',
      '# soft clip + normalize',
      'y_out = np.tanh(1.2 * y_out)',
      'y_out /= (np.max(np.abs(y_out)) + 1e-12)',
      '',
      'sf.write(OUT_FILE, y_out, sr)',
      'print(f"✓ Saved {OUT_FILE} at {sr} Hz")'
    )
    Set-Content -Path ".\brighten.py" -Value $lines -Encoding UTF8
    Write-Host "Created brighten.py" -ForegroundColor Yellow
  }

  # 5) Make extra-bright file (if bright exists)
  if (Test-Path "samples_gabo_voice_bright.wav") {
    Write-Host "`nGenerating extra-bright file..." -ForegroundColor Yellow
    python brighten.py
  } else {
    Write-Host "`nsamples_gabo_voice_bright.wav not found — skipping brightening." -ForegroundColor DarkYellow
  }

  # 6) Analyze all available WAVs with your preferred flags
  $flags = @("--save","--air-low","2000","--air-high","8000","--decimals","3")

  $targets = @(
    "samples_gabo_voice_demo.wav",
    "samples_gabo_voice_bright.wav",
    "samples_gabo_voice_extra_bright.wav"
  )

  foreach ($wav in $targets) {
    if (Test-Path $wav) {
      Write-Host "`nAnalyzing $wav ..." -ForegroundColor Yellow
      python overtone_analyzer.py $wav @flags
    } else {
      Write-Host "$wav not found — skipping." -ForegroundColor DarkGray
    }
  }

  Pause-And-Wait "✅ All done. Check the folder for *_spectrum.png, *_bands.png, *_summary.json, *_spectrum.csv"
}
catch {
  Write-Host "`n❌ ERROR:" -ForegroundColor Red
  Write-Host $_.Exception.Message -ForegroundColor Red
  Write-Host "`nStack:" -ForegroundColor DarkGray
  Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
  Write-Host "`nPress Enter to close..." -ForegroundColor Red
  [void][System.Console]::ReadLine()
}
