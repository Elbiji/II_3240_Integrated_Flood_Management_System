"use_client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export default function WeatherWidget() {
    const [data, setData] = useState([]);
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
        <div>

        </div>
    )
}