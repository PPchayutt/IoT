#include <WiFiS3.h>
#include <PubSubClient.h>
#include "DHT.h"

// ตั้งค่าขาที่ต่อกับขา S ของเซนเซอร์ DHT11
#define DHTPIN A4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// แก้ชื่อ Wi-Fi และรหัสผ่าน
const char* ssid = "Rattanamanee";
const char* password = "0816868621";

// ตั้งค่า MQTT Broker และ Topic ให้ตรงกับ server.py บน Raspberry Pi
const char* mqtt_server = "mqtt-dashboard.com";
const int mqtt_port = 1883;
const char* temp_topic = "mcp-115/temperature";
const char* client_id = "arduino-r4-pitchayut-115";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(client_id)) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();  // เริ่มการทำงานของเซนเซอร์ DHT11
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // อ่านค่าอุณหภูมิและส่งเข้า MQTT ทุกๆ 3 วินาที
  unsigned long now = millis();
  if (now - lastMsg > 3000) {
    lastMsg = now;

    // อ่านค่าอุณหภูมิเป็นองศาเซลเซียส (°C)
    float t = dht.readTemperature();

    if (!isnan(t)) {
      // สร้างข้อความ JSON เช่น {"temperature": 31.20} ส่งไปยัง MQTT Broker
      String payload = "{\"temperature\": " + String(t, 2) + "}";
      client.publish(temp_topic, payload.c_str());

      Serial.print("Published to ");
      Serial.print(temp_topic);
      Serial.print(" -> ");
      Serial.println(payload);
    } else {
      Serial.println("Failed to read from DHT11 sensor! Check wiring (S, VCC, GND).");
    }
  }
}