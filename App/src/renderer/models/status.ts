import { Model, createModel } from '@rematch/core';
import { RootModel } from '.';

export type Status = {
  deviceConnected: boolean;
};

export default createModel<RootModel>()({
  state: {
    deviceConnected: false,
  } as Status,
  reducers: {
    setStatus(state, payload) {
      return {
        ...state,
        ...payload,
      };
    },
  },
});
