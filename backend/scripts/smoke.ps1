$ErrorActionPreference = "Stop"

$base  = "http://127.0.0.1:8000"
$email = "owner@example.com"
$pw    = "YourPass123!"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$loginJson  = Join-Path $here "login.json"
$cookies    = Join-Path $here "cookies.txt"
$hdrs       = Join-Path $here "login_headers.txt"
$bodyFile   = Join-Path $here "login_body.json"
$tokenFile  = Join-Path $here "token.txt"

@{ email=$email; password=$pw } | ConvertTo-Json -Compress | Set-Content -Encoding ascii $loginJson
Remove-Item $cookies,$hdrs,$bodyFile,$tokenFile -ErrorAction SilentlyContinue

curl.exe -sS -D $hdrs -o $bodyFile -c $cookies -H "Content-Type: application/json" --data-binary "@$loginJson" "$base/api/auth/login" | Out-Null

"LOGIN BODY:"
Get-Content $bodyFile

$token = (Get-Content $bodyFile -Raw | ConvertFrom-Json).access_token
Set-Content -Encoding ascii $tokenFile $token

""
"ME (cookie):"
curl.exe -sS -b $cookies "$base/api/auth/me"
""
"ME (bearer):"
curl.exe -sS -H "Authorization: Bearer $token" "$base/api/auth/me"
""
"Saved token to: $tokenFile"
