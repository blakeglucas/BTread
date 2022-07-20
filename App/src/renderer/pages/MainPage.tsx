import React from 'react';
import { Avatar, Button, Layout, List, Menu, Spin } from 'antd';
import clsx from 'clsx';
import { RootState, Dispatch } from '../store';
import { useSelector, useDispatch } from 'react-redux';
import { ScannedDevice } from '../models/devices';
import { Link, NavLink, Routes, Route } from 'react-router-dom';
import { CurrentTrainingPage } from './CurrentTrainingPage';
import { ReportingPage } from './ReportingPage';

const { Header, Footer, Sider, Content } = Layout;

const links = [
  {
    label: 'Current Training',
    href: '/',
  },
  {
    label: 'Historical Data',
    href: 'reporting',
  },
];

export function MainPage() {
  const [selectedDevice, setSelectedDevice] = React.useState<string>('');

  const scannedDevices = useSelector(
    (state: RootState) => state.devices.scannedDevices
  );

  const scanning = useSelector((state: RootState) => state.devices.scanning);
  const connecting = useSelector(
    (state: RootState) => state.devices.connecting
  );

  const deviceConnected = useSelector(
    (state: RootState) => state.devices.deviceConnected
  );
  const device = useSelector((state: RootState) => state.devices.device);

  const disconnecting = useSelector(
    (state: RootState) => state.devices.disconnecting
  );

  const dispatch = useDispatch<Dispatch>();

  async function startScan() {
    await dispatch.devices.startScan();
  }

  async function connect(dev: ScannedDevice) {
    setSelectedDevice(dev.address);
    await dispatch.devices.connectToDevice(dev);
  }

  async function disconnect() {
    await dispatch.devices.disconnect(null);
    setSelectedDevice('');
  }

  return (
    <Layout className="h-full">
      <Sider
        className="bg-neutral-600 flex flex-col items-center justify-start"
        width={300}
      >
        <div className="w-full px-6 py-4 flex flex-col items-center">
          <Button
            type="primary"
            size="large"
            onClick={() => startScan()}
            loading={scanning}
            disabled={connecting || deviceConnected}
          >
            Scan for BTread Devices
          </Button>
          <List
            className="my-3 max-h-64 w-full"
            dataSource={scannedDevices?.sort((a, b) => b.rssi - a.rssi)}
            bordered
            renderItem={(item) => (
              <List.Item
                onClick={
                  connecting || deviceConnected || scanning || disconnecting
                    ? undefined
                    : () => {
                        connect(item);
                      }
                }
                className={clsx(
                  !connecting &&
                    !scanning &&
                    !deviceConnected &&
                    'cursor-pointer hover:bg-neutral-500',
                  deviceConnected &&
                    device?.address === item.address &&
                    'bg-green-600'
                )}
              >
                <List.Item.Meta
                  title={item.name}
                  description={item.address}
                  avatar={
                    <Avatar size={32}>
                      {connecting && selectedDevice === item.address ? (
                        <Spin />
                      ) : (
                        item.rssi
                      )}
                    </Avatar>
                  }
                />
              </List.Item>
            )}
          ></List>
          <Button
            type="primary"
            danger
            onClick={() => disconnect()}
            loading={disconnecting}
            disabled={!deviceConnected}
          >
            Disconnect
          </Button>
        </div>
        <div className="flex flex-row items-center p-4 w-full">
          <hr className="w-full text-neutral-400" />
        </div>
        <div className="w-full mt-4">
          {links.map((link, index) => (
            <NavLink
              key={index}
              to={link.href}
              className={({ isActive }) =>
                isActive
                  ? 'bg-neutral-800 w-full p-3 text-white flex hover:text-white cursor-default'
                  : 'bg-neutral-700 w-full p-3 text-white hover:text-white hover:bg-neutral-500 cursor-pointer flex'
              }
            >
              <span>{link.label}</span>
            </NavLink>
          ))}
        </div>
      </Sider>
      <Content className="bg-neutral-800">
        <Routes>
          <Route index element={<CurrentTrainingPage />} />
          <Route path="reporting" element={<ReportingPage />} />
        </Routes>
      </Content>
    </Layout>
  );
}
