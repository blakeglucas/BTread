import React from 'react';
import { HashRouter } from 'react-router-dom';
import { MainPage } from './pages/MainPage';

export default function () {
  React.useEffect(() => {
    electron.ipcRenderer.send('ui:ready');
  }, []);

  return (
    <HashRouter>
      <MainPage />
    </HashRouter>
  );
}
