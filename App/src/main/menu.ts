import { Menu } from 'electron';

const menu = Menu.buildFromTemplate([
  {
    label: 'File',
    submenu: [],
  },
  {
    label: 'View',
    submenu: [],
  },
  {
    label: 'Actions',
    submenu: [],
  },
  {
    label: 'Help',
    submenu: [],
  },
]);

Menu.setApplicationMenu(menu);

export default menu;
