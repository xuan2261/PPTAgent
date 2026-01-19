# Research: Electron + Python Desktop App for Windows

**Date:** 2026-01-19
**Focus:** Bundling strategies, IPC, CI/CD, auto-update, Playwright packaging

---

## 1. Electron + PyInstaller Bundling Strategies

### Recommended Approach
1. **Bundle Python with PyInstaller** → single `.exe`
   ```bash
   pyinstaller --onefile --windowed backend.py
   ```
2. **Place exe in Electron's resources** → `resources/backend/backend.exe`
3. **Use electron-builder** to include Python exe in final package

### Key Configurations
- Use `.spec` file for complex imports/hidden dependencies
- Flask recommended for web-based backend (smaller footprint)
- Output goes to `dist/` folder by default

### electron-builder extraResources
```json
{
  "build": {
    "extraResources": [
      { "from": "python-dist/", "to": "backend/" }
    ]
  }
}
```

---

## 2. IPC Communication: Electron ↔ Python

### Option A: child_process.spawn (Recommended)
```javascript
const { spawn } = require('child_process');
const pythonPath = path.join(process.resourcesPath, 'backend', 'backend.exe');
const python = spawn(pythonPath, ['-u']); // -u = unbuffered output

python.stdout.on('data', (data) => { /* handle response */ });
python.stdin.write(JSON.stringify({ command: 'process' }) + '\n');
```

### Option B: python-shell npm package
```javascript
const { PythonShell } = require('python-shell');
PythonShell.run('script.py', { mode: 'json' }, (err, results) => {});
```

### Option C: HTTP/Socket (Flask backend)
- Python runs Flask server on localhost:port
- Electron makes HTTP requests to backend
- Better for complex APIs, worse for startup time

### Best Practices
- Use `-u` flag for unbuffered Python output
- JSON for structured data exchange
- `tree-kill` package to terminate Python process on app close
- Handle process lifecycle in Electron's `app.on('quit')`

---

## 3. GitHub Actions CI/CD for Windows .exe

### Workflow Template
```yaml
name: Build Windows
on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # Build Python backend
      - run: |
          pip install pyinstaller
          pyinstaller --onefile backend.py

      # Build Electron
      - run: npm ci
      - run: npx electron-builder --win --publish always
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Key Points
- Use `windows-latest` runner
- Matrix strategy for multi-OS builds
- Tag-based releases (`v1.0.0`)
- `--publish always` auto-uploads to GitHub Releases

---

## 4. Auto-Update Mechanisms

### electron-updater (Recommended)
- **NSIS installer required** (not Squirrel.Windows)
- Works with GitHub Releases out-of-box

```javascript
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();
autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall();
});
```

### Configuration (package.json)
```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "your-org",
      "repo": "your-repo"
    },
    "win": {
      "target": "nsis"
    }
  }
}
```

### Important Notes
- Squirrel.Windows NOT supported by electron-updater
- Migrate to NSIS for simplified auto-updates
- Handle `--squirrel-firstrun` if using legacy Squirrel

---

## 5. Packaging Playwright/Chromium with Electron

### Challenge
- Electron bundles its own Chromium
- Playwright requires separate Chromium binary (~150MB)

### Solutions

**Option A: Use Electron's Chromium**
```javascript
// Point Playwright to Electron's Chromium
const electron = require('electron');
const browser = await playwright.chromium.launch({
  executablePath: electron.app.getPath('exe')
});
```

**Option B: Bundle Playwright browsers**
```json
{
  "build": {
    "extraResources": [
      { "from": "node_modules/playwright/.local-browsers/", "to": "browsers/" }
    ]
  }
}
```

**Option C: Download on first run**
```javascript
// Check and download if missing
const { chromium } = require('playwright');
await chromium.install();
```

### Recommendations
- Option A preferred (smallest bundle)
- Set `PLAYWRIGHT_BROWSERS_PATH` env var
- Consider `playwright-core` (no auto-download)

---

## Architecture Summary

```
electron-app/
├── src/
│   ├── main.js          # Electron main process
│   ├── preload.js       # Bridge to renderer
│   └── renderer/        # Frontend UI
├── python/
│   └── backend.py       # Python backend source
├── resources/
│   └── backend/         # PyInstaller output
├── package.json
└── electron-builder.yml
```

---

## Sources

- [Medium - Electron + Python bundling](https://medium.com)
- [Stack Overflow - child_process spawn](https://stackoverflow.com)
- [Electron Docs - IPC](https://electronjs.org)
- [DEV Community - GitHub Actions Electron](https://dev.to)
- [electron-builder docs](https://electron.build)
- [electron-updater npm](https://npmjs.com/package/electron-updater)

---

## Unresolved Questions

1. **Code signing**: Windows SmartScreen requires EV certificate (~$300/yr) - acceptable cost?
2. **Python version pinning**: Should we embed specific Python version or rely on PyInstaller?
3. **Playwright browser size**: ~150MB additional - acceptable for distribution?
4. **Hot reload during dev**: How to handle Python backend reload without full app restart?
