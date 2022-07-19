import React from 'react';
import { RootState, store } from './store';
import { useSelector, Provider } from 'react-redux';
import { PerformanceChart } from './components/PerformanceChart';

export default function () {
  const statusState = useSelector((state: RootState) => state.status);

  React.useEffect(() => {
    electron.ipcRenderer.send('ui:ready');
    setTimeout(() => {
      electron.ipcRenderer.send(
        'socket',
        'ble:scan',
      );
    }, 2000);
  }, []);

  React.useEffect(() => {
    console.log(statusState);
  }, [statusState]);

  return <PerformanceChart />;
// return <div></div>
}
