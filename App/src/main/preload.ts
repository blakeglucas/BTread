// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts
import { ipcRenderer, contextBridge } from 'electron';
import { Titlebar, Color } from 'custom-electron-titlebar';
import path from 'path';

contextBridge.exposeInMainWorld('electron', {
  ipcRenderer: {
    ...ipcRenderer,
    on: ipcRenderer.on.bind(ipcRenderer),
  },
});

window.addEventListener('DOMContentLoaded', () => {
  // Title bar implemenation
  new Titlebar({
    backgroundColor: Color.fromHex('#2f2f2f'),
    icon: null,
  });
});
