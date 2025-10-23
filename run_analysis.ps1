
# ================================
# Overtone Analyzer Auto Runner
# ================================

# Make errors stop the script (so we can catch them)
$ErrorActionPreference = "Stop"

# Always keep the window open at the end
function Stop-And-Wait($msg) {
  Write-Host ""
  Write-Host $msg -ForegroundColor Green
  Write-Host "Press Enter to close..."
  [void][System.Console]::ReadLine()
}

try {
  # 1) Go to project folder (quotes handle spaces)
  Set-Location "C:\Users\gabri\iCloudDrive\Overtone Analyzer Project"

  Write-Host "Current folder: $((Get-Location).Path)" -ForegroundColor Cyan

  # 2) Ensure venv exists; if not, create it
  if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual env not found. Creating .venv ..." -ForegroundColor Yellow
    python -m venv .venv
  }

  # 3) Activate (PowerShell uses Activate.ps1)
  Write-Host "Activating virtual environment..." -ForegroundColor Cyan
  & ".\.venv\Scripts\Activate.ps1"

  # 4) Install/ensure deps
  Write-Host "Checking dependencies (numpy, matplotlib, soundfile, scipy)..." -ForegroundColor Cyan
  pip install --quiet numpy matplotlib soundfile scipy

  # 5) Run analyses
  $bright = "samples_gabo_voice_bright.wav"
  $demo   = "samples_gabo_voice_demo.wav"

  if (Test-Path $bright) {
    Write-Host "`nAnalyzing $bright ..." -ForegroundColor Yellow
    python overtone_analyzer.py $bright --save
  } else {
    Write-Host "`n$bright not found — skipping." -ForegroundColor Red
  }

  if (Test-Path $demo) {
    Write-Host "`nAnalyzing $demo ..." -ForegroundColor Yellow
    python overtone_analyzer.py $demo --save
  } else {
    Write-Host "`n$demo not found — skipping." -ForegroundColor DarkYellow
  }

  Stop-And-Wait "✅ Analysis complete. Check for *_spectrum.png, *_bands.png, *_summary.json, *_spectrum.csv"
}
catch {
  Write-Host "`n❌ ERROR:" -ForegroundColor Red
  Write-Host $_.Exception.Message -ForegroundColor Red
  Write-Host "`nStack:" -ForegroundColor DarkGray
  Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
  Write-Host ""
  Write-Host "Tip: Make sure file names are exactly:" -ForegroundColor DarkGray
  Write-Host "  - samples_gabo_voice_bright.wav" -ForegroundColor DarkGray
  Write-Host "  - samples_gabo_voice_demo.wav (optional)" -ForegroundColor DarkGray
  Write-Host ""
  Write-Host "Also check that overtone_analyzer.py is in this folder." -ForegroundColor DarkGray
  Write-Host ""
  Write-Host "If activation fails, ensure this exists: .\.venv\Scripts\Activate.ps1" -ForegroundColor DarkGray
  Write-Host ""
  Write-Host "Press Enter to close..." -ForegroundColor Red
  [void][System.Console]::ReadLine()
}
