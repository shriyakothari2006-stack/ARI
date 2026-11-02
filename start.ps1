#!/usr/bin/env pwsh
# ARI — Start Backend + Frontend
# Usage: .\start.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host ""
Write-Host "  ✨ ARI — Multilingual RAG Knowledge Assistant" -ForegroundColor Magenta
Write-Host "  Starting backend (FastAPI) and frontend (Vite)..." -ForegroundColor Cyan
Write-Host ""

# ── Backend ────────────────────────────────────────────────────
$backendDir = Join-Path $root "backend"
$venvPython = Join-Path $backendDir ".venv\Scripts\uvicorn.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "  [ERROR] Backend venv not found. Run:" -ForegroundColor Red
    Write-Host "    cd backend; uv venv --python 3.11; uv pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

$envFile = Join-Path $backendDir ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "  [WARN] No .env found. Copying .env.example → .env" -ForegroundColor Yellow
    Copy-Item (Join-Path $backendDir ".env.example") $envFile
    Write-Host "  [ACTION REQUIRED] Add your XAI_API_KEY to backend\.env" -ForegroundColor Yellow
}

Write-Host "  → Backend: http://localhost:8000  (Docs: http://localhost:8000/docs)" -ForegroundColor Green
$backendProcess = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoProfile -Command `"Set-Location '$backendDir'; & '$venvPython' app.main:app --reload --host 127.0.0.1 --port 8000`"" `
    -PassThru -WindowStyle Normal

Start-Sleep -Seconds 2

# ── Frontend ───────────────────────────────────────────────────
$frontendDir = Join-Path $root "frontend"
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Host "  [ERROR] node_modules not found. Run:" -ForegroundColor Red
    Write-Host "    cd frontend; npm install" -ForegroundColor Yellow
    $backendProcess | Stop-Process -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "  → Frontend: http://localhost:5173" -ForegroundColor Green
$frontendProcess = Start-Process -FilePath "powershell.exe" `
    -ArgumentList "-NoProfile -Command `"Set-Location '$frontendDir'; npm run dev`"" `
    -PassThru -WindowStyle Normal

Write-Host ""
Write-Host "  Both servers running. Press Ctrl+C or close this window to stop." -ForegroundColor Cyan
Write-Host "  Open: http://localhost:5173" -ForegroundColor Magenta
Write-Host ""

# Wait for either process to exit
try {
    Wait-Process -Id $backendProcess.Id, $frontendProcess.Id -ErrorAction SilentlyContinue
} finally {
    Write-Host "  Shutting down..." -ForegroundColor Yellow
    $backendProcess | Stop-Process -ErrorAction SilentlyContinue
    $frontendProcess | Stop-Process -ErrorAction SilentlyContinue
}
