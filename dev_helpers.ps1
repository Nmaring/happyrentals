Set-StrictMode -Version Latest

function Backup-File {
  param([Parameter(Mandatory=$true)][string]$Path)
  if (!(Test-Path $Path)) { throw "Backup-File: missing file: $Path" }
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $bak = "$Path.bak_$stamp"
  Copy-Item -Force $Path $bak
  Write-Host "✅ backup: $bak"
}

function Show-Lines {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][int]$Start,
    [Parameter(Mandatory=$true)][int]$End
  )
  if (!(Test-Path $Path)) { throw "Show-Lines: missing file: $Path" }
  $lines = Get-Content $Path
  for ($i=$Start; $i -le $End; $i++){
    if ($i -ge 1 -and $i -le $lines.Count) {
      "{0}: {1}" -f $i, $lines[$i-1] | Out-Host
    }
  }
}

function Replace-Regex {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][string]$Pattern,
    [Parameter(Mandatory=$true)][string]$Replacement
  )
  if (!(Test-Path $Path)) { throw "Replace-Regex: missing file: $Path" }
  $txt = Get-Content -Raw $Path
  $new = [regex]::Replace($txt, $Pattern, $Replacement, [System.Text.RegularExpressions.RegexOptions]::Singleline)
  if ($new -eq $txt) {
    Write-Host "⚠️ no change (pattern not found) in $Path"
  } else {
    Set-Content -Encoding UTF8 $Path $new
    Write-Host "✅ patched: $Path"
  }
}

function Find-FirstFile {
  param(
    [Parameter(Mandatory=$true)][string]$Root,
    [Parameter(Mandatory=$true)][string]$Pattern
  )
  $hit = Get-ChildItem -Recurse -Path $Root -Filter *.py |
    Select-String -Pattern $Pattern -List |
    Select-Object -First 1
  if ($null -eq $hit) { return $null }
  return $hit.Path
}
