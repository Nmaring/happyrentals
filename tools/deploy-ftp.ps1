param(
  [Parameter(Mandatory=$true)][string]$Host,
  [Parameter(Mandatory=$true)][string]$User,
  [Parameter(Mandatory=$true)][string]$RemotePath,
  [string]$LocalPath = "C:\HappyRentals\frontend\dist",
  [ValidateSet("ftp","ftps","sftp")][string]$Protocol = "sftp",
  [int]$Port = 22
)

$ErrorActionPreference = "Stop"

# Prompt for password so it isn't stored in the script
$pw = Read-Host "Password for $User@$Host" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pw)
$Plain = [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR) | Out-Null

$WinSCP = "$env:USERPROFILE\scoop\apps\winscp\current\WinSCP.com"
if (!(Test-Path $WinSCP)) { throw "WinSCP.com not found at $WinSCP" }
if (!(Test-Path $LocalPath)) { throw "LocalPath not found: $LocalPath" }

# Build session URL
# For FTP/FTPS: use port 21
if ($Protocol -in @("ftp","ftps")) { $Port = 21 }

$session = "{0}://{1}:{2}@{3}:{4}/" -f $Protocol, $User, $Plain, $Host, $Port

# Write a temp WinSCP script
$tmp = New-TemporaryFile
@"
option batch abort
option confirm off
open "$session"
synchronize remote -delete "$LocalPath" "$RemotePath"
exit
"@ | Set-Content -Path $tmp -Encoding ASCII

# Run it
& $WinSCP "/script=$($tmp.FullName)" "/log=C:\HappyRentals\release\winscp-deploy.log"

Remove-Item $tmp -Force
Write-Host "✅ Deployed. Log: C:\HappyRentals\release\winscp-deploy.log"
