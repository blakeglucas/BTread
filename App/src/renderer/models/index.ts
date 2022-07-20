import { Models } from '@rematch/core';
import DevicesModel from './devices';
import TrainingModel from './training';

export interface RootModel extends Models<RootModel> {
  devices: typeof DevicesModel;
  training: typeof TrainingModel;
}

export const models: RootModel = {
  devices: DevicesModel,
  training: TrainingModel,
};
