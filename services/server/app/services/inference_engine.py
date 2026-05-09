from app.model.schemas import Classification
from app.config import DatabaseClient

class InferenceEngine:
    @classmethod 
    async def calculate_flood_probability(cls, weather_data: dict, sensor_data: dict, device_id: str) -> Classification:
        print(type(sensor_data.get("is_wet")))
        
        # 1. Height Score (4.5m is our 'critical' threshold)
        height_score = min(1 / 4.5, 1.0) * 70 # Hardcode
        
        # 2. Rain Score (75.0mm/hr is 'extreme' for this area)
        rain_score = min(weather_data.get('precipitation') / 75.0, 1.0) * 30

        # dh/dt
        prev_height = await cls._get_previous_height(device_id)

        if prev_height is None:
            prev_height = 1

        velocity = (1 - prev_height) / 10.0 # Per 10 detik (Masih hardcode ketinggian)
        print(f"dv/dt = {velocity}")
        
        # 3. Total Probability
        probability = height_score + rain_score

        if velocity > 0.05:
            probability += 10
        elif velocity < 0:
            probability -= 5

        if sensor_data.get("is_wet"): # Untuk sementara waktu pake ini dulu
            return Classification.DANGER
        elif probability < 20:
            return Classification.SAFE
        elif  20 <= probability < 60:
            return Classification.CAUTION
        elif probability >= 60: 
            return Classification.DANGER

    @staticmethod
    async def _get_previous_height(device_id: str) -> float:
        pool = DatabaseClient.get_pool()
        # Merata-rata kan ketinggian selama 20 detik
        async with pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT avg(water_height)
                FROM sensor_readings
                WHERE sensor_id = $1
                    AND timestamp > NOW() - INTERVAL '30 seconds'
                    AND timestamp < NOW() - INTERVAL '10 seconds'
                """, device_id)