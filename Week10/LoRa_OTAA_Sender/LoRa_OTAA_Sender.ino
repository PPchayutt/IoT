#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

// 1. นำคีย์แบบ HEX array ของบอร์ด Sender_Board มาวางที่ 3 บรรทัดนี้
static const u1_t PROGMEM APPEUI[8] = { 0xBA, 0x5F, 0xE2, 0x05, 0xD9, 0xB8, 0xFB, 0x0E };
void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8);}

static const u1_t PROGMEM DEVEUI[8] = { 0x3D, 0xEA, 0x6F, 0x5E, 0x3A, 0xC7, 0x10, 0x99 };
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8);}

static const u1_t PROGMEM APPKEY[16] = { 0x47, 0xA3, 0x69, 0xB8, 0xED, 0x2D, 0xD7, 0x34, 0x95, 0x9B, 0x35, 0xBC, 0xB1, 0x20, 0x85, 0x94 };
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16);}

const int SWITCH_PIN = 3;
const int POT_PIN = A0;
static uint8_t mydata[2];
static osjob_t sendjob;
const unsigned TX_INTERVAL = 15; // ส่งทุกๆ 15 วินาที

const lmic_pinmap lmic_pins = { .nss = 10, .rxtx = LMIC_UNUSED_PIN, .rst = 7, .dio = {2, 5, 6}, };

void do_send(osjob_t* j){
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, not sending"));
    } else {
        uint8_t swState = (digitalRead(SWITCH_PIN) == LOW) ? 1 : 0;
        uint8_t pwmValue = map(analogRead(POT_PIN), 0, 1023, 0, 255);
        mydata[0] = swState;
        mydata[1] = pwmValue;
        
        Serial.print(F("Sending -> Switch: ")); Serial.print(swState);
        Serial.print(F(" | PWM: ")); Serial.println(pwmValue);
        LMIC_setTxData2(1, mydata, sizeof(mydata), 0);
    }
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
    pinMode(SWITCH_PIN, INPUT_PULLUP);
    os_init();
    LMIC_reset();
    LMIC_setClockError(MAX_CLOCK_ERROR * 10 / 100);
    do_send(&sendjob);
}
void loop() { os_runloop_once(); }