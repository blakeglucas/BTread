import { events } from './sync';

electron.ipcRenderer.on('socket', (event, eventName, eventArgs) => {
  events.emit(eventName, eventArgs);
});

export function sendMessage(eventName: string, ...eventArgs: any[]) {
  electron.ipcRenderer.send('socket', eventName, ...eventArgs);
}
