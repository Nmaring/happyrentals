function Backup-File {
  param([Parameter(Mandatory=$true)][string]$Path)
  $stamp = Get-Date -Format yyyyMMdd_HHmmss
  Copy-Item $Path "$Path.bak_$stamp" -Force
  "$Path.bak_$stamp"
}

function Show-Lines {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [int]$Start = 1,
    [int]$End = 60
  )
  $lines = Get-Content $Path
  for($i=$Start; $i -le $End; $i++){
    if($i -ge 1 -and $i -le $lines.Count){
      "{0}: {1}" -f $i, $lines[$i-1] | Out-Host
    }
  }
}

function Remove-BOM {
  param([Parameter(Mandatory=$true)][string]$Path)
  $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
  $txt = [System.IO.File]::ReadAllText($Path)
  $txt2 = $txt -replace "`uFEFF",""
  [System.IO.File]::WriteAllText($Path, $txt2, $utf8NoBom)
  "Removed BOM/U+FEFF => $Path" | Out-Host
}
