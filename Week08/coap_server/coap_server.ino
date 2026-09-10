#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <coap-simple.h>

const char WIFI_SSID[] = "Free Robux";
const char WIFI_PASSWORD[] = "555555333311";
const uint16_t COAP_PORT = 5683; 

WiFiUDP udp;
Coap coap(udp);
int lastMappedValue = -1; 

// ฟังก์ชัน Handle สำหรับ GET Request
void handlePot(CoapPacket &packet, IPAddress ip, int port) {
  int potValue = analogRead(A0); // อ่านค่าแรงดัน (0-5V) สำหรับรองรับ GET
  int mappedValue = map(potValue, 0, 1023, 0, 100); // Scale ให้อยู่ในช่วง 0-100
  
  String payload = String(mappedValue);
  char messageBuffer[100];
  payload.toCharArray(messageBuffer, 100);
  coap.sendResponse(ip, port, packet.messageid, messageBuffer);
}

void connectWiFi() {
  int status = WL_IDLE_STATUS;
  while (status != WL_CONNECTED) {
    status = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(10000);
  }
  Serial.print("WiFi IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  connectWiFi();
  
  udp.begin(COAP_PORT);
  coap.server(handlePot, "pot"); // ลงทะเบียน resource ชื่อ pot
  coap.start();
}

void loop() {
  coap.loop(); // ประมวลผลคำขอที่เข้ามา

  // ค้นคว้าและเขียนโปรแกรมให้ CoAP Server รองรับ Observe Feature
  int potValue = analogRead(A0);
  int mappedValue = map(potValue, 0, 1023, 0, 100);
  
// ตรวจสอบว่าค่าเปลี่ยนไปหรือไม่ (ใส่เงื่อนไขความต่าง >= 2 เพื่อลดสัญญาณรบกวน)
if (abs(mappedValue - lastMappedValue) >= 2) {
  lastMappedValue = mappedValue;
  
  // 1. แปลงค่าตัวเลขให้เป็น String
  String payload = String(mappedValue);
  
  // 2. ส่งข้อมูลให้ครบ 4 Arguments: (ชื่อ resource, ค่าที่ส่ง, ความยาว, ชนิดข้อมูล)
  coap.notify("pot", payload.c_str(), payload.length(), COAP_TEXT_PLAIN); 
}
  delay(50);
}