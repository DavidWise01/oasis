[CmdletBinding()]
param(
 [Parameter(Mandatory=$true)][string]$ServerIP,
 [Parameter(Mandatory=$true)][string]$EventID,
 [string]$RepoDir = (Join-Path $PSScriptRoot 'oasis'),
 [string]$StateDir = (Join-Path $PSScriptRoot 'gate6-state'),
 [int]$Port = 32443,
 [switch]$ExpectLostACK
)
$ErrorActionPreference='Stop'
$argsList=@((Join-Path $PSScriptRoot 'gate6.mjs'),'send','--repo',$RepoDir,'--state',$StateDir,'--address',$ServerIP,'--port',"$Port",'--event',$EventID)
if($ExpectLostACK){$argsList+=@('--expect-loss','yes')}
& node @argsList
exit $LASTEXITCODE