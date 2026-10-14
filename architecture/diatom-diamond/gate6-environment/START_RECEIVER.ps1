[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$BindIP,
  [string]$RepoDir = (Join-Path $PSScriptRoot 'oasis'),
  [string]$StateDir = (Join-Path $PSScriptRoot 'gate6-state'),
  [int]$Port = 32443,
  [string]$CrashEvent = ''
)
$ErrorActionPreference='Stop'
$argsList=@((Join-Path $PSScriptRoot 'gate6.mjs'),'serve','--repo',$RepoDir,'--state',$StateDir,'--bind',$BindIP,'--port',"$Port")
if($CrashEvent){$argsList+=@('--test-crash',$CrashEvent);Write-Warning "TEST MODE: receiver will exit code 86 after durable commit of '$CrashEvent' and BEFORE ACK. Use disposable journal only."}
& node @argsList
exit $LASTEXITCODE