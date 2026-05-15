/*
 * Sistem Bencana Alam Banjir Terpadu - IoT Node
 * 1 Soil Moisture Sensor + HC-SR04 Water Level + Relay Pump + MQTT
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ─────────────────────────────────────────────
// WiFi & MQTT
// ─────────────────────────────────────────────
const char* ssid         = "pinoc";          // ganti ke wifimu
const char* password     = "gabisaaa";       // ganti ke pw wifi
const char* mqtt_server  = "10.54.246.249";  // ubah ini ke ipmu
const int   mqtt_port    = 1883;

// ─────────────────────────────────────────────
// Pin Definitions
// ─────────────────────────────────────────────
#define SOIL_SENSOR_PIN   34
#define RELAY_PIN         26
#define HCSR04_TRIG_PIN   18   // ← sesuaikan ke pin ESP32mu
#define HCSR04_ECHO_PIN   19   // ← sesuaikan ke pin ESP32mu

// ─────────────────────────────────────────────
// Relay Logic
// ─────────────────────────────────────────────
#define RELAY_ON   HIGH
#define RELAY_OFF  LOW

// ─────────────────────────────────────────────
// Sensor Threshold
// ─────────────────────────────────────────────
#define SOIL_WET_THRESHOLD  3600   // nilai ADC <= ini = BASAH

// HC-SR04: jarak (cm) dari sensor ke permukaan air
// Semakin kecil jarak = air semakin tinggi
// Sesuaikan dengan tinggi wadah / instalasi sensor fisikmu
#define WATER_DANGER_CM     10.0   // ← air dianggap BAHAYA jika jarak <= ini
#define WATER_SIAGA_CM      20.0   // ← air dianggap SIAGA jika jarak <= ini
#define HCSR04_MAX_CM       400.0  // batas maksimum baca sensor (spec HC-SR04)
#define HCSR04_TIMEOUT_US   25000  // timeout pulseIn dalam microsecond

// ─────────────────────────────────────────────
// MQTT Topics
// ─────────────────────────────────────────────
const char* TOPIC_SENSOR  = "esp32_01/sensor_readings";
const char* TOPIC_PUMP    = "esp32_01/pump";
const char* TOPIC_CONTROL = "esp32_01/water_pump";

// ─────────────────────────────────────────────
// Timing
// ─────────────────────────────────────────────
const unsigned long PUBLISH_INTERVAL      = 5000;   // ms antar kirim data
const unsigned long SERVER_CONTROL_TIMEOUT = 30000; // ms sebelum fallback aktif

// ─────────────────────────────────────────────
// State
// ─────────────────────────────────────────────
WiFiClient   espClient;
PubSubClient mqttClient(espClient);

bool  pumpState        = false;
bool  serverHasControl = false;
unsigned long lastPublish      = 0;
unsigned long lastServerCommand = 0;


// ═════════════════════════════════════════════
// WIFI
// ═════════════════════════════════════════════
void setup_wifi() {
  delay(10);
  Serial.println("\n[WiFi] Connecting to: " + String(ssid));
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[WiFi] FAILED - cek SSID/password");
  }
}


// ═════════════════════════════════════════════
// SENSOR HELPERS
// ═════════════════════════════════════════════

// Rata-rata 10 sampel ADC untuk mengurangi noise
int readSoilAverage(int pin) {
  long total = 0;
  for (int i = 0; i < 10; i++) {
    total += analogRead(pin);
    delay(10);
  }
  return (int)(total / 10);
}

// Baca jarak HC-SR04 dalam cm, return -1 jika timeout/error
float readHCSR04() {
  // Pastikan trig LOW dulu
  digitalWrite(HCSR04_TRIG_PIN, LOW);
  delayMicroseconds(2);

  // Trigger 10µs pulse
  digitalWrite(HCSR04_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(HCSR04_TRIG_PIN, LOW);

  // Ukur lama echo pulse
  long duration = pulseIn(HCSR04_ECHO_PIN, HIGH, HCSR04_TIMEOUT_US);

  if (duration == 0) {
    Serial.println("[HCSR04] Timeout / no echo - sensor tidak terdeteksi");
    return -1.0;
  }

  float distanceCm = (duration * 0.0343) / 2.0;

  if (distanceCm > HCSR04_MAX_CM) {
    Serial.println("[HCSR04] Nilai di luar range - abaikan");
    return -1.0;
  }

  return distanceCm;
}

// Rata-rata 3 pembacaan HC-SR04 untuk stabilitas
float readHCSR04Average() {
  float total = 0;
  int valid   = 0;

  for (int i = 0; i < 3; i++) {
    float d = readHCSR04();
    if (d > 0) {
      total += d;
      valid++;
    }
    delay(60); // jeda antar pulse (spec: min 60ms)
  }

  if (valid == 0) return -1.0;
  return total / valid;
}

// Tentukan flood level dari jarak air (cm)
// Level 0 = AMAN, 1 = SIAGA, 2 = BAHAYA
int getWaterFloodLevel(float distanceCm) {
  if (distanceCm < 0) return 0;                       // sensor error → anggap aman
  if (distanceCm <= WATER_DANGER_CM) return 2;        // air sangat tinggi
  if (distanceCm <= WATER_SIAGA_CM) return 1;         // air mulai naik
  return 0;
}

const char* floodLevelLabel(int level) {
  switch (level) {
    case 2: return "BAHAYA";
    case 1: return "SIAGA";
    default: return "AMAN";
  }
}


// ═════════════════════════════════════════════
// PUMP CONTROL
// ═════════════════════════════════════════════
bool isServerControlActive() {
  return serverHasControl && (millis() - lastServerCommand < SERVER_CONTROL_TIMEOUT);
}

void publishPumpState(const char* reason) {
  StaticJsonDocument<128> doc;
  doc["pump"]           = pumpState;
  doc["reason"]         = reason;
  doc["control_source"] = isServerControlActive() ? "SERVER" : "SENSOR_FALLBACK";

  char buf[128];
  serializeJson(doc, buf);

  mqttClient.publish(TOPIC_PUMP, buf, true);
  Serial.println("[MQTT] Pump state published -> " + String(TOPIC_PUMP));
}

void setPump(bool on, const char* reason) {
  if (pumpState == on) {
    Serial.printf("[PUMP] Already %s (%s)\n", on ? "ON" : "OFF", reason);
    return;
  }

  pumpState = on;
  digitalWrite(RELAY_PIN, on ? RELAY_ON : RELAY_OFF);

  Serial.printf("[PUMP] %s (%s)\n", on ? "ON" : "OFF", reason);

  publishPumpState(reason);
}

void handlePumpCommand(bool pump) {
  serverHasControl    = true;
  lastServerCommand   = millis();

  setPump(pump, "server_command");
}

// Fallback logic jika server timeout:
// Pompa ON jika air BAHAYA (level 2) ATAU tanah basah DAN air SIAGA (level 1)
void sensorFallbackControl(bool soilIsWet, int waterLevel) {
  if (isServerControlActive()) {
    Serial.println("[PUMP] Server control aktif, fallback diabaikan");
    return;
  }

  if (serverHasControl) {
    Serial.println("[PUMP] Server timeout, sensor fallback aktif");
    serverHasControl = false;
  }

  bool shouldPumpOn = false;

  if (waterLevel >= 2) {
    // Air sudah BAHAYA → pompa ON
    shouldPumpOn = true;
    Serial.println("[FALLBACK] Trigger: air level BAHAYA");
  } else if (waterLevel == 1 && soilIsWet) {
    // Air SIAGA + tanah basah → pompa ON (kombinasi risiko tinggi)
    shouldPumpOn = true;
    Serial.println("[FALLBACK] Trigger: air SIAGA + tanah basah");
  } else {
    Serial.println("[FALLBACK] Kondisi aman, pompa OFF");
  }

  setPump(shouldPumpOn, shouldPumpOn ? "fallback_danger" : "fallback_safe");
}


// ═════════════════════════════════════════════
// MQTT
// ═════════════════════════════════════════════
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  msg.trim();

  Serial.println("[MQTT] Received on " + String(topic) + " -> " + msg);

  if (String(topic) == TOPIC_CONTROL) {
    StaticJsonDocument<128> doc;
    DeserializationError error = deserializeJson(doc, msg);

    if (!error) {
      bool pump = doc["pump"] | false;
      handlePumpCommand(pump);
      return;
    }

    // Fallback: plain text ON/OFF
    msg.toUpperCase();
    if (msg == "ON") {
      handlePumpCommand(true);
    } else if (msg == "OFF") {
      handlePumpCommand(false);
    } else {
      Serial.println("[MQTT] Perintah tidak dikenal: " + msg);
    }
  }
}

void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Connecting...");

    if (mqttClient.connect("ESP32Client")) {
      Serial.println(" terhubung");
      mqttClient.subscribe(TOPIC_CONTROL);
      Serial.println("[MQTT] Subscribed: " + String(TOPIC_CONTROL));
      publishPumpState("reconnected");
    } else {
      Serial.printf(" gagal (rc=%d), retry 5s\n", mqttClient.state());
      delay(5000);
    }
  }
}


// ═════════════════════════════════════════════
// MAIN READ & PUBLISH
// ═════════════════════════════════════════════
void readAndPublish() {
  // 1. Baca soil moisture
  int  soilValue = readSoilAverage(SOIL_SENSOR_PIN);
  bool soilIsWet = (soilValue <= SOIL_WET_THRESHOLD);

  // 2. Baca HC-SR04
  float waterDistanceCm = readHCSR04Average();
  int   waterLevel      = getWaterFloodLevel(waterDistanceCm);
  const char* waterStatus = floodLevelLabel(waterLevel);
  bool  sensorError     = (waterDistanceCm < 0);

  // 3. Log ke Serial
  Serial.printf("[SENSOR] Soil=%d(%s) | Air=%.1fcm Level=%d(%s)%s\n",
    soilValue,
    soilIsWet ? "BASAH" : "KERING",
    sensorError ? 0.0 : waterDistanceCm,
    waterLevel,
    waterStatus,
    sensorError ? " [SENSOR ERROR]" : ""
  );

  // 4. Publish ke MQTT
  // Kita pakai DynamicJsonDocument karena payload lebih besar
  StaticJsonDocument<320> doc;
  doc["soil_sensor"]       = soilValue;
  doc["soil_is_wet"]       = soilIsWet;
  doc["water_distance_cm"] = sensorError ? -1 : (int)(waterDistanceCm * 10) / 10.0;
  doc["water_level"]       = waterLevel;
  doc["water_status"]      = waterStatus;
  doc["hcsr04_error"]      = sensorError;
  doc["pump"]              = pumpState;
  doc["pump_mode"]         = isServerControlActive() ? "SERVER_CONTROL" : "SENSOR_FALLBACK";

  char buf[320];
  serializeJson(doc, buf);

  mqttClient.publish(TOPIC_SENSOR, buf);
  Serial.println("[MQTT] Published -> " + String(TOPIC_SENSOR));
  Serial.println("[MQTT] Payload: " + String(buf));

  // 5. Jalankan fallback control (diabaikan jika server aktif)
  sensorFallbackControl(soilIsWet, waterLevel);
}


// ═════════════════════════════════════════════
// SETUP & LOOP
// ═════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n=== Flood Detection System Booting ===");

  // Relay
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, RELAY_OFF);
  pumpState = false;
  Serial.println("[RELAY] Init - pompa OFF");

  // Soil sensor
  pinMode(SOIL_SENSOR_PIN, INPUT);
  Serial.println("[SOIL] Pin init OK");

  // HC-SR04
  pinMode(HCSR04_TRIG_PIN, OUTPUT);
  pinMode(HCSR04_ECHO_PIN, INPUT);
  digitalWrite(HCSR04_TRIG_PIN, LOW);
  Serial.println("[HCSR04] Pin init OK");

  // WiFi
  setup_wifi();

  // MQTT
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(mqttCallback);

  Serial.println("=== Boot selesai ===\n");
}

void loop() {
  // Reconnect WiFi jika putus
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Koneksi putus - reconnecting...");
    setup_wifi();
    return;
  }

  // Reconnect MQTT jika putus
  if (!mqttClient.connected()) {
    reconnect();
  }

  mqttClient.loop();

  // Publish setiap PUBLISH_INTERVAL ms
  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL) {
    lastPublish = now;
    readAndPublish();
  }
}
