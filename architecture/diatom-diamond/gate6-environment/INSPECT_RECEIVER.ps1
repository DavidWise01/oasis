[CmdletBinding()]
param([string]$StateDir = (Join-Path $PSScriptRoot 'gate6-state'))
& node (Join-Path $PSScriptRoot 'gate6.mjs') inspect --state $StateDir
exit $LASTEXITCODE