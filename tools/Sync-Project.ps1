param(
    [Parameter(Mandatory=$true)][ValidateSet('Pull','Push')][string]$Mode,
    [string]$Message = ('project: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repoRoot
if ((git branch --show-current) -ne 'dev') { throw 'Synchronization is allowed only on dev.' }
$remote = git remote get-url origin
if ($remote -notmatch 'github\.com[:/]Pronin-Mike/Final-coil(?:\.git)?$') { throw 'Unexpected origin repository.' }
if (Get-Process UnrealEditor -ErrorAction SilentlyContinue) { throw 'Save the level and close Unreal Editor before synchronization.' }
if ($Mode -eq 'Pull') {
    if (git status --porcelain) { throw 'Local changes exist. Commit/push them first; no files were overwritten.' }
    git pull --ff-only origin dev
    if ($LASTEXITCODE) { throw 'Pull failed; resolve branch divergence manually.' }
    git lfs pull
    if ($LASTEXITCODE) { throw 'Git LFS download failed.' }
} else {
    git add --all
    if ($LASTEXITCODE) { throw 'Staging failed.' }
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 1) {
        git commit -m $Message
        if ($LASTEXITCODE) { throw 'Commit failed.' }
    } elseif ($LASTEXITCODE -ne 0) { throw 'Cannot inspect staged changes.' }
    git push origin dev
    if ($LASTEXITCODE) { throw 'Push failed. Your commit remains local; pull/reconcile before retrying.' }
}
Write-Host 'Synchronization completed.'
