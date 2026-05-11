/*
 * Sistem Bencana Alam Banjir Terpadu - IoT Node
 * 1 Soil Moisture Sensor + Relay Pump + MQTT
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi & MQTT
const char* ssid         = "pinoc"; //ganti ke wifimu
const char* password     = "gabisaaa"; //ganti ke pw wifi
const char* mqtt_server  = "10.238.43.249"; //ubah ini ke ipmu
// caranya :
// 1. buka terminal
// 2. ipconfig
// 3. cari wlan adapter
// 4. cari yg ipv4 address
// 5. salin ipnya kesini ^
const int   mqtt_port    = 1883;

// Pin Definitions
#define SOIL_SENSOR_PIN 34
#define RELAY_PIN       26

// Relay Logic - based on your tested pump code
#define RELAY_ON  HIGH
#define RELAY_OFF LOW

// Sensor threshold - based on your tested sensor code
#define WET_THRESHOLD 3600

// MQTT Topics
const char* TOPIC_SENSOR  = "esp32_01/sensor_readings";
const char* TOPIC_PUMP    = "esp32_01/pump";
const char* TOPIC_CONTROL = "esp32_01/water_pump";

// Timing
const unsigned long PUBLISH_INTERVAL = 5000;
const unsigned long SERVER_CONTROL_TIMEOUT = 30000;

// State
WiFiClient espClient;
PubSubClient mqttClient(espClient);

bool pumpState = false;
bool serverHasControl = false;
unsigned long lastPublish = 0;
unsigned long lastServerCommand = 0;

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
    Serial.println("\n[WiFi] FAILED - check SSID/password");
  }
}

int readAverage(int pin) {
  int total = 0;

  for (int i = 0; i < 10; i++) {
    total += analogRead(pin);
    delay(10);
  }

  return total / 10;
}

bool isServerControlActive() {
  return serverHasControl && (millis() - lastServerCommand < SERVER_CONTROL_TIMEOUT);
}

void publishPumpState(const char* reason) {
  StaticJsonDocument<128> doc;
  doc["pump"] = pumpState;
  doc["reason"] = reason;
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
  serverHasControl = true;
  lastServerCommand = millis();

  if (pump) {
    setPump(true, "server_callback");
  } else {
    setPump(false, "server_callback");
  }
}

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

    msg.toUpperCase();

    if (msg == "ON") {
      handlePumpCommand(true);
    } else if (msg == "OFF") {
      handlePumpCommand(false);
    } else {
      Serial.println("[MQTT] Unknown pump command: " + msg);
    }
  }
}

void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("[MQTT] Connecting...");

    if (mqttClient.connect("ESP32Client")) {
      Serial.println(" connected");

      mqttClient.subscribe(TOPIC_CONTROL);
      Serial.println("[MQTT] Subscribed to: " + String(TOPIC_CONTROL));

      publishPumpState("reconnected");
    } else {
      Serial.printf(" failed (rc=%d), retry in 5s\n", mqttClient.state());
      delay(5000);
    }
  }
}

void sensorFallbackControl(bool isWet) {
  if (isServerControlActive()) {
    Serial.println("[PUMP] Server control active, sensor fallback ignored");
    return;
  }

  if (serverHasControl) {
    Serial.println("[PUMP] Server control timeout, sensor fallback enabled");
    serverHasControl = false;
  }

  if (isWet) {
    setPump(true, "sensor_fallback_wet");
  } else {
    setPump(false, "sensor_fallback_dry");
  }
}

void readAndPublish() {
  int soilValue = readAverage(SOIL_SENSOR_PIN);

  bool isWet = soilValue <= WET_THRESHOLD;

  int floodLevel = 0;
  const char* floodStatus = "AMAN";

  if (isWet) {
    floodLevel = 1;
    floodStatus = "SIAGA";
  }

  Serial.printf("[SENSOR] Soil=%d(%s) -> Level %d (%s)\n",
    soilValue,
    isWet ? "WET" : "DRY",
    floodLevel,
    floodStatus
  );

  Serial.printf("[SENSOR] Raw=%d  Threshold=%d  isWet=%s\n",
    soilValue,
    WET_THRESHOLD,
    isWet ? "YES" : "NO"
  );

  StaticJsonDocument<256> doc;
  doc["soil_sensor"]  = soilValue;
  doc["is_wet"]       = isWet;
  doc["flood_level"]  = floodLevel;
  doc["flood_status"] = floodStatus;
  doc["pump"]         = pumpState;
  doc["pump_mode"]    = isServerControlActive() ? "SERVER_CONTROL" : "SENSOR_FALLBACK";

  char buf[256];
  serializeJson(doc, buf);

  mqttClient.publish(TOPIC_SENSOR, buf);
  Serial.println("[MQTT] Published -> " + String(TOPIC_SENSOR));

  sensorFallbackControl(isWet);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n=== Flood Detection System Booting ===");

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, RELAY_OFF);
  pumpState = false;

  Serial.println("[RELAY] Initialized - pump OFF");

  pinMode(SOIL_SENSOR_PIN, INPUT);

  setup_wifi();

  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(mqttCallback);

  Serial.println("=== Boot complete ===\n");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Lost connection - reconnecting...");
    setup_wifi();
    return;
  }

  if (!mqttClient.connected()) {
    reconnect();
  }

  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL) {
    lastPublish = now;
    readAndPublish();
  }
}
