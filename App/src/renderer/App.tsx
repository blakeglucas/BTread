import React from 'react';
import { MainPage } from './pages/MainPage';

export default function () {
  React.useEffect(() => {
    electron.ipcRenderer.send('ui:ready');
  }, []);

  return <MainPage />;
}
