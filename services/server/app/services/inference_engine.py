from app.model.schemas import Classification
from app.config import DatabaseClient
from app.services.inference_config import InferenceConfig

class InferenceEngine:
    @classmethod 
    async def calculate_inference(cls, weather_data: dict, sensor_data: dict, device_id: str) -> tuple[Classification, float, float]:
        curr_height = InferenceConfig.CONTAINER_HEIGHT - sensor_data.get('water_distance_cm')
        
        # 1. Height Score 
        height_score = (curr_height / InferenceConfig.CRITICAL_HEIGHT) * 70 
        
        # 2. Rain Score 
        rain_score = (weather_data.get('precipitation') / InferenceConfig.CRITICAL_RAIN_PRECIPITATION) * 30

        # dh/dt
        velocity = await cls._calculate_velocity_of_change(device_id, sensor_data.get('water_distance_cm'))
        
        # 3. Total Probability
        probability = height_score + rain_score

        if velocity > InferenceConfig.CRITICAL_RATE_OF_CHANGE:
            probability += 100
        else:
            probability -= 10

        if probability < 20:
            return Classification.SAFE, velocity, curr_height
        elif  20 <= probability < 60:
            return Classification.CAUTION, velocity, curr_height
        elif probability >= 60: 
            return Classification.DANGER, velocity, curr_height
        
    @staticmethod
    async def _calculate_velocity_of_change(device_id: str, curr_height: float) -> float:
        prev_height = await InferenceEngine._get_avg_previous_height(device_id=device_id)

        if prev_height is None:
            prev_height = curr_height

        # Per 10 detik (cm/s)
        velocity = (curr_height - prev_height) / 10.0
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
    
    # TODO
    @staticmethod 
    async def _get_current_sensor_data(device_id: str) -> dict:
        pool = DatabaseClient.get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch("""
                SELECT 
                """)