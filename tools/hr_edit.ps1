function Read-Text([string]$Path){
  [System.IO.File]::ReadAllText($Path)
}

function Write-Utf8NoBom([string]$Path, [string]$Text){
  $enc = [System.Text.UTF8Encoding]::new($false)  # no BOM
  [System.IO.File]::WriteAllText($Path, $Text, $enc)
}

function Backup-File([string]$Path){
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  Copy-Item $Path "$Path.bak_$stamp" -Force
}

function Show-Lines([string]$Path, [int]$Start, [int]$End){
  $lines = Get-Content $Path
  for($i=$Start; $i -le $End; $i++){
    "{0}: {1}" -f $i, $lines[$i-1] | Out-Host
  }
}

function Replace-Regex([string]$Path, [string]$Pattern, [string]$Replacement){
  $txt = Read-Text $Path
  $new = [regex]::Replace($txt, $Pattern, $Replacement)
  if($new -eq $txt){
    Write-Host "WARN: no change made (pattern not found) => $Path"
    return
  }
  Backup-File $Path
  Write-Utf8NoBom $Path $new
  Write-Host "OK: patched => $Path"
}

function Remove-BOM([string]$Path){
  $txt = Read-Text $Path
  $new = $txt -replace "`uFEFF", ""
  if($new -ne $txt){
    Backup-File $Path
    Write-Utf8NoBom $Path $new
    Write-Host "OK: removed BOM => $Path"
  }
}
