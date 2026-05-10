from app.model.schemas import Classification
from app.config import DatabaseClient

class InferenceEngine:
    @classmethod 
    async def calculate_inference(cls, weather_data: dict, sensor_data: dict, device_id: str) -> Classification:
        print(type(sensor_data.get("is_wet")))
        
        # 1. Height Score (4.5m is our 'critical' threshold)
        height_score = min(1 / 4.5, 1.0) * 70 # Hardcode
        
        # 2. Rain Score (75.0mm/hr is 'extreme' for this area)
        rain_score = min(weather_data.get('precipitation') / 75.0, 1.0) * 30

        # dh/dt
        velocity = await cls._calculate_velocity_of_change(device_id)
        
        # 3. Total Probability
        probability = height_score + rain_score

        if velocity > 0.05:
            probability += 10
        elif velocity < 0:
            probability -= 5

        if sensor_data.get("is_wet"): # Untuk sementara waktu pake ini dulu
            return Classification.DANGER, velocity
        elif probability < 20:
            return Classification.SAFE
        elif  20 <= probability < 60:
            return Classification.CAUTION, velocity
        elif probability >= 60: 
            return Classification.DANGER, velocity
        
    @staticmethod
    async def _calculate_velocity_of_change(device_id: str) -> float:
        prev_height = await InferenceEngine._get_avg_previous_height(device_id=device_id)

        if prev_height is None:
            prev_height = 1

        velocity = (1 - prev_height) / 10.0
        print(f"dv/dt = {velocity}")

        return velocity

    @staticmethod
    async def _get_avg_previous_height(device_id: str) -> float:
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
        
    @staticmethod 
    async def _get_current_sensor_data(device_id: str) -> dict:
        pool = DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch("""
                SELECT 
                """)