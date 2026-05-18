# II3240
> A prototype for developing Early Warning System (EWS) for floods.

Sistem ini dibangun diberbagai teknologi seperti TimescaleDB (Ekstensi postgreSQL) untuk penanganan database timeseries, Mosquitto sebagai broker IoT, Nextjs sebagai framework website, FastAPI sebagai layanan BE dan Docker untuk proses spin up layanan yang cepat dan proses kolaborasi yang lebih efisien. Seluruh layanan memiliki kontainer masing-masing yang berada di dalam file Docker-compose.yaml. Keputusan dalam pemilihan Docker adalah untuk membantu membuat layanan yang gampang diskalakan dan direplikasikan di berbagai mesin. 

| Implementasi                     | /Parsial/Largely/Fully  |
|----------------------------------|-------------------------|
| BE-pembacaan sensor IoT          | Largely                 |
| BE-proses inferensi IoT          | Parsial                 |
| BE-penyimpanan data IoT          | Fully                   |
| BE-pembacaan layanan eksternal   | Fully                   |
| BE-rate limiter                  | Fully                   |
| BE-rate limiter                  | Fully                   |
| BE-endpoint web                  | Largely                 |
| FE-tampilan data cuaca           | Fully                   |
| FE-tampilan peta IoT             | Fully                   |
| FE-tampilan inferensi            | Fully                   |
| FE-tampilan grafik ketinggian air| Fully                   |
| FE-tampilan grafik dv/dt air     | Fully                   |
| FE-tampilan lokasi               | Fully                   |

Sangat penting untuk digarisbawahi bahwa layanan ini belum sepenuhnya fungsional sehingga masih terdapat beberapa ketidaksesuain dengan spesifikasi pada dokuman.

# Struktur Folder
  ```bash
      .
      ├── infra/
      │ ├── mosquitto/ # Konfigurasi mosquitto
      │ │ ├── config 
      │ │ │ └── mosquitto.conf
      │ │ ├── data 
      │ │ │ └── mosquitto.db
      │ │ └── log
      │ │   └── mosquitto.log
      │ ├── redis/ # Konfigurasi redis
      │ │ └── redis.conf
      │ └── timescaledb # Konfigurasi skema database
      │   └── init.sql
      ├── services/
      │ ├── .venv/ # Interpreter BE berbasis python 
      │ ├── app/
      │ │ ├── model/
      │ │ │ └── schemas.py # Type checking untuk database (DDD)
      │ │ ├── routes/
      │ │ │ ├── __init__.py
      │ │ │ ├── mqtt_handler.py # Menangani komunikasi dengan IoT
      │ │ │ └── web_handler.py # Menangani komunikasi dengan Web
      │ │ ├── services/
      │ │ │ ├── __init__.py 
      │ │ │ └── inference_engine.py # Mesin RBS
      │ │ ├── __init__.py
      │ │ ├── config.py # Singleton untuk seluruh client (redis, db, broker, httpx)
      │ │ ├── main.py # Entrypoint FastAPI
      │ │ └── middleware.py # Rate limiter dengan Redis
      │ ├── .dockerignore
      │ ├── .python-version
      │ ├── Dockerfile
      │ ├── pyproject.toml
      │ ├── README.md
      │ └── uv.lock
      ├── web/
      │ ├── my-app/
      │ │ ├── public/
      │ │ ├── src/
      │ │ │ ├── app/
      │ │ │ │ ├── globals.css
      │ │ │ │ ├── layout.tsx
      │ │ │ │ └── page.tsx
      │ │ │ ├── components/
      │ │ │ │ ├── charts/
      │ │ │ │ │ └── WaterHeight_Chart.tsx
      │ │ │ │ └── ui
      │ │ │ │   ├── card.tsx
      │ │ │ │   ├── map.tsx
      │ │ │ │   ├── MapWidget.tsx
      │ │ │ │   ├── ServerClock.tsx
      │ │ │ │   └── WeatherWidget.tsx
      │ │ │ └──  lib/
      │ │ │  └── api.ts # Logika routing api menggunakan jaringan internal docker atau eksternal
      │ │ ├── .gitignore
      │ │ ├── .AGENTS.md
      │ │ ├── biome.json
      │ │ ├── CLAUDE.md
      │ │ ├── components.json
      │ │ ├── Dockerfile
      │ │ ├── next.config.ts
      │ │ ├── package-lock.json
      │ │ ├── package.json
      │ │ ├── postcss.config.mjs
      │ │ ├── README.md
      │ │ └── tsconfig.json
      │ └── node_modules/
      ├── .env # Variable Lingkungan
      ├── gitignore
      ├── docker-compose.yml # Konfigurasi keseluruhan sistem
      └── README.md
  ```

Visualsiasi struktur ini dibuat untuk memudahkan pemahaman struktur kode keseluruhan pada projek. Dockerfile berada di dua folder utama yaitu `services` dan `web`. Dockerfile digunakan untuk pembentukan image yang nantinya akan dipakai pada docker-compose.yml. 

# Daftar Endpoint

|Method        | Endpoint               | Fungsi                                                     |
|--------------|------------------------|------------------------------------------------------------|
| GET          | /api/v1/sensors/{device_id}/history                 | Mengambil data sensor berdasarkan ID sensor                               | 
| GET          | /api/v1/sensors/{device_id}/weather_history              | Mengambil data cuaca berdasarkan ID sensor     | 
| GET          | /api/v1/sensors/{device_id}/information         | Mengambil informasi data sensor berdasrkan ID sensor  | 
| GET          | /api/v1/services/{device_id}/inference  | Mengambil hasil inferensi data sensor berdasrakan ID sensor                       | 
| GET          | /api/v1/services/weather    | Mengambil data cuaca      | 
| GET          | /root    | Mengembalikan nama layanan     | 
| GET          | /health    | Mengembalikan status layanan      | 

# How to RUN

  ```bash
        GOOGLE_API_WEATHER_KEY ={}
        GOOGLE_CLIENT={}
        GOOGLE_REDIRECT_URI={}
        GOOGLE_SECRET={}
        REDIS_URL=redis://redis:6379
        DATABASE_URL=postgresql://postgres:password@timescaledb:5432/flooddb
        DATABASE_SERVICE = http://timescaledb:5432
        MQTT_BROKER_SERVICE = mqtt://mosquitto:1883
        MQTT_HOST = mosquitto
        MQTT_PORT = 1883
        GATEWAY_SERVICE = http://gateway:8000
        TOKEN_EXPIRE=60
  ```
  ```bash
        docker compose up -d
  ```

