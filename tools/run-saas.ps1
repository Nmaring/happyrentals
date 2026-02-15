param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Load local Stripe env vars (local file; not committed)
$StripeEnv = "C:\HappyRentals\tools\stripe-env.ps1"
if (Test-Path $StripeEnv) { . $StripeEnv }
$Root = "C:\HappyRentals"
$Backend = "$Root\backend"
$Py = "$Backend\.venv\Scripts\python.exe"

$env:APP_MODE = "saas"
$env:JWT_SECRET = "change-me-now"
$env:DATABASE_URL = "sqlite:///C:/HappyRentals/backend/saas.db"

Push-Location $Backend
& $Py -m uvicorn app.saas_main:app --reload --port $Port
Pop-Location

