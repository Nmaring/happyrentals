$ErrorActionPreference = "Stop"

# Kill anything already listening on 8000
$pid = (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1).OwningProcess
if ($pid) { taskkill /PID $pid /F | Out-Null }

Remove-Item .\uvicorn.out.log, .\uvicorn.err.log -ErrorAction SilentlyContinue

Start-Process -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList "-m uvicorn app.saas_main:app --host 127.0.0.1 --port 8000 --log-level info --access-log" `
  -RedirectStandardOutput ".\uvicorn.out.log" `
  -RedirectStandardError ".\uvicorn.err.log" `
  -NoNewWindow

Start-Sleep -Seconds 1

$code = (curl.exe -sS -o NUL -w "%{http_code}" http://127.0.0.1:8000/openapi.json)
"openapi.json => $code"
if ($code -ne "200") {
  "---- uvicorn.err.log ----"
  Get-Content .\uvicorn.err.log -Tail 200
  exit 1
}
