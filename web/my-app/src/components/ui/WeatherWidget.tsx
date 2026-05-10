"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

export default function WeatherWidget() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await apiFetch("/api/v1/services/weather")
                const json = await res.json()
                setData(json)
            } catch (error) {
                console.error("Failed to fetch weather data:", error)
            } finally {
                setLoading(false)
            }
        };

        fetchData()
    }, [])

    if (loading) return <div>Loading weather widget</div>

    return (
        <div className="w-full rounded-lg border border-zinc-200 flex flex-col gap-2 h-full">
            <div className='border-b border-zinc-200 flex-col'>
                <div className='px-10 font-medium text-lg pt-4'>
                    Cuaca
                </div>
                <div className='px-10 text-sm pb-4 text-zinc-500'>
                    Data cuaca diambil melalui API eksternal terbuka (open-meteo).
                </div>
            </div>
            <div className="flex flex-col px-10 gap-2 py-3">
                <p className="text-zinc-500">Temperatur</p>
                <h1 className="text-4xl font-mono">
                    {data.temperature_2m} °C
                </h1>
            </div>
            <div className='border-t border-zinc-200 flex-1 flex flex-col'>
                <div className='px-2 flex-row flex justify-between items-center gap-2 flex-1'>
                    <div className="flex-1 flex flex-col items-center py-4 gap-2">
                        <p className="text-zinc-500 ">Kelembaban</p>
                        <span className="text-xl font-mono">{data.relative_humidity_2m}%</span>
                    </div>
                    <div className="self-stretch w-px bg-zinc-200"></div>
                    <div className="flex-1 flex flex-col items-center py-4 gap-2">
                        <p className="text-zinc-500 ">Awan</p>
                        <span className="text-xl font-mono">{data.cloud_cover}%</span>
                    </div>
                    <div className="self-stretch w-px bg-zinc-200"></div>
                    <div className="flex-1 flex flex-col items-center py-4 gap-2">
                        <p className="text-zinc-500 ">Presipitasi</p>
                        <span className="text-xl font-mono">{data.precipitation}%</span>
                    </div>
                </div>
            </div>
        </div>
    );
}