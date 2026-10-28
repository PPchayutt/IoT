#include <WiFiS3.h>
#include <PubSubClient.h>

const char ssid[] = "Rattanamanee";
const char pass[] = "0816868621";

WiFiClient net;
PubSubClient client(net);

// กำหนดขาเซนเซอร์
const int SWITCH_PIN = 3;
const int POT_PIN = A0;

// หัวข้อ MQTT Topic สำหรับทดสอบ (ตั้งให้ไม่ซ้ำใคร)
const char* topic = "kmitl/it115/lab2/sim";
unsigned long lastMillis = 0;

void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    // ตั้งชื่อ Client ID ให้ไม่ซ้ำกัน
    if (client.connect("UNO_R4_Sender_115")) {
      Serial.println(" Connected!");
    } else {
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" WiFi Connected!");

  // ใช้ HiveMQ Public Broker จำลองแทนของคณะ
  client.setServer("broker.hivemq.com", 1883);
}

void loop() {
  if (!client.connected()) connectMQTT();
  client.loop();

  // ส่งข้อมูลทุกๆ 3 วินาที
  if (millis() - lastMillis > 3000) { 
    lastMillis = millis();
    
    // 1. อ่านค่าและเตรียมข้อมูลแบบเดียวกับ LoRaWAN
    uint8_t swState = (digitalRead(SWITCH_PIN) == LOW) ? 1 : 0;
    uint8_t pwmValue = map(analogRead(POT_PIN), 0, 1023, 0, 255);
    
    // 2. แพ็กข้อมูล 2 bytes ลง Array
    uint8_t payload[2] = {swState, pwmValue};

    // 3. ส่งข้อมูลขึ้น MQTT
    client.publish(topic, payload, 2);
    
    Serial.print("Sent -> Switch: "); Serial.print(swState);
    Serial.print(" | PWM: "); Serial.println(pwmValue);
  }
}