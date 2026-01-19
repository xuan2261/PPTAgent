const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', callback),
  onUpdateReady: (callback) => ipcRenderer.on('update-ready', callback),
  installUpdate: () => ipcRenderer.invoke('install-update'),
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),
  platform: process.platform,
});
