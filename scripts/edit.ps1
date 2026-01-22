[CmdletBinding(DefaultParameterSetName="Help")]
param(
  # Common
  [Parameter(ParameterSetName="Replace", Mandatory=$true)]
  [Parameter(ParameterSetName="Append", Mandatory=$true)]
  [Parameter(ParameterSetName="FixBom", Mandatory=$true)]
  [Parameter(ParameterSetName="RemoveStrayGt", Mandatory=$true)]
  [Parameter(ParameterSetName="Show", Mandatory=$true)]
  [string]$File,

  [Parameter(ParameterSetName="Replace", Mandatory=$true)]
  [string]$Find,

  [Parameter(ParameterSetName="Replace", Mandatory=$true)]
  [string]$With,

  [Parameter(ParameterSetName="Append", Mandatory=$true)]
  [string]$Text,

  [Parameter(ParameterSetName="Show")]
  [int]$Start = 1,

  [Parameter(ParameterSetName="Show")]
  [int]$End = 60,

  [Parameter(ParameterSetName="Replace")]
  [switch]$Literal,

  [Parameter(ParameterSetName="Replace")]
  [switch]$Singleline,

  [Parameter(ParameterSetName="Replace")]
  [Parameter(ParameterSetName="Append")]
  [Parameter(ParameterSetName="FixBom")]
  [Parameter(ParameterSetName="RemoveStrayGt")]
  [switch]$NoBackup,

  # Actions
  [Parameter(ParameterSetName="Replace", Mandatory=$true)]
  [switch]$DoReplace,

  [Parameter(ParameterSetName="Append", Mandatory=$true)]
  [switch]$DoAppend,

  [Parameter(ParameterSetName="FixBom", Mandatory=$true)]
  [switch]$DoFixBom,

  [Parameter(ParameterSetName="RemoveStrayGt", Mandatory=$true)]
  [switch]$DoRemoveStrayGt,

  [Parameter(ParameterSetName="Show", Mandatory=$true)]
  [switch]$DoShow,

  [Parameter(ParameterSetName="Help")]
  [switch]$Help
)

function Backup-File([string]$p){
  if($NoBackup){ return }
  if(!(Test-Path $p)){ throw "Missing file: $p" }
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  Copy-Item $p "$p.bak_$stamp" -Force
}

function Write-Utf8NoBom([string]$p, [string]$content){
  $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
  [System.IO.File]::WriteAllText($p, $content, $utf8NoBom)
}

if($Help -or $PSCmdlet.ParameterSetName -eq "Help"){
@"
Usage examples:

# Replace (regex)
.\scripts\edit.ps1 -DoReplace -File "C:\HappyRentals\frontend\src\App.jsx" -Find 'path="/payments"' -With 'path="/payments/*"'

# Replace (literal string)
.\scripts\edit.ps1 -DoReplace -Literal -File "C:\x\a.txt" -Find 'foo' -With 'bar'

# Append text
.\scripts\edit.ps1 -DoAppend -File "C:\x\a.txt" -Text "hello`n"

# Fix BOM / remove U+FEFF
.\scripts\edit.ps1 -DoFixBom -File "C:\HappyRentals\backend\app\db_compat.py"

# Remove lines that are just '>'
.\scripts\edit.ps1 -DoRemoveStrayGt -File "C:\HappyRentals\frontend\src\pages\LeasesPage.jsx"

# Show lines (1-indexed)
.\scripts\edit.ps1 -DoShow -File "C:\HappyRentals\frontend\src\pages\LeasesPage.jsx" -Start 240 -End 280
"@ | Write-Host
  exit 0
}

# --- Actions ---
switch($PSCmdlet.ParameterSetName){

  "Replace" {
    Backup-File $File
    $t = Get-Content -Raw $File

    if($Singleline){
      # PowerShell regex '.' doesn't match newline by default; use (?s)
      $Find2 = "(?s)$Find"
    } else {
      $Find2 = $Find
    }

    if($Literal){
      $t2 = $t.Replace($Find, $With)
    } else {
      $t2 = [regex]::Replace($t, $Find2, $With)
    }

    Write-Utf8NoBom $File $t2
    "✅ Replaced in $File" | Write-Host
  }

  "Append" {
    Backup-File $File
    Add-Content -Encoding UTF8 -Path $File -Value $Text
    "✅ Appended to $File" | Write-Host
  }

  "FixBom" {
    Backup-File $File
    $t = [System.IO.File]::ReadAllText($File)
    $t2 = $t -replace "`uFEFF",""
    Write-Utf8NoBom $File $t2
    "✅ Cleaned BOM/FEFF in $File" | Write-Host
  }

  "RemoveStrayGt" {
    Backup-File $File
    $lines = Get-Content $File
    $lines = $lines | Where-Object { $_ -notmatch '^\s*>\s*$' }
    # also fix "/> >" on same line
    for($i=0; $i -lt $lines.Count; $i++){
      $lines[$i] = $lines[$i] -replace '(/>\s*)>', '$1'
    }
    Set-Content -Encoding UTF8 -Path $File -Value $lines
    "✅ Removed stray '>' tokens in $File" | Write-Host
  }

  "Show" {
    if(!(Test-Path $File)){ throw "Missing file: $File" }
    $lines = Get-Content $File
    $s = [Math]::Max(1, $Start)
    $e = [Math]::Min($lines.Count, $End)
    "`n--- $File lines $s to $e ---" | Write-Host
    for($i=$s; $i -le $e; $i++){
      "{0}: {1}" -f $i, $lines[$i-1] | Write-Host
    }
    "`n--- end ---`n" | Write-Host
  }

  default {
    throw "Unknown action."
  }
}
