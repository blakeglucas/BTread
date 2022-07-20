import { TrainingDatum } from '../models/training';
import { store } from '../store';
import { events } from '../sync';

events.on('training:start', () => {
  store.dispatch.training.start();
});

events.on('training:end', () => {
  store.dispatch.training.end();
});

events.on('training:datum', (d: [TrainingDatum]) => {
  store.dispatch.training.addDatum(d[0]);
});
