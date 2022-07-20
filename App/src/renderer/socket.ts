import { events } from './sync';

electron.ipcRenderer.on('socket', (event, eventName, eventArgs) => {
  console.log(1, event, eventName, eventArgs);
  events.emit(eventName, eventArgs);
});

export function sendMessage(eventName: string, ...eventArgs: any[]) {
  console.log('sending message', eventName);
  electron.ipcRenderer.send('socket', eventName, ...eventArgs);
}
