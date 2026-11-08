# Cut a release tag from main. CD does the rest (PyPI + GitHub Release).
# Usage: .\scripts\cut_release.ps1
# Optional: .\scripts\cut_release.ps1 -Push

param(
    [switch]$Push
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$py = (Select-String -Path pyproject.toml -Pattern '^version\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
$init = (Select-String -Path src/sentinelrag/__init__.py -Pattern '__version__\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
if ($py -ne $init) {
    throw "Version mismatch: pyproject=$py __init__=$init"
}

$tag = "v$py"
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
if ($branch -ne "main") {
    throw "Cut releases from main (current: $branch)"
}

git fetch origin --tags
if (git rev-parse "$tag" 2>$null) {
    throw "Tag $tag already exists"
}

Write-Host "Creating annotated tag $tag"
git tag -a $tag -m "Release $tag"

if ($Push) {
    git push origin $tag
    Write-Host "Pushed $tag — watch Actions: publish workflow"
} else {
    Write-Host "Tag created locally. Push with: git push origin $tag"
    Write-Host "Or re-run: .\scripts\cut_release.ps1 -Push"
}
