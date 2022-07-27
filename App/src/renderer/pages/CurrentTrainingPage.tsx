import React from 'react';
import { Button, Layout } from 'antd';
import { Line, LineConfig } from '@ant-design/plots';
import { RootState, Dispatch } from '../store';
import { useSelector, useDispatch } from 'react-redux';
import { PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import { formatSecs } from '../utils/formatSecs';

const { Sider, Content } = Layout;

export function CurrentTrainingPage() {
  const deviceConnected = useSelector(
    (state: RootState) => state.devices.deviceConnected
  );
  const status = useSelector((state: RootState) => state.training.status);
  const data = useSelector((state: RootState) => state.training.data);

  const dispatch = useDispatch<Dispatch>();

  const config = React.useMemo<LineConfig>(
    () => ({
      data,
      xField: 'Timestamp',
      yField: 'Speed',
      stepType: 'vh',
      xAxis: {
        type: 'time',
      },
      // slider: {
      //   start: 0.5,
      //   end: 1,
      // },
    }),
    [data]
  );

  const lastDatum = React.useMemo(() => data[data.length - 1], [data]);

  //   function formatSecs(secs: number) {
  //     const parts: number[] = []
  //     while (secs >= 1) {
  //         const x = secs % 60;
  //         parts.push(x)
  //         secs = (secs - x) / 60
  //     }
  //     return parts.reverse().map((x, i) => x.toString().padStart(i === 0 ? 1 : 2, '0')).join(':')
  //   }

  async function onTrainingButton() {
    const result = await dispatch.training.toggle(null);
  }

  return (
    <Layout className="h-full">
      <Content className="bg-neutral-800 pl-4">
        <div className="flex flex-row items-center mt-3">
          <Button
            icon={
              status === 'idle' ? (
                <PlayCircleOutlined />
              ) : (
                <PauseCircleOutlined />
              )
            }
            type="primary"
            size="large"
            className="training-control-button mr-4"
            onClick={() => onTrainingButton()}
            disabled={!deviceConnected}
          ></Button>
          <div className="flex flex-col">
            <span>Training Status</span>
            <p className="text-5xl mb-0">{status.toUpperCase()}</p>
          </div>
        </div>
        <div className="w-full mt-8">
          <Line {...config} className="w-full" />
        </div>
      </Content>
      <Sider>
        <div className="w-full py-4 px-6">
          <div>
            <span>Elapsed Time</span>
            <p className="text-5xl">
              {lastDatum ? formatSecs(lastDatum.ElapsedTime) : '0:00'}
            </p>
          </div>
          <div>
            <span>Distance (mi)</span>
            <p className="text-5xl">
              {lastDatum
                ? ((lastDatum.Distance / 1000) * 0.621371).toFixed(2)
                : 0}
            </p>
          </div>
          <div>
            <span>Distance (km)</span>
            <p className="text-5xl">
              {lastDatum ? (lastDatum.Distance / 1000).toFixed(2) : 0}
            </p>
          </div>
          <div>
            <span>Calories</span>
            <p className="text-5xl">{lastDatum?.Calories || 0}</p>
          </div>
        </div>
      </Sider>
    </Layout>
  );
}
