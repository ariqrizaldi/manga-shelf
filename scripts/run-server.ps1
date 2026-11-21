# Menjalankan MangaShelf untuk Tailscale Funnel.
# Loop ini membuat Uvicorn otomatis hidup lagi jika prosesnya berhenti.
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# Cegah dua instance berjalan bersamaan.
$mutex = New-Object System.Threading.Mutex($false, "Local\MangaShelf")
if (-not $mutex.WaitOne(0)) {
    exit 0
}

$log = Join-Path $root "server.log"
while ($true) {
    if ((Test-Path $log) -and ((Get-Item $log).Length -gt 5MB)) {
        Move-Item -Force $log "$log.1"
    }

    & "$root\.venv\Scripts\python.exe" -m uvicorn app.main:app `
        --host 127.0.0.1 `
        --port 8000 `
        --env-file .env *>> $log

    Start-Sleep -Seconds 5
}
