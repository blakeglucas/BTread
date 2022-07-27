import { init, RematchDispatch, RematchRootState } from '@rematch/core';
import { models, RootModel } from './models';
import { ScannedDevice } from './models/devices';
import { events } from './sync';
import DevicesModel from './models/devices';
import { TrainingDatum } from './models/training';

export const store = init({
  models,
});

export type Store = typeof store;
export type Dispatch = RematchDispatch<RootModel>;
export type RootState = RematchRootState<RootModel>;

export type ExpectedStateObj = {
  devices: {
    device: ScannedDevice;
    isScanning: boolean;
    scannedDevices: [ScannedDevice[]];
  };
  training: {
    status: 'idle' | 'running';
    data: TrainingDatum[];
  };
};

events.on('state_sync', (obj: [ExpectedStateObj]) => {
  store.dispatch.devices.stateSync(obj[0].devices);
  store.dispatch.training.stateSync(obj[0].training);
});
