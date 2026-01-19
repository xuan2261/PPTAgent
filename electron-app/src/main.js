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
    show: false,
    titleBarStyle: 'default',
  });

  mainWindow.loadFile(path.join(__dirname, 'renderer/index.html'));
  mainWindow.once('ready-to-show', () => mainWindow.show());

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
    await new Promise(r => setTimeout(r, 2000));
    mainWindow.loadURL(`http://localhost:${port}`);
  } catch (error) {
    console.error('Backend startup failed:', error);
    dialog.showErrorBox('Startup Error', `Failed to start PPTAgent backend:\n${error.message}`);
    app.quit();
  }

  if (app.isPackaged) {
    autoUpdater.checkForUpdatesAndNotify();
  }
}

app.whenReady().then(startApp);

app.on('window-all-closed', async () => {
  await backendManager.stop();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', async () => {
  await backendManager.stop();
});

autoUpdater.on('update-downloaded', () => {
  mainWindow.webContents.send('update-ready');
});

ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});

ipcMain.handle('get-app-info', () => {
  return { version: app.getVersion(), isPackaged: app.isPackaged };
});
