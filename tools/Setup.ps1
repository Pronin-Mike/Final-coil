$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repoRoot
git lfs version
if ($LASTEXITCODE) { throw 'Install Git LFS first.' }
git -c core.hooksPath=.git/hooks lfs install --local
if ($LASTEXITCODE) { throw 'Git LFS setup failed.' }
git config core.hooksPath .githooks
git config pull.ff only
git config merge.ff only
git config fetch.prune true
git config lfs.locksverify false
$branch = git branch --show-current
if ($branch -ne 'dev') { throw 'Switch to dev before editing. This script does not switch a dirty working tree.' }
git lfs pull
if ($LASTEXITCODE) { throw 'Git LFS download failed.' }
Write-Host 'Ready: dev, Git LFS, protected local push, Obsidian vault in obsidian-doc.'
