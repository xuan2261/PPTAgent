# Build Python backend with PyInstaller
Write-Host "Building PPTAgent backend..."

# Clean previous builds
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue

# Build with spec file
Write-Host "Running PyInstaller..."
pyinstaller backend.spec --clean

# Copy to electron-app location
$destDir = "python-dist"
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir }
Copy-Item "dist/backend.exe" -Destination "$destDir/backend.exe" -Force

Write-Host "Build complete: python-dist/backend.exe"
