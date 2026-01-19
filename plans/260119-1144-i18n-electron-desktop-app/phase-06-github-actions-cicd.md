# Phase 6: GitHub Actions CI/CD

## Context Links
- [Plan Overview](plan.md)
- [Phase 3: Electron Setup](phase-03-electron-project-setup.md)
- [Phase 4: Backend Bundling](phase-04-python-backend-bundling.md)
- [Electron Research](research/researcher-01-electron-python-integration.md)

## Overview
- **Priority**: P2
- **Status**: pending
- **Effort**: 3h
- **Description**: Create GitHub Actions workflow for automated Windows builds and releases

## Key Insights
- Tag-based releases (`v1.0.0`) trigger builds
- Windows runner: `windows-latest`
- electron-builder `--publish always` uploads to GitHub Releases
- GH_TOKEN from GITHUB_TOKEN secret
- Cache npm and pip for faster builds

## Requirements

### Functional
- Build triggered on version tags
- Python backend built with PyInstaller
- Electron app built with electron-builder
- Installer uploaded to GitHub Releases
- Auto-update works from releases

### Non-Functional
- Build time <30min
- Reliable caching
- Clear build logs

## Architecture

```
Push tag v1.0.0
        │
        ▼
GitHub Actions Workflow
        │
        ├── Setup Python 3.11
        │   └── pip install + PyInstaller
        │
        ├── Build backend.exe
        │   └── Copy to python-dist/
        │
        ├── Setup Node.js 20
        │   └── npm ci
        │
        ├── Build Electron
        │   └── electron-builder --win --publish always
        │
        └── Upload to GitHub Releases
            ├── PPTAgent-Setup-1.0.0.exe
            └── latest.yml (for auto-update)
```

## Related Code Files

### Create
- `D:/NCKH_2025/PPTAgent/.github/workflows/build-desktop.yml`
- `D:/NCKH_2025/PPTAgent/.github/workflows/test-build.yml` (optional)

## Implementation Steps

### Step 1: Create main build workflow
```yaml
# .github/workflows/build-desktop.yml
name: Build Windows Desktop

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      publish:
        description: 'Publish to GitHub Releases'
        required: false
        default: 'false'
        type: boolean

jobs:
  build-windows:
    runs-on: windows-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      # Python setup and backend build
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller
          pip install -e deeppresenter
          pip install gradio platformdirs python-pptx playwright

      - name: Build Python backend
        run: |
          pyinstaller backend.spec --clean
          mkdir -p python-dist
          cp dist/backend.exe python-dist/

      # Node.js setup and Electron build
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
          cache-dependency-path: electron-app/package-lock.json

      - name: Install npm dependencies
        working-directory: electron-app
        run: npm ci

      - name: Build Electron app
        working-directory: electron-app
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          if ("${{ github.event_name }}" -eq "push") {
            npx electron-builder --win --publish always
          } elseif ("${{ inputs.publish }}" -eq "true") {
            npx electron-builder --win --publish always
          } else {
            npx electron-builder --win
          }

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: windows-installer
          path: |
            electron-app/dist/*.exe
            electron-app/dist/latest.yml
          if-no-files-found: error
```

### Step 2: Create test build workflow (PR validation)
```yaml
# .github/workflows/test-build.yml
name: Test Build

on:
  pull_request:
    paths:
      - 'electron-app/**'
      - 'backend.py'
      - 'backend.spec'
      - 'webui.py'
      - '.github/workflows/build-desktop.yml'

jobs:
  test-build:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Verify PyInstaller spec
        run: |
          pip install pyinstaller
          pyinstaller --help

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Verify Electron setup
        working-directory: electron-app
        run: |
          npm ci
          npx electron-builder --help
```

### Step 3: Add version bump script
```powershell
# scripts/bump-version.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern("^\d+\.\d+\.\d+$")]
    [string]$Version
)

Write-Host "Bumping version to $Version..."

# Update package.json
$packageJson = Get-Content "electron-app/package.json" -Raw | ConvertFrom-Json
$packageJson.version = $Version
$packageJson | ConvertTo-Json -Depth 10 | Set-Content "electron-app/package.json"

# Create git tag
git add electron-app/package.json
git commit -m "chore: bump version to v$Version"
git tag "v$Version"

Write-Host "Version bumped. Run 'git push && git push --tags' to trigger build."
```

### Step 4: Create release checklist
```markdown
# Release Checklist

## Pre-release
- [ ] All tests passing
- [ ] Version bumped in package.json
- [ ] CHANGELOG updated
- [ ] Documentation updated

## Release
1. Run: `.\scripts\bump-version.ps1 -Version X.Y.Z`
2. Run: `git push && git push --tags`
3. Monitor GitHub Actions build
4. Verify release assets uploaded

## Post-release
- [ ] Test installer on clean Windows VM
- [ ] Verify auto-update works
- [ ] Announce release
```

### Step 5: Configure electron-builder for auto-update
Ensure `electron-app/package.json` has correct publish config:
```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "icip-cas",
      "repo": "PPTAgent",
      "releaseType": "release"
    }
  }
}
```

### Step 6: Add auto-update release notes
```yaml
# In build-desktop.yml, add release notes
- name: Generate release notes
  if: startsWith(github.ref, 'refs/tags/')
  run: |
    echo "## PPTAgent Desktop ${{ github.ref_name }}" > release_notes.md
    echo "" >> release_notes.md
    echo "### Installation" >> release_notes.md
    echo "Download and run \`PPTAgent-Setup-*.exe\`" >> release_notes.md
    echo "" >> release_notes.md
    echo "### What's Changed" >> release_notes.md
    git log --oneline $(git describe --tags --abbrev=0 HEAD^)..HEAD >> release_notes.md
```

## Todo List
- [ ] Create `.github/workflows/build-desktop.yml`
- [ ] Create `.github/workflows/test-build.yml`
- [ ] Create `scripts/bump-version.ps1`
- [ ] Verify package.json publish config
- [ ] Test workflow with `workflow_dispatch`
- [ ] Create test tag for dry run
- [ ] Verify artifacts uploaded
- [ ] Test auto-update on installed app

## Success Criteria
- Workflow triggers on tag push
- Both Python and Electron build successfully
- Installer uploaded to GitHub Releases
- `latest.yml` present for auto-update
- Total build time <25min

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Build timeout | High | Optimize caching |
| PyInstaller failures | High | Test locally first |
| Publish failures | Medium | Check GH_TOKEN permissions |
| Large artifacts | Low | GitHub supports large releases |

## Security Considerations
- Use GITHUB_TOKEN (auto-provided)
- No custom secrets needed
- Artifacts signed with GitHub attestation

## Next Steps
→ Test full release cycle
→ Document release process in README
