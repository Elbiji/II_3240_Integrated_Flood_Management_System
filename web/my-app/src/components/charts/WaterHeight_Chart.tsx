"use client"; 

import { apiFetch } from '@/lib/api';
import { useState, useEffect } from 'react';
import { 
  AreaChart,
  Area, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

export default function FloodLineChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await apiFetch("/api/v1/sensors/esp32_01/history");
        const json = await res.json()
        setData(json)
      } catch (error) {
        console.error("Failed to fetch sensor data:", error)
      } finally {
        setLoading(false)
      }
    };

    fetchData()
  }, [])


  const formatXAxis = (tickItem: string) => {
    if (!tickItem) return "";
    const date = new Date(tickItem);
    
    // Returns HH:mm (e.g., 15:30)
    return date.toLocaleTimeString('id-ID', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (loading) return <div className='h-100 flex items-center'>Loading chart...</div>

  return (
    <div className="w-full h-100 rounded-lg border border-zinc-200 flex flex-col gap-12 pb-2">
      <div className='border-b border-zinc-200 flex-col'>
        <div className='px-10 font-medium text-lg pt-4'>
          Grafik Ketinggian Air vs Laju dv/dt
        </div>
        <div className='px-10 text-sm pb-4 text-zinc-500'>
          Ketinggian air dihitung dari jarak air terhadap sensor ultrasonik.
        </div>
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 5, right: 40, left: 40, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="4" vertical={false} stroke="#f0f0f0" />

          <defs>
            <linearGradient id="fillWater" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#888888" stopOpacity={0.5}/>
              <stop offset="95%" stopColor="var(--color-chart-1)" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="fillChange" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0d9488" stopOpacity={0.5}/>
              <stop offset="95%" stopColor="#0d9488" stopOpacity={0}/>
            </linearGradient>
          </defs>

          <XAxis 
            axisLine={false}
            dataKey="timestamp" 
            tickFormatter={formatXAxis}
            tickLine={false} 
            tick={{ fill: 'var(--color-muted-foreground)', fontSize: 12 }}
            stroke="#888888" 
            fontSize={12}
          />
          <YAxis stroke="#888888" 
            axisLine={false}
            width={0}
            tickLine={false}
            tick={{ fill: 'var(--color-muted-foreground)', fontSize: 0 }}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="water_height"
            stroke="#1e3a8a" 
            strokeWidth={2}
            activeDot={{ r: 4, strokeWidth: 0, fill: "var(--color-chart-1)" }}
            dot={false}
            fill="url(#fillWater)"
            legendType="none"
          />
          <Area
            type="monotone"
            dataKey="water_height_change"
            stroke="#1e3a8a" 
            strokeWidth={2}
            activeDot={{ r: 4, strokeWidth: 0, fill: "var(--color-chart-1)" }}
            dot={false}
            fill="url(#fillChange)"
            legendType="none"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}