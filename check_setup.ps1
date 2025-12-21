# Voice Assistant - Dependency Check Script
# This script checks if all required dependencies are properly installed

Write-Host ""
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "Voice Assistant - Dependency Check" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check if FFmpeg is in PATH
Write-Host "Checking FFmpeg..." -ForegroundColor Yellow
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "  ✅ FFmpeg is installed and in PATH" -ForegroundColor Green
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "  Version: $ffmpegVersion" -ForegroundColor Gray
} else {
    Write-Host "  ❌ FFmpeg not found in PATH" -ForegroundColor Red
    Write-Host "  Please install FFmpeg - see SETUP_DEPENDENCIES.md" -ForegroundColor Yellow
    $allGood = $false
}

# Check if Piper exists (check multiple possible locations)
Write-Host "`nChecking Piper..." -ForegroundColor Yellow
$piperPaths = @(".\piper\piper.exe", ".\piper\piper\piper.exe")
$piperFound = $false
foreach ($piperPath in $piperPaths) {
    if (Test-Path $piperPath) {
        Write-Host "  ✅ Piper is installed at: $piperPath" -ForegroundColor Green
        $piperSize = (Get-Item $piperPath).Length / 1MB
        Write-Host "  Size: $([math]::Round($piperSize, 2)) MB" -ForegroundColor Gray
        $piperFound = $true
        break
    }
}
if (-not $piperFound) {
    Write-Host "  ❌ Piper not found at any expected location" -ForegroundColor Red
    Write-Host "  Expected: .\piper\piper.exe or .\piper\piper\piper.exe" -ForegroundColor Yellow
    Write-Host "  Download from: https://github.com/rhasspy/piper/releases" -ForegroundColor Yellow
    $allGood = $false
}

# Check if voice model exists
Write-Host "`nChecking Voice Model..." -ForegroundColor Yellow
$voicePaths = @(".\voices\en_US-lessac-medium.onnx", ".\piper\voices\en_US-lessac-medium.onnx")
$voiceFound = $false
foreach ($voicePath in $voicePaths) {
    if (Test-Path $voicePath) {
        Write-Host "  ✅ Voice model is installed at: $voicePath" -ForegroundColor Green
        $voiceSize = (Get-Item $voicePath).Length / 1MB
        Write-Host "  Size: $([math]::Round($voiceSize, 2)) MB" -ForegroundColor Gray
        $voiceFound = $true
        break
    }
}
if (-not $voiceFound) {
    Write-Host "  ❌ Voice model not found at any expected location" -ForegroundColor Red
    Write-Host "  Expected: .\voices\ or .\piper\voices\" -ForegroundColor Yellow
    Write-Host "  Download from: https://github.com/rhasspy/piper/releases" -ForegroundColor Yellow
    $allGood = $false
}

# Check if Python is available
Write-Host "`nChecking Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "  ✅ Python is installed" -ForegroundColor Green
    $pythonVersion = python --version 2>&1
    Write-Host "  Version: $pythonVersion" -ForegroundColor Gray
} else {
    Write-Host "  ❌ Python not found" -ForegroundColor Red
    $allGood = $false
}

# Check if required Python packages are installed
Write-Host "`nChecking Python Packages..." -ForegroundColor Yellow
$packageChecks = @{
    "openai-whisper" = "whisper"
    "sounddevice" = "sounddevice"
    "soundfile" = "soundfile"
    "ollama" = "ollama"
    "colorama" = "colorama"
    "python-dotenv" = "dotenv"
}
$missingPackages = @()

foreach ($packageName in $packageChecks.Keys) {
    $importName = $packageChecks[$packageName]
    $result = python -c "import $importName; print('OK')" 2>&1 | Out-String
    if ($result -match "OK") {
        Write-Host "  ✅ $packageName" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $packageName (missing)" -ForegroundColor Red
        $missingPackages += $packageName
        $allGood = $false
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "`n  Install missing packages with:" -ForegroundColor Yellow
    Write-Host "  pip install $($missingPackages -join ' ')" -ForegroundColor Cyan
}

# Check if Ollama is running
Write-Host "`nChecking Ollama..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5 -UseBasicParsing 2>$null
    Write-Host "  ✅ Ollama is running at http://localhost:11434" -ForegroundColor Green
    
    # Try to parse models
    try {
        $models = ($response.Content | ConvertFrom-Json).models
        if ($models.Count -gt 0) {
            Write-Host "  Available models:" -ForegroundColor Gray
            foreach ($model in $models) {
                Write-Host "    - $($model.name)" -ForegroundColor Gray
            }
        }
    } catch {
        # Ignore parsing errors
    }
} catch {
    Write-Host "  ❌ Ollama is not running or not accessible" -ForegroundColor Red
    Write-Host "  Start Ollama with: ollama serve" -ForegroundColor Yellow
    Write-Host "  Or download from: https://ollama.com" -ForegroundColor Yellow
    $allGood = $false
}

# Check if config file exists
Write-Host "`nChecking Configuration..." -ForegroundColor Yellow
if (Test-Path ".\config.py") {
    Write-Host "  ✅ config.py found" -ForegroundColor Green
} else {
    Write-Host "  ❌ config.py not found" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path ".\.env") {
    Write-Host "  ✅ .env file found (custom configuration)" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  .env file not found (using defaults)" -ForegroundColor Cyan
}

# Final summary
Write-Host ""
Write-Host "="*60 -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✅ All dependencies are installed!" -ForegroundColor Green
    Write-Host "You can run the voice assistant with: python voice_assistant.py" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Some dependencies are missing" -ForegroundColor Yellow
    Write-Host "Please check SETUP_DEPENDENCIES.md for installation instructions" -ForegroundColor Yellow
}
Write-Host "="*60 -ForegroundColor Cyan
Write-Host ""
