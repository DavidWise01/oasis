# Windows PowerShell 5.1+ | Run from an ordinary user PowerShell terminal.
# Downloads only the public repository. No automatic package installation or elevation.
[CmdletBinding()]
param(
  [string]$RepoDir = (Join-Path $PSScriptRoot 'oasis'),
  [string]$StateDir = (Join-Path $PSScriptRoot 'gate6-state'),
  [string]$PinnedCommit = '0f1447ece052d0434edad58f57784392116d59d8',
  [switch]$ProvisionKeys,
  [switch]$SkipLocalTest
)
$ErrorActionPreference = 'Stop'
$RepoDir = [System.IO.Path]::GetFullPath($RepoDir)
$StateDir = [System.IO.Path]::GetFullPath($StateDir)
if ($StateDir.StartsWith($RepoDir + [System.IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'State directory must be outside the Git repo. It will contain private keys.' }
foreach ($cmd in @('git','node','openssl')) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {throw "Missing '$cmd'. Install it, open a new PowerShell terminal, rerun. See README.md."}
}
$v = (& node -p 'Number(process.versions.node.split(".")[0])'); if ([int]$v -lt 22) {throw 'Node.js >=22 required.'}
if (-not (Test-Path -LiteralPath (Join-Path $RepoDir '.git'))) {
  Write-Host "Cloning public OASIS repository into $RepoDir" -ForegroundColor Cyan
  & git clone 'https://github.com/DavidWise01/oasis.git' $RepoDir
  if ($LASTEXITCODE -ne 0) {throw 'git clone failed'}
  & git -C $RepoDir checkout --detach $PinnedCommit
  if ($LASTEXITCODE -ne 0) {throw 'Could not select pinned release commit'}
} else {
  Write-Warning 'Using your existing git checkout; not modifying branch or working tree. Validate source hash below.'
}
$meta = @{repo=$RepoDir;state=$StateDir;source='DavidWise01/oasis';pin=$PinnedCommit;created=(Get-Date).ToUniversalTime().ToString('o')}
$meta | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -LiteralPath (Join-Path $PSScriptRoot 'bootstrap-local.json')
Write-Host 'Checking release dependencies and pinned frozen hash...' -ForegroundColor Cyan
& node (Join-Path $PSScriptRoot 'gate6.mjs') doctor --repo $RepoDir --state $StateDir
if ($LASTEXITCODE -ne 0) {throw 'Preflight failed. Do not proceed.'}
if (-not $SkipLocalTest) {
  Write-Host 'Running existing RC1 local mTLS crash/replay suite...' -ForegroundColor Cyan
  & node (Join-Path $PSScriptRoot 'local_smoke.mjs') --repo $RepoDir
  if ($LASTEXITCODE -ne 0) {throw 'Local mTLS test failed.'}
}
if ($ProvisionKeys) {
  Write-Host 'Generating unique credentials outside git...' -ForegroundColor Cyan
  & node (Join-Path $PSScriptRoot 'gate6.mjs') prepare --repo $RepoDir --state $StateDir
  if ($LASTEXITCODE -ne 0) {throw 'Key provisioning failed.'}
}
Write-Host 'ENVIRONMENT READY: code checked and local dependencies resolved. Hardware Gate 6 not claimed.' -ForegroundColor Green
Write-Host 'Next: see README.md for receiver/server and sender/client commands.'