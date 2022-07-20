import { Model, createModel } from '@rematch/core';
import { RootModel } from '.';
import { sendMessage } from '../socket';
import { events } from '../sync';

export type ScannedDevice = {
  name: string;
  address: string;
  rssi: number;
};

export type DevicesModel = {
  deviceConnected: boolean;
  scannedDevices: ScannedDevice[];
  scanning: boolean;
  connecting: boolean;
  disconnecting: boolean;
  device?: ScannedDevice;
};

export default createModel<RootModel>()({
  state: {
    deviceConnected: false,
    scannedDevices: [],
    scanning: false,
    connecting: false,
    disconnecting: false,
    device: undefined,
  } as DevicesModel,
  reducers: {
    stateSync(state, payload: any) {
      return {
        ...state,
        device: payload.device,
        deviceConnected: !!payload.device,
        scannedDevices: payload.scannedDevices[0],
        scanning: payload.isScanning,
      };
    },
    setScanning(state, scanning: boolean) {
      return {
        ...state,
        scanning,
      };
    },
    setScannedDevices(state, scannedDevices: ScannedDevice[]) {
      return {
        ...state,
        scannedDevices,
      };
    },
    setConnecting(state, connecting: boolean) {
      return {
        ...state,
        connecting,
      };
    },
    setConnected(state, device: ScannedDevice) {
      return {
        ...state,
        deviceConnected: true,
        device,
      };
    },
    setDisconnecting(state, disconnecting: boolean) {
      return {
        ...state,
        disconnecting,
      };
    },
    setDisconnected(state) {
      return {
        ...state,
        deviceConnected: false,
        device: undefined,
      };
    },
  },
  effects: {
    async startScan() {
      this.setScanning(true);
      sendMessage('ble:scan');
      const result = await new Promise<ScannedDevice[]>((resolve) => {
        events.once('ble:scan', (args: [ScannedDevice[]]) => resolve(args[0]));
      });
      this.setScannedDevices(result);
      this.setScanning(false);
    },
    async connectToDevice(dev: ScannedDevice) {
      this.setConnecting(true);
      sendMessage('ble:connect', dev.address);
      const didConnect = await new Promise<boolean>((resolve) => {
        events.once('ble:connect', (result: [boolean]) => resolve(result[0]));
      });
      this.setConnecting(false);
      if (didConnect) {
        this.setConnected(dev);
      } else {
        // TODO Error
      }
    },
    async disconnect(payload: null, state) {
      if (!state.devices.deviceConnected) {
        // TODO Error
        return;
      }
      this.setDisconnecting(true);
      sendMessage('ble:disconnect');
      const success = await new Promise<boolean>((resolve) => {
        events.once('ble:disconnect', (result: [boolean]) =>
          resolve(result[0])
        );
      });
      this.setDisconnecting(false);
      if (success) {
        this.setDisconnected();
      }
    },
  },
});
