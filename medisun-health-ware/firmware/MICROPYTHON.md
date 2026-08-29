# Medisun Health-Ware — ESP32-S3 firmware skeleton (MicroPython)

Follows the NextBand/Aegis pin pattern. This is the **P2 wearable** build — the software spine
(the bridge + identity) is already done; this gets the device talking to it.

## Hardware
- MCU: **ESP32-S3 N16R8** (16MB flash / 8MB PSRAM)
- Mic: **INMP441** (I2S, digital MEMS)
- Vitals: **MAX30102** (heart rate + SpO2, I2C)
- Optional: LiPo + USB-C, power switch

## Pin map (per NextBand — verify against your board before flashing)
| Signal | ESP32-S3 pin |
|---|---|
| I2S WS (mic) | GPIO4 |
| I2S BCK | GPIO5 |
| I2S DIN | GPIO6 |
| MAX30102 SDA | GPIO8 |
| MAX30102 SCL | GPIO9 |
| I2S output / amp | (PAM8403, optional) |

## MicroPython skeleton (record audio → POST wifi → bridge `/ingest`)
```python
# firmware/main.py  (MicroPython on ESP32-S3)
import network, urequests, time, machine, ujson
from machine import I2S, Pin, I2C

BRIDGE = "http://<DOCK_IP>:8108/ingest"
SSID, PASS = "medisun-iot", "REDACTED"   # sealed, never in git

def connect():
    w = network.WLAN(network.STA_IF); w.active(True); w.connect(SSID, PASS)
    while not w.isconnected(): time.sleep(0.5)
    print("wifi ok", w.ifconfig()[0])

def read_vitals():
    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
    # MAX30102 is a red/IR photoplethysmograph; the actual HR/SpO2 algorithm
    # is a register-read + DSP. For the MVP skeleton, this is the seam.
    return {"heart_rate": 0.0, "spo2": 0.0}   # TODO: reads 0x0f (part id) etc.

def loop():
    connect()
    while True:
        v = read_vitals()
        try:
            urequests.post(BRIDGE, json={"device_id":"medisun-band-0001",
                "heart_rate":v["heart_rate"], "spo2":v["spo2"], "operator":"medic"},
                timeout=10)
        except Exception as e:
            print("bridge err", e)
        time.sleep(10)
```

## Flashing
```bash
mpremote connect <port> fs cp firmware/main.py :main.py
# or ESP-IDF: idf.py set-target esp32s3 && idf.py build flash monitor
```

## Notes / honest caveats
- MAX30102 HR/SpO2 requires the red/IR ratio + HRA algorithm — the skeleton stubs it; the real
  firmware needs the vendor datasheet DSP (or a validated open lib like `max30102`).
- Audio (INMP441) → I2S bytes → the bridge `/ingest` `audio` field → whisper (sovereign). MVP runs
  the data path; the STT lane is the next increment.
- **Never flash real PHI or the SSID/password into git.** Secrets sealed in `.env` (0600).
