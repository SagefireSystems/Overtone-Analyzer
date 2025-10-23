# Overtone Analyzer — Simple Auto Runner (no try/catch, no here-strings)

# UTF-8 so emojis/checkmarks render right
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8

# 1) Go to project folder
Set-Location "C:\Users\gabri\iCloudDrive\Overtone Analyzer Project"
Write-Host "Folder: $((Get-Location).Path)" -ForegroundColor Cyan

# 2) Ensure venv exists, then activate
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
  Write-Host "Creating virtual environment .venv ..." -ForegroundColor Yellow
  python -m venv .venv
}
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"

# 3) Dependencies
Write-Host "Ensuring dependencies (numpy, matplotlib, soundfile, scipy)..." -ForegroundColor Cyan
pip install --quiet numpy matplotlib soundfile scipy

# 4) Make extra-bright file if bright exists (requires brighten.py you already created)
if (Test-Path ".\brighten.py" -and Test-Path "samples_gabo_voice_bright.wav") {
  Write-Host "`nGenerating extra-bright file..." -ForegroundColor Yellow
  python brighten.py
} else {
  Write-Host "`nbrighten.py or samples_gabo_voice_bright.wav not found — skipping brightening." -ForegroundColor DarkYellow
}

# 5) Analyze available WAVs
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

Write-Host "`n✅ All done. Check for *_spectrum.png, *_bands.png, *_summary.json, *_spectrum.csv" -ForegroundColor Green
Read-Host "Press Enter to close"
