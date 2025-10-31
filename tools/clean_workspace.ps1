# Clean unnecessary build and cache artifacts from the workspace
# Usage (PowerShell):
#   pwsh -File .\tools\clean_workspace.ps1
#   # or
#   powershell -ExecutionPolicy Bypass -File .\tools\clean_workspace.ps1

$ErrorActionPreference = 'SilentlyContinue'

$root = Split-Path -Parent $PSCommandPath
$repo = Split-Path $root -Parent
$engine = Join-Path $repo 'infinite-tower-engine'
$src = Join-Path $engine 'src\infinite_tower'

Write-Host 'Cleaning workspace...' -ForegroundColor Cyan

# Remove engine build artifacts
$buildDir = Join-Path $engine 'build'
if (Test-Path $buildDir) {
  Write-Host " - Removing: $buildDir"
  Remove-Item -LiteralPath $buildDir -Recurse -Force
}

# Remove pytest cache
$pytestCache = Join-Path $engine '.pytest_cache'
if (Test-Path $pytestCache) {
  Write-Host " - Removing: $pytestCache"
  Remove-Item -LiteralPath $pytestCache -Recurse -Force
}

# Remove all __pycache__ folders
$pycaches = Get-ChildItem -LiteralPath $src -Directory -Recurse -Filter '__pycache__'
foreach ($d in $pycaches) {
  Write-Host " - Removing: $($d.FullName)"
  Remove-Item -LiteralPath $d.FullName -Recurse -Force
}

Write-Host 'Done.' -ForegroundColor Green
