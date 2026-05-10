"use client"; 

import { apiFetch } from '@/lib/api';
import { useState, useEffect } from 'react';
import { 
  AreaChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

const sampleData = [
  { name: '08:00', uv: 4000, pv: 2400 },
  { name: '10:00', uv: 3000, pv: 1398 },
  { name: '12:00', uv: 2000, pv: 9800 },
  { name: '14:00', uv: 2780, pv: 3908 },
  { name: '16:00', uv: 1890, pv: 4800 },
];

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

  if (loading) return <div className='h-[400px] flex items-center'>Loading chart...</div>

  return (
    <div className="w-full h-[400px] bg-white p-4 rounded-lg">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={formatXAxis} 
            stroke="#888888" 
            fontSize={12}
          />
          <YAxis stroke="#888888" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="water_height"
            stroke="#1e3a8a" 
            strokeWidth={2}
            activeDot={{ r: 8 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}