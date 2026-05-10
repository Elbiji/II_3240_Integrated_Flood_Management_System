CREATE TABLE sensors(
    sensor_id TEXT PRIMARY KEY,
    location TEXT NOT NULL
);

CREATE TABLE sensor_readings(
    timestamp TIMESTAMPTZ NOT NULL,
    sensor_id TEXT NOT NULL REFERENCES sensors(sensor_id),
    precipitation REAL NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    water_height REAL NOT NULL,
    water_height_change REAL NOT NULL,
    classification TEXT CHECK (classification IN ('SAFE','CAUTION','DANGER')),
    PRIMARY KEY (sensor_id, timestamp)
);

SELECT create_hypertable('sensor_readings', 'timestamp');