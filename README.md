# Smart Home Sensor Network

A smart home sensor network using a Raspberry Pi 5 as the main hub and MQTT broker.
An ESP32 microcontroller collects data from a BME680 environmental sensor and an
STHS34PF80 presence sensor, creating a WiFi pipeline from the sensors to the Pi,
which renders the data onto a web dashboard.

## Hardware

| Component | Role |
|---|---|
| Raspberry Pi 5 | Main hub, MQTT broker, dashboard server |
| ESP32 Microcontroller | MQTT publisher, sensor gateway |
| BME680 Environmental Sensor | Temperature, humidity, pressure, VOC |
| STHS34PF80 Presence Sensor | Thermal signature and motion detection |

## Software

The MQTT broker is configured and running on the Raspberry Pi. Basic
publisher and subscriber scripts are functional.

## Current Status

- [x] Raspberry Pi set up and running
- [x] MQTT broker configured
- [x] Publisher/subscriber scripts working
- [ ] ESP32 in shipment
- [ ] STHS34PF80 soldered, awaiting wiring
- [ ] BME680 awaiting soldering and wiring
- [ ] Dashboard in planning

## Project Structure

```
smart-home-sensor/
├── README.md
├── LICENSE
├── .gitignore
├── pi/
│   ├── mqtt/
│   │   ├── publisher.py
│   │   └── subscriber.py
│   └── dashboard/
│       └── app.py
├── esp32/
│   └── main.py
└── docs/
    └── wiring.md
```
