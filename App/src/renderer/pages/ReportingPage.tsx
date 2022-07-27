import React from 'react';
import { Button, DatePicker } from 'antd';
import {
  endOfDay,
  startOfDay,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  startOfYear,
  differenceInSeconds,
  parseISO,
  sub,
} from 'date-fns';
import moment from 'moment';
import { sendMessage } from '../socket';
import { events } from '../sync';
import { TrainingDatum } from '../models/training';
import { formatSecs } from '../utils/formatSecs';
import { Line, LineConfig, DualAxes, DualAxesConfig } from '@ant-design/plots';

const DateRanges: Record<string, { start: () => Date; end?: () => Date }> = {
  today: {
    start: () => startOfDay(new Date()),
    end: () => endOfDay(new Date()),
  },
  thisWeek: {
    start: () => startOfWeek(new Date()),
    end: () => endOfWeek(new Date()),
  },
  mtd: {
    start: () => startOfMonth(new Date()),
  },
  ytd: {
    start: () => startOfYear(new Date()),
  },
  '1m': {
    start: () => sub(new Date(), { months: 1 }),
  },
  '3m': {
    start: () => sub(new Date(), { months: 3 }),
  },
  '6m': {
    start: () => sub(new Date(), { months: 6 }),
  },
  '1y': {
    start: () => sub(new Date(), { years: 1 }),
  },
};

export type Session = {
  SessionID: number;
  StartTime: string;
  EndTime: string;
  Distance: number;
  Calories: number;
  Data: TrainingDatum[];
};

export function ReportingPage() {
  const [startDate, setStartDate] = React.useState(startOfDay(new Date()));
  const [endDate, setEndDate] = React.useState(endOfDay(new Date()));
  const [data, setData] = React.useState<Session[]>([]);

  const [timeSpent, setTimeSpent] = React.useState(0);
  const [distance, setDistance] = React.useState(0);
  const [distanceMiles, setDistanceMiles] = React.useState(0);
  const [calories, setCalories] = React.useState(0);

  React.useEffect(() => {
    async function updateData() {
      sendMessage('data:range', startDate.toISOString(), endDate.toISOString());
      const result = await new Promise<Session[]>((resolve) => {
        events.once('data:range', (result: [any]) => {
          resolve(result[0]);
        });
      });
      setData(result);
    }
    updateData();
  }, [startDate, endDate]);

  function setRange(id: keyof typeof DateRanges) {
    const gen = DateRanges[id];
    if (!gen) {
      console.log('lmao');
      return;
    }
    const startDate = gen.start ? gen.start() : new Date();
    const endDate = gen.end ? gen.end() : new Date();
    setStartDate(startDate);
    setEndDate(endDate);
  }

  React.useEffect(() => {
    setTimeSpent(
      data.reduce(
        (pV, cV) =>
          pV +
          differenceInSeconds(parseISO(cV.EndTime), parseISO(cV.StartTime)),
        0
      )
    );
    setDistance(data.reduce((pV, cV) => pV + cV.Distance / 1000, 0));
    setCalories(data.reduce((pV, cV) => pV + cV.Calories, 0));
  }, [data]);

  React.useEffect(() => {
    setDistanceMiles(distance * 0.621371);
  }, [distance]);

  const config = React.useMemo<DualAxesConfig>(() => {
    const dataCaloriesAgg = data
      .map((session, index) => {
        if (index > 0) {
          return session.Data.map((d) => ({
            Calories:
              d.Calories +
              data.slice(0, index).reduce((pV, cV) => pV + cV.Calories, 0),
            Timestamp: d.Timestamp,
          }));
        } else {
          return [...session.Data];
        }
      })
      .flat();
    const dataDistanceAgg = data
      .map((session, index) => {
        if (index > 0) {
          return session.Data.map((d) => ({
            Distance:
              (d.Distance +
                data.slice(0, index).reduce((pV, cV) => pV + cV.Distance, 0)) /
              1000,
            Timestamp: d.Timestamp,
          }));
        } else {
          return [
            ...session.Data.map((d) => ({ ...d, Distance: d.Distance / 1000 })),
          ];
        }
      })
      .flat();
    return {
      data: [dataCaloriesAgg, dataDistanceAgg],
      xField: 'Timestamp',
      yField: ['Calories', 'Distance'],
      xAxis: {
        type: 'time',
      },
      slider: {
        start: 0,
        end: 1,
      },
    };
  }, [data]);

  return (
    <div>
      <div className="flex flex-row w-full items-center gap-2 justify-center my-4">
        <Button type="primary" onClick={() => setRange('today')}>
          Today
        </Button>
        <Button type="primary" onClick={() => setRange('thisWeek')}>
          This Week
        </Button>
        <Button type="primary" onClick={() => setRange('mtd')}>
          MTD
        </Button>
        <Button type="primary" onClick={() => setRange('ytd')}>
          YTD
        </Button>
        <Button type="primary" onClick={() => setRange('1m')}>
          1M
        </Button>
        <Button type="primary" onClick={() => setRange('3m')}>
          3M
        </Button>
        <Button type="primary" onClick={() => setRange('6m')}>
          6M
        </Button>
        <Button type="primary" onClick={() => setRange('1y')}>
          1Y
        </Button>
        <DatePicker.RangePicker
          allowClear={false}
          value={[moment(startDate), moment(endDate)]}
          onChange={([start, end]) => {
            setStartDate(start.toDate());
            setEndDate(end.toDate());
          }}
        />
      </div>
      <div className="flex flex-row w-full items-center justify-around my-4">
        <div>
          <span>Total Time</span>
          <p className="text-5xl select-none">{formatSecs(timeSpent)}</p>
        </div>
        <div>
          <span>Total Distance (mi)</span>
          <p className="text-5xl select-none">{distanceMiles.toFixed(2)}</p>
        </div>
        <div>
          <span>Total Distance (km)</span>
          <p className="text-5xl select-none">{distance.toFixed(2)}</p>
        </div>
        <div>
          <span>Total Calories</span>
          <p className="text-5xl select-none">{calories}</p>
        </div>
      </div>
      <div className="w-full mt-8">
        <DualAxes {...config} className="w-full" />
      </div>
    </div>
  );
}
