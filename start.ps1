$ErrorActionPreference="Stop"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND  = Join-Path $ROOT "backend"
$FRONTEND = Join-Path $ROOT "frontend"

Start-Process powershell -WorkingDirectory $BACKEND -ArgumentList @(
  "-NoExit",
  "-Command",
  @"
`$ErrorActionPreference='Stop'
cd '$BACKEND'
`$env:PYTHONPATH = (Get-Location).Path
`$PY='.\.venv\Scripts\python.exe'; if(!(Test-Path `$PY)){ `$PY='python' }
& `$PY -m uvicorn app.main:app --app-dir . --host 127.0.0.1 --port 8000 --reload
"@
)

Start-Process powershell -WorkingDirectory $FRONTEND -ArgumentList @(
  "-NoExit",
  "-Command",
  @"
`$ErrorActionPreference='Stop'
cd '$FRONTEND'
npm run dev
"@
)

Write-Host ""
Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host ""
