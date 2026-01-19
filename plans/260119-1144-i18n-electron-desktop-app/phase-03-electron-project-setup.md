# Phase 3: Electron Project Setup

## Context Links
- [Plan Overview](plan.md)
- [Electron Research](research/researcher-01-electron-python-integration.md)

## Overview
- **Priority**: P2
- **Status**: pending
- **Effort**: 3h
- **Description**: Initialize Electron project structure with electron-builder

## Key Insights
- electron-builder with NSIS for Windows installer
- electron-updater for auto-update (requires NSIS, not Squirrel)
- extraResources for bundling Python backend
- Separate main/preload/renderer architecture

## Requirements

### Functional
- Electron app loads embedded Gradio WebUI
- Window management (min/max/close)
- System tray integration
- Auto-update capability

### Non-Functional
- Fast startup (<5s)
- Minimal memory footprint
- Clean installer experience

## Architecture

```
electron-app/
├── src/
│   ├── main.js           # Main process
│   ├── preload.js        # Secure bridge
│   └── renderer/
│       └── index.html    # Loading screen
├── resources/
│   └── icons/            # App icons
├── package.json
├── electron-builder.yml
└── .gitignore
```

## Related Code Files

### Create
- `D:/NCKH_2025/PPTAgent/electron-app/package.json`
- `D:/NCKH_2025/PPTAgent/electron-app/electron-builder.yml`
- `D:/NCKH_2025/PPTAgent/electron-app/src/main.js`
- `D:/NCKH_2025/PPTAgent/electron-app/src/preload.js`
- `D:/NCKH_2025/PPTAgent/electron-app/src/renderer/index.html`
- `D:/NCKH_2025/PPTAgent/electron-app/.gitignore`

## Implementation Steps

### Step 1: Create electron-app directory
```bash
mkdir -p electron-app/src/renderer
mkdir -p electron-app/resources/icons
```

### Step 2: Create package.json
```json
{
  "name": "pptagent-desktop",
  "version": "1.0.0",
  "description": "PPTAgent Desktop - AI Presentation Generator",
  "main": "src/main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder --win",
    "build:publish": "electron-builder --win --publish always"
  },
  "author": "ICIP-CAS",
  "license": "MIT",
  "devDependencies": {
    "electron": "^33.0.0",
    "electron-builder": "^25.0.0"
  },
  "dependencies": {
    "electron-updater": "^6.3.0",
    "tree-kill": "^1.2.2"
  },
  "build": {
    "appId": "com.icip.pptagent",
    "productName": "PPTAgent",
    "copyright": "Copyright © 2025 ICIP-CAS",
    "directories": {
      "output": "dist"
    },
    "extraResources": [
      {
        "from": "../python-dist/",
        "to": "backend/"
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "resources/icons/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true
    },
    "publish": {
      "provider": "github",
      "owner": "icip-cas",
      "repo": "PPTAgent"
    }
  }
}
```

### Step 3: Create electron-builder.yml (alternative config)
```yaml
appId: com.icip.pptagent
productName: PPTAgent
copyright: Copyright © 2025 ICIP-CAS

directories:
  output: dist

extraResources:
  - from: ../python-dist/
    to: backend/

win:
  target: nsis
  icon: resources/icons/icon.ico

nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true

publish:
  provider: github
  owner: icip-cas
  repo: PPTAgent
```

### Step 4: Create main.js
```javascript
const { app, BrowserWindow, ipcMain } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const { spawn } = require('child_process');
const kill = require('tree-kill');

let mainWindow;
let pythonProcess;
const BACKEND_PORT = 7861;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, '../resources/icons/icon.ico'),
    show: false,
  });

  // Show loading screen first
  mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));
  mainWindow.once('ready-to-show', () => mainWindow.show());
}

function startPythonBackend() {
  const backendPath = app.isPackaged
    ? path.join(process.resourcesPath, 'backend', 'backend.exe')
    : path.join(__dirname, '../../python-dist/backend.exe');

  pythonProcess = spawn(backendPath, ['-u'], {
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    if (output.includes('Running on')) {
      // Backend ready, load Gradio UI
      mainWindow.loadURL(`http://localhost:${BACKEND_PORT}`);
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend error: ${data}`);
  });
}

app.whenReady().then(() => {
  createWindow();
  startPythonBackend();
  autoUpdater.checkForUpdatesAndNotify();
});

app.on('window-all-closed', () => {
  if (pythonProcess) {
    kill(pythonProcess.pid);
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Auto-updater events
autoUpdater.on('update-downloaded', () => {
  mainWindow.webContents.send('update-ready');
});

ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});
```

### Step 5: Create preload.js
```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onUpdateReady: (callback) => ipcRenderer.on('update-ready', callback),
  installUpdate: () => ipcRenderer.invoke('install-update'),
  getAppVersion: () => process.env.npm_package_version,
});
```

### Step 6: Create index.html (loading screen)
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>PPTAgent</title>
  <style>
    body {
      margin: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .loader {
      text-align: center;
      color: white;
    }
    .spinner {
      width: 50px;
      height: 50px;
      border: 3px solid rgba(255,255,255,0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 20px;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    h1 { margin: 0 0 10px; font-size: 24px; }
    p { margin: 0; opacity: 0.8; }
  </style>
</head>
<body>
  <div class="loader">
    <div class="spinner"></div>
    <h1>PPTAgent</h1>
    <p>Starting AI backend...</p>
  </div>
</body>
</html>
```

### Step 7: Create .gitignore
```
node_modules/
dist/
*.log
.DS_Store
```

### Step 8: Install dependencies
```bash
cd electron-app
npm install
```

## Todo List
- [ ] Create electron-app directory structure
- [ ] Create package.json with electron-builder config
- [ ] Create main.js with window and backend management
- [ ] Create preload.js for secure IPC
- [ ] Create loading screen HTML
- [ ] Create .gitignore
- [ ] Add app icon (icon.ico)
- [ ] Run `npm install`
- [ ] Test `npm start` (will fail until backend exists)

## Success Criteria
- `npm install` completes without errors
- Electron app starts and shows loading screen
- electron-builder config validated

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Electron version conflicts | Medium | Pin specific version |
| Missing icon | Low | Use placeholder |
| Path issues (dev vs prod) | High | Test both modes |

## Security Considerations
- contextIsolation: true (prevent renderer access to Node)
- nodeIntegration: false
- Use preload for safe IPC

## Next Steps
→ Phase 4: Python Backend Bundling
