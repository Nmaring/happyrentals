$ErrorActionPreference="Stop"
$base="http://127.0.0.1:8000"

# must return 200
$code = (curl.exe -sS -o NUL -w "%{http_code}" "$base/openapi.json")
"openapi: $code"

# log in -> cookie
Set-Location $HOME
@{ email="owner@example.com"; password="YourPass123!" } | ConvertTo-Json -Compress | Set-Content -Encoding ascii .\login.json
Remove-Item .\cookies.txt,. \login_body.json -ErrorAction SilentlyContinue

curl.exe -sS -c .\cookies.txt -o .\login_body.json -H "Content-Type: application/json" --data-binary "@login.json" "$base/api/auth/login" | Out-Null
"login_body:"
Get-Content .\login_body.json

"me:"
curl.exe -sS -b .\cookies.txt "$base/api/auth/me"
