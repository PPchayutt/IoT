#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

// 2. นำคีย์แบบ HEX array ของบอร์ด Receiver_Board มาวางที่ 3 บรรทัดนี้
static const u1_t PROGMEM APPEUI[8] = { 0x4E, 0x31, 0xD5, 0xFC, 0x57, 0x91, 0xEA, 0xC9 };
void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8);}

static const u1_t PROGMEM DEVEUI[8] = { 0x33, 0xE8, 0x1E, 0xA2, 0x50, 0x61, 0xCC, 0x3D };
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8);}

static const u1_t PROGMEM APPKEY[16] = { 0x95, 0xD9, 0x54, 0x69, 0xEF, 0xB6, 0xD5, 0x22, 0x7B, 0x33, 0xDC, 0x0C, 0x12, 0x01, 0xBA, 0x65 };
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16);}

const int LED_ONOFF_PIN = 4;
const int LED_PWM_PIN = 9;
static uint8_t mydata[] = "RX";
static osjob_t sendjob;
const unsigned TX_INTERVAL = 15; // ต้องส่งสัญญาณล่อทุก 15 วิ เพื่อให้หน้าต่างรับสัญญาณ (RX Window) เปิด

const lmic_pinmap lmic_pins = { .nss = 10, .rxtx = LMIC_UNUSED_PIN, .rst = 7, .dio = {2, 5, 6}, };

void do_send(osjob_t* j){
    if (!(LMIC.opmode & OP_TXRXPEND)) LMIC_setTxData2(1, mydata, sizeof(mydata)-1, 0);
}

void onEvent (ev_t ev) {
    Serial.print(os_getTime());
    Serial.print(": ");
    switch(ev) {
        case EV_JOINING:
            Serial.println(F("EV_JOINING... (กำลังขอเชื่อมต่อเครือข่าย)"));
            // บังคับล็อกความถี่ 923.2 MHz และปิดช่องอื่นทั้งหมดหลังจากเริ่มโหมด Join
            LMIC_setupChannel(0, 923200000, DR_RANGE_MAP(DR_SF12, DR_SF7), BAND_CENTI);
            for (int i = 1; i < 16; i++) {
                LMIC_disableChannel(i);
            }
            LMIC_setDrTxpow(DR_SF7, 14);
            break;
        case EV_JOINED:
            Serial.println(F("EV_JOINED!!! (เชื่อมต่อสำเร็จแล้ว!)"));
            LMIC_setLinkCheckMode(0);
            break;
        case EV_JOIN_FAILED:
            Serial.println(F("EV_JOIN_FAILED (เชื่อมต่อล้มเหลว)"));
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE (ส่งข้อมูลเสร็จสิ้น และหมดเวลารอ RX แล้ว)"));
            if (LMIC.dataLen >= 2) {
                uint8_t swState = LMIC.frame[LMIC.dataBeg + 0];
                uint8_t pwmValue = LMIC.frame[LMIC.dataBeg + 1];
                digitalWrite(LED_ONOFF_PIN, (swState == 1) ? HIGH : LOW);
                analogWrite(LED_PWM_PIN, pwmValue);
                Serial.print(F("Downlink Received -> LED: ")); Serial.print(swState);
                Serial.print(F(" | Brightness: ")); Serial.println(pwmValue);
            }
            os_setTimedCallback(&sendjob, os_getTime()+sec2osticks(TX_INTERVAL), do_send);
            break;
        case EV_TXSTART:
            Serial.println(F("EV_TXSTART (เริ่มส่งคลื่นวิทยุ)"));
            break;
        case EV_JOIN_TXCOMPLETE:
            Serial.println(F("EV_JOIN_TXCOMPLETE: no JoinAccept (ไม่ได้รับคำตอบรับจาก Gateway)"));
            break;
        default:
            Serial.print(F("Unknown event: "));
            Serial.println((unsigned) ev);
            break;
    }
}

void setup() {
    Serial.begin(9600);
    pinMode(LED_ONOFF_PIN, OUTPUT);
    pinMode(LED_PWM_PIN, OUTPUT);
    os_init();
    LMIC_reset();
    LMIC_setClockError(MAX_CLOCK_ERROR * 10 / 100);
    do_send(&sendjob);
}
void loop() { os_runloop_once(); }