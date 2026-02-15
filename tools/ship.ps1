param(
  [int]$Port = 8010,
  [switch]$Background,
  [switch]$Smoke
)

$ErrorActionPreference = "Stop"

$Root    = "C:\HappyRentals"
$Frontend= "$Root\frontend"
$Backend = "$Root\backend"
$Py      = "$Backend\.venv\Scripts\python.exe"
$Exe     = "$Root\release\HappyRentals.exe"

# Stop EXE + free port
Get-Process HappyRentals -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
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

# FAIL FAST: backend import must succeed before PyInstaller
Push-Location $Backend
& $Py -c "from app.main import app; print('backend import OK')"
Pop-Location

# Build EXE (bundles static + app)
Push-Location $Backend
Remove-Item ".\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".\dist"  -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".\HappyRentals.spec" -Force -ErrorAction SilentlyContinue

& $Py -m PyInstaller `
  --noconfirm `
  --clean `
  --name HappyRentals `
  --onefile `
  --console `
  --paths "." `
  --add-data "static;static" `
  --add-data "app;app" `
  run_happyrentals.py
Pop-Location

Copy-Item "$Backend\dist\HappyRentals.exe" $Exe -Force

# Run
Remove-Item Env:DB_PATH -ErrorAction SilentlyContinue
$env:PORT = "$Port"

if ($Background) {
  Start-Process powershell -ArgumentList "-NoExit","-Command",('$env:PORT="'+$Port+'"; & "'+$Exe+'"')
} else {
  & $Exe
}

# Optional smoke test (only works if Background is on)
if ($Smoke -and $Background) {
  $base = "http://127.0.0.1:$Port"

  $ok = $false
  for ($i=0; $i -lt 80; $i++) {
    try {
      $r = Invoke-WebRequest "$base/api/health" -UseBasicParsing -TimeoutSec 1
      if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch {}
    Start-Sleep -Milliseconds 250
  }
  if (!$ok) { throw "Smoke: server not responding on $base" }

  # Create property
  $prop = Invoke-RestMethod -Method Post -Uri "$base/api/properties" -ContentType "application/json" -Body (@{
    name="Smoke Property"
    address1="123 Main"
    city="Minneapolis"
    state="MN"
    zip="55406"
  } | ConvertTo-Json)

  # Create tenant
  $tenant = Invoke-RestMethod -Method Post -Uri "$base/api/tenants" -ContentType "application/json" -Body (@{
    first_name="Smoke"
    last_name="Tenant"
    email="smoke@example.com"
    phone="555-555-5555"
  } | ConvertTo-Json)
  # Create unit
  $unit = Invoke-RestMethod -Method Post -Uri "$base/api/units" -ContentType "application/json" -Body (@{
    property_id=$prop.id
    unit_number="1A"
  } | ConvertTo-Json)

  # Create lease (tenant_id optional in some builds; include it)
  $lease = Invoke-RestMethod -Method Post -Uri "$base/api/leases" -ContentType "application/json" -Body (@{
    unit_id=$unit.id
    tenant_id=$tenant.id
    monthly_rent=1500
  } | ConvertTo-Json)

  # Record payment
  $pay = Invoke-RestMethod -Method Post -Uri "$base/api/payments" -ContentType "application/json" -Body (@{
    lease_id=$lease.id
    amount=1500
    payment_date=(Get-Date -Format "yyyy-MM-dd")
    method="manual"
  } | ConvertTo-Json)

  Write-Host "SMOKE OK:"
  Write-Host ("  property_id=" + $prop.id)
  Write-Host ("  tenant_id=" + $tenant.id)
  Write-Host ("  unit_id=" + $unit.id)
  Write-Host ("  lease_id=" + $lease.id)
  Write-Host ("  payment_id=" + $pay.id)
}



