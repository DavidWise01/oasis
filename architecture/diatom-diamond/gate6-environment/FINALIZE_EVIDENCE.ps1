[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$CrashEvent,
 [ValidateSet('vm','physical','loopback')][string]$Mode='vm',
 [string]$StateDir = (Join-Path $PSScriptRoot 'gate6-state')
)
& node (Join-Path $PSScriptRoot 'gate6.mjs') finalize --state $StateDir --event $CrashEvent --mode $Mode
exit $LASTEXITCODE