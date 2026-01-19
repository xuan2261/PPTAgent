# Phase 5: Electron-Python IPC

## Context Links
- [Plan Overview](plan.md)
- [Phase 3: Electron Setup](phase-03-electron-project-setup.md)
- [Phase 4: Backend Bundling](phase-04-python-backend-bundling.md)
- [Electron Research](research/researcher-01-electron-python-integration.md)

## Overview
- **Priority**: P2
- **Status**: pending
- **Effort**: 3h
- **Description**: Implement robust IPC between Electron and Python backend

## Key Insights
- child_process.spawn with `-u` for unbuffered output
- tree-kill for proper process termination
- Health check before loading Gradio URL
- Retry logic for backend startup
- Error handling and user notifications

## Requirements

### Functional
- Start Python backend on app launch
- Detect when backend is ready
- Graceful shutdown on app close
- Handle backend crashes
- Show error dialogs on failure

### Non-Functional
- Backend ready detection <10s
- Clean process termination
- No zombie processes

## Architecture

```
Electron Main Process
        │
        ├── spawn() → Python Backend (backend.exe)
        │                    │
        │                    ├── stdout: "Running on localhost:7861"
        │                    │
        ├── detect ready ←───┘
        │
        ├── loadURL() → http://localhost:7861
        │
        └── on quit → tree-kill(pid)
```

## Related Code Files

### Modify
- `D:/NCKH_2025/PPTAgent/electron-app/src/main.js`

### Create
- `D:/NCKH_2025/PPTAgent/electron-app/src/backend-manager.js`

## Implementation Steps

### Step 1: Create backend-manager.js
```javascript
const { spawn } = require('child_process');
const path = require('path');
const kill = require('tree-kill');
const { app } = require('electron');

class BackendManager {
  constructor() {
    this.process = null;
    this.port = 7861;
    this.isReady = false;
    this.onReady = null;
    this.onError = null;
  }

  getBackendPath() {
    if (app.isPackaged) {
      return path.join(process.resourcesPath, 'backend', 'backend.exe');
    }
    // Development mode
    return path.join(__dirname, '../../python-dist/backend.exe');
  }

  start() {
    return new Promise((resolve, reject) => {
      const backendPath = this.getBackendPath();

      console.log(`Starting backend: ${backendPath}`);

      this.process = spawn(backendPath, ['-u'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        windowsHide: true,
      });

      const timeout = setTimeout(() => {
        reject(new Error('Backend startup timeout (30s)'));
      }, 30000);

      this.process.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`[Backend] ${output}`);

        if (output.includes('Running on') || output.includes('localhost:7861')) {
          clearTimeout(timeout);
          this.isReady = true;
          resolve(this.port);
        }
      });

      this.process.stderr.on('data', (data) => {
        console.error(`[Backend Error] ${data}`);
      });

      this.process.on('error', (err) => {
        clearTimeout(timeout);
        reject(new Error(`Failed to start backend: ${err.message}`));
      });

      this.process.on('exit', (code) => {
        console.log(`Backend exited with code ${code}`);
        this.isReady = false;
        if (this.onError && code !== 0) {
          this.onError(new Error(`Backend crashed with code ${code}`));
        }
      });
    });
  }

  async stop() {
    if (this.process) {
      return new Promise((resolve) => {
        kill(this.process.pid, 'SIGTERM', (err) => {
          if (err) console.error('Error killing backend:', err);
          this.process = null;
          this.isReady = false;
          resolve();
        });
      });
    }
  }

  async healthCheck() {
    try {
      const http = require('http');
      return new Promise((resolve) => {
        const req = http.get(`http://localhost:${this.port}`, (res) => {
          resolve(res.statusCode === 200);
        });
        req.on('error', () => resolve(false));
        req.setTimeout(2000, () => {
          req.destroy();
          resolve(false);
        });
      });
    } catch {
      return false;
    }
  }
}

module.exports = BackendManager;
```

### Step 2: Update main.js
```javascript
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const BackendManager = require('./backend-manager');

let mainWindow;
const backendManager = new BackendManager();

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: path.join(__dirname, '../resources/icons/icon.ico'),
    show: false,
    titleBarStyle: 'default',
  });

  // Show loading screen
  mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));
  mainWindow.once('ready-to-show', () => mainWindow.show());

  // Handle window close
  mainWindow.on('close', async (e) => {
    e.preventDefault();
    await backendManager.stop();
    mainWindow.destroy();
  });
}

async function startApp() {
  createWindow();

  try {
    const port = await backendManager.start();
    console.log(`Backend ready on port ${port}`);

    // Wait a bit for Gradio to fully initialize
    await new Promise(r => setTimeout(r, 2000));

    mainWindow.loadURL(`http://localhost:${port}`);
  } catch (error) {
    console.error('Backend startup failed:', error);
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start PPTAgent backend:\n${error.message}\n\nPlease restart the application.`
    );
    app.quit();
  }

  // Handle backend crashes
  backendManager.onError = (error) => {
    dialog.showErrorBox(
      'Backend Error',
      `The backend process crashed:\n${error.message}\n\nPlease restart the application.`
    );
    app.quit();
  };

  // Check for updates
  if (app.isPackaged) {
    autoUpdater.checkForUpdatesAndNotify();
  }
}

app.whenReady().then(startApp);

app.on('window-all-closed', async () => {
  await backendManager.stop();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', async () => {
  await backendManager.stop();
});

// Auto-updater events
autoUpdater.on('update-available', () => {
  mainWindow.webContents.send('update-available');
});

autoUpdater.on('update-downloaded', () => {
  mainWindow.webContents.send('update-ready');
});

ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});

ipcMain.handle('get-app-info', () => {
  return {
    version: app.getVersion(),
    isPackaged: app.isPackaged,
  };
});
```

### Step 3: Update preload.js
```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Updates
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', callback),
  onUpdateReady: (callback) => ipcRenderer.on('update-ready', callback),
  installUpdate: () => ipcRenderer.invoke('install-update'),

  // App info
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),

  // Platform
  platform: process.platform,
});
```

### Step 4: Update loading screen (index.html)
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>PPTAgent</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      color: white;
    }
    .loader {
      text-align: center;
      padding: 40px;
    }
    .spinner {
      width: 60px;
      height: 60px;
      border: 4px solid rgba(255,255,255,0.2);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 30px;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    h1 {
      margin: 0 0 15px;
      font-size: 28px;
      font-weight: 600;
    }
    .status {
      opacity: 0.9;
      font-size: 14px;
    }
    .version {
      margin-top: 30px;
      opacity: 0.6;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="loader">
    <div class="spinner"></div>
    <h1>PPTAgent</h1>
    <p class="status">Initializing AI backend...</p>
    <p class="version" id="version"></p>
  </div>
  <script>
    if (window.electronAPI) {
      window.electronAPI.getAppInfo().then(info => {
        document.getElementById('version').textContent = `v${info.version}`;
      });
    }
  </script>
</body>
</html>
```

## Todo List
- [ ] Create backend-manager.js module
- [ ] Update main.js with new backend management
- [ ] Update preload.js with new IPC handlers
- [ ] Enhance loading screen with version info
- [ ] Add error dialogs for failures
- [ ] Test startup sequence
- [ ] Test graceful shutdown
- [ ] Test crash recovery
- [ ] Verify no zombie processes

## Success Criteria
- Backend starts within 30s
- Gradio UI loads in Electron window
- Clean shutdown with no orphan processes
- Error dialog shown on failure

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Backend timeout | High | Increase timeout, show progress |
| Zombie processes | Medium | tree-kill, process cleanup |
| Port conflict | Low | Check port availability |

## Security Considerations
- Backend only binds to localhost
- No external network access
- User data stays local

## Next Steps
→ Phase 6: GitHub Actions CI/CD
