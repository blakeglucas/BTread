import { BrowserWindow } from 'electron';
import io from 'socket.io-client';

export default class SocketHandler {
  private readonly socket;
  constructor(private win: BrowserWindow) {
    this.socket = io('http://localhost:8826', {});

    this.socket.on('connect', () => {
      console.log('connected');
      this.send('state_sync');
    });

    this.socket.on('disconnect', () => {
      console.log('disconnected');
    });

    // @ts-ignore
    this.socket.onAny((eventName, ...args) => {
      this.win.webContents.send('socket', eventName, args);
    });
  }

  send(eventName: string, ...args: any[]) {
    this.socket.emit(eventName, ...args);
  }
}
