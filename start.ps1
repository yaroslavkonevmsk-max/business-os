# Business OS - One-Click Startup Script
# This script does EVERYTHING automatically:
# 1. Checks if Docker Desktop is running, starts it if not
# 2. Waits for Docker to be ready
# 3. Runs docker compose up --build -d
# 4. Waits for backend to be healthy
# 5. Opens browser with API docs

$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Business OS - Smart Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $null = docker info 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

# Check Docker Desktop
Write-Host "[1/5] Checking Docker Desktop..." -ForegroundColor Yellow
if (-not (Test-DockerRunning)) {
    Write-Host "Docker Desktop is not running. Starting it now..." -ForegroundColor Yellow
    $dockerPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "Waiting for Docker Desktop to start..." -ForegroundColor Yellow
        $timeout = 120
        $elapsed = 0
        while (-not (Test-DockerRunning) -and $elapsed -lt $timeout) {
            Start-Sleep -Seconds 2
            $elapsed += 2
            Write-Host "  ...waiting ($elapsed sec)" -ForegroundColor Gray
        }
        if (-not (Test-DockerRunning)) {
            Write-Host "ERROR: Docker Desktop didn't start in time. Please start it manually." -ForegroundColor Red
            pause
            exit 1
        }
        Write-Host "Docker Desktop is running!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Docker Desktop not found. Please install it from https://docker.com" -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host "Docker Desktop is already running." -ForegroundColor Green
}

# Check .env file
Write-Host ""
Write-Host "[2/5] Checking environment..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host ".env file created from .env.example" -ForegroundColor Green
    } else {
        Write-Host "WARNING: No .env file found. Using default settings." -ForegroundColor Yellow
    }
} else {
    Write-Host ".env file exists." -ForegroundColor Green
}

# Build and start containers
Write-Host ""
Write-Host "[3/5] Building and starting containers..." -ForegroundColor Yellow
Write-Host "This may take 3-5 minutes on first run. Please wait..." -ForegroundColor Cyan
docker compose down 2>$null
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start containers." -ForegroundColor Red
    pause
    exit 1
}
Write-Host "Containers started successfully!" -ForegroundColor Green

# Wait for backend to be ready
Write-Host ""
Write-Host "[4/5] Waiting for backend to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$backendReady = $false
while ($attempt -lt $maxAttempts -and -not $backendReady) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "Backend is ready!" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ...waiting for backend ($attempt/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
}

if (-not $backendReady) {
    Write-Host "WARNING: Backend health check timed out. It may still be starting." -ForegroundColor Yellow
}

# Show status
Write-Host ""
Write-Host "[5/5] Checking services..." -ForegroundColor Yellow
docker compose ps

# Open browser
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Business OS is RUNNING!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  Mini App:     http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "  Opening API Docs in your browser..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  To stop: run ./stop.bat" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Green

Start-Process "http://localhost:8000/docs"

Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
