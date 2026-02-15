param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Load local Stripe env vars (local file; not committed)
$StripeEnv = "C:\HappyRentals\tools\stripe-env.ps1"
if (Test-Path $StripeEnv) { . $StripeEnv }
$Root = "C:\HappyRentals"
$Frontend = "$Root\frontend"
$Backend  = "$Root\backend"
$Py = "$Backend\.venv\Scripts\python.exe"

# Kill anything on port
Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess |
  Sort-Object -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

# Build frontend
Push-Location $Frontend
npm run build
Pop-Location

# Copy dist -> backend/static
Remove-Item "$Backend\static" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$Backend\static" | Out-Null
Copy-Item "$Frontend\dist\*" "$Backend\static" -Recurse -Force

# Env for SaaS
$env:APP_MODE = "saas"
$env:JWT_SECRET = "change-me-now"
$env:DATABASE_URL = "sqlite:///C:/HappyRentals/backend/saas.db"

# Run SaaS
Start-Process "http://127.0.0.1:$Port/login"
Push-Location $Backend
& $Py -m uvicorn app.saas_main:app --reload --port $Port
Pop-Location


