electron.ipcRenderer.on('socket', (event, eventName, eventArgs) => {
    console.log(1, event, eventName, eventArgs)
})