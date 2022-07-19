import { Models } from '@rematch/core';
import statusModel from './status';

export interface RootModel extends Models<RootModel> {
  status: typeof statusModel;
}

export const models: RootModel = { status: statusModel };
