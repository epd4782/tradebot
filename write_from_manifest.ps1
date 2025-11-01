param([string]$ManifestPath)

$manifest = Get-Content -LiteralPath $ManifestPath
$path = $null
$buf  = New-Object System.Collections.Generic.List[string]

function Flush-File([string]$p,[System.Collections.Generic.List[string]]$b){
  if(-not $p){ return }
  $dir = Split-Path $p
  if($dir){ [System.IO.Directory]::CreateDirectory($dir) | Out-Null }  # rekursiv
  [System.IO.File]::WriteAllText($p, ($b -join "`r`n"), [System.Text.Encoding]::UTF8)
}

foreach($line in $manifest){
  if($line -like 'BEGIN_MANIFEST*' -or $line -eq 'END_MANIFEST'){ continue }
  if($line -eq '=== END ==='){ Flush-File $path $buf; $path=$null; $buf.Clear(); continue }
  if($line -match '^=== (.+) ===$'){ if($path){ Flush-File $path $buf; $buf.Clear() }; $path=$Matches[1]; continue }
  $buf.Add($line) | Out-Null
}
if($path -and $buf.Count -gt 0){ Flush-File $path $buf }
Write-Host "✅ Manifest verarbeitet: $ManifestPath"
