cd C:\HappyRentals\backend
$secret = python -c "import secrets; print(secrets.token_urlsafe(48))"
(Get-Content .\.env.saas) -replace '^SECRET_KEY=.*$', "SECRET_KEY=$secret" | Set-Content -Encoding UTF8 .\.env
Write-Host "✅ Updated backend\.env secret key."
