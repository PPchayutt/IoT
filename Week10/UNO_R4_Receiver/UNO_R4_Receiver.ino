#include <WiFiS3.h>
#include <PubSubClient.h>

const char ssid[] = "Rattanamanee";
const char pass[] = "0816868621";

WiFiClient net;
PubSubClient client(net);

// กำหนดขา LED
const int LED_ONOFF_PIN = 4;
const int LED_PWM_PIN = 9;

const char* topic = "kmitl/it115/lab2/sim";

// ฟังก์ชันดักจับข้อมูลเมื่อมีคน Publish มาที่ Topic
void callback(char* topic, byte* payload, unsigned int length) {
  // เช็คว่าได้รับข้อมูลมาครบ 2 bytes ตามที่ฝั่งส่งแพ็กมาหรือไม่
  if (length >= 2) {
    uint8_t swState = payload[0];
    uint8_t pwmValue = payload[1];
    
    // สั่งเปิด-ปิด และ หรี่ไฟ LED
    digitalWrite(LED_ONOFF_PIN, (swState == 1) ? HIGH : LOW);
    analogWrite(LED_PWM_PIN, pwmValue);
    
    Serial.print("Received -> LED State: "); Serial.print(swState);
    Serial.print(" | Brightness: "); Serial.println(pwmValue);
  }
}

void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("UNO_R4_Receiver_115")) {
      Serial.println(" Connected!");
      // Subscribe Topic เดียวกับฝั่งส่ง
      client.subscribe(topic);
    } else {
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(LED_ONOFF_PIN, OUTPUT);
  pinMode(LED_PWM_PIN, OUTPUT);
  
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" WiFi Connected!");

  client.setServer("broker.hivemq.com", 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) connectMQTT();
  client.loop();
}