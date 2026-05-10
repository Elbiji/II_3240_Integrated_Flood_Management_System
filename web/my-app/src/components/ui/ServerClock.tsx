"use client"; 

import { useState, useEffect } from "react";
import { apiFetch } from '@/lib/api';

export default function ServerClock() {
    const [time, setTime] = useState<string | null>(null)
    const [data, setData] = useState<any>(null)
    const [inference, setInference] = useState<any>(null)
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res_info = await apiFetch("/api/v1/sensors/esp32_01/information")
                const res_inference = await apiFetch("/api/v1/services/esp32_01/inference")

                const json_info = await res_info.json()
                const json_inference = await res_inference.json()

                setData(json_info)
                setInference(json_inference)
            } catch (error) {
                console.error("Failed to fetch sensor information:", error)
            } finally {
                setLoading(false)
            }
        };

        fetchData()
    }, [])

    useEffect(() => {
        setTime(new Date().toUTCString())
    }, [])

    if (loading) return <div>Loading...</div>

    return (
        <div className="flex flex-row justify-between items-baseline">
            <p className="font-medium text-zinc-600 text-xl">{time}</p>
            <div className="flex flex-row gap-4 justify-between">
                <div className="flex flex-row px-4 py-2 border border-zinc-200 rounded-xl shadow-sm justify-between items-center gap-4">
                    <div className={`h-3 w-3 rounded-full ${
                        inference?.[0]?.classification == "DANGER"
                        ? "bg-red-500 border-2 border-red-700 "
                        : "bg-green-500 border-2 border-green-700 "}`}></div>
                    <p className={`font-mono ${
                        inference?.[0]?.classification == "DANGER"
                        ? "text-red-600"
                        : "text-green-600"}`}>{inference[0].classification}</p>
                </div>
                <div className="flex flex-row px-4 py-2 border border-zinc-200 rounded-xl shadow-sm justify-between items-center gap-4">
                    <div className="h-3 w-3 rounded-full bg-green-500 border-2 border-green-700"></div>
                    <p className="text-sm text-zinc-500">{data[0].location}</p>
                </div>
                <div className="flex flex-row px-4 py-2 border border-zinc-200 rounded-xl shadow-sm justify-between items-center gap-4">
                    <div className="h-3 w-3 rounded-full bg-green-500 border-2 border-green-700"></div>
                    <p className="text-sm text-zinc-500">{data[0].sensor_id}</p>
                </div>
            </div>
        </div>
    );
}