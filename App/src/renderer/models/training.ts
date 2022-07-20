import { Model, createModel } from '@rematch/core';
import { RootModel } from '.';
import { sendMessage } from '../socket';
import { events } from '../sync';

export type TrainingModel = {
  status: 'idle' | 'running';
  data: TrainingDatum[];
};

export type TrainingDatum = {
  DatumID: number;
  Timestamp: Date | string;
  Speed: number;
  ElapsedTime: number;
  Calories: number;
  Distance: number;
  SessionID: number;
};

export default createModel<RootModel>()({
  state: {
    status: 'idle',
    data: [],
  } as TrainingModel,
  reducers: {
    stateSync(state, payload: any) {
      return {
        ...state,
        status: payload.status,
      };
    },
    start(state) {
      return {
        ...state,
        status: 'running',
        data: [],
      };
    },
    end(state) {
      return {
        ...state,
        status: 'idle',
      };
    },
    addDatum(state, payload: TrainingDatum) {
      return {
        ...state,
        data: [...state.data, payload],
      };
    },
  },
  effects: {},
});
