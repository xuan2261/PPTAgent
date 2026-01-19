param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern("^\d+\.\d+\.\d+$")]
    [string]$Version
)

Write-Host "Bumping version to $Version..."

$packageJson = Get-Content "electron-app/package.json" -Raw | ConvertFrom-Json
$packageJson.version = $Version
$packageJson | ConvertTo-Json -Depth 10 | Set-Content "electron-app/package.json"

git add electron-app/package.json
git commit -m "chore: bump version to v$Version"
git tag "v$Version"

Write-Host "Version bumped. Run 'git push && git push --tags' to trigger build."
