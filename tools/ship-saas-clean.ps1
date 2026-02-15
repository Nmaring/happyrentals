param([int]$Port = 8000)

$ErrorActionPreference="Stop"

$Root="C:\HappyRentals"
$Frontend="$Root\frontend"
$Backend="$Root\backend"
$Py="$Backend\.venv\Scripts\python.exe"

# Optional local Stripe env (won't break param)
$StripeEnv="$Root\tools\stripe-env.ps1"
if(Test-Path $StripeEnv){ . $StripeEnv }

# Stop port
Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
  Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique |
  ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

# Build frontend
Push-Location $Frontend
npm run build
Pop-Location

# Copy dist -> backend/static
Remove-Item "$Backend\static" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$Backend\static" | Out-Null
Copy-Item "$Frontend\dist\*" "$Backend\static" -Recurse -Force

# Run SaaS
$env:APP_MODE="saas"
if(-not $env:JWT_SECRET){ $env:JWT_SECRET="change-me-now" }
if(-not $env:DATABASE_URL){ $env:DATABASE_URL="sqlite:///./saas.db" }
$env:STATIC_DIR="$Backend\static"

Start-Process "http://127.0.0.1:$Port/login" | Out-Null
Push-Location $Backend
& $Py -m uvicorn app.saas_main:app --reload --port $Port
Pop-Location
