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

The `main()` function in `esp32/sensors/sths34pf80.py` was written by me after
studying the sample code in the `Adafruit_CircuitPython_STHS34PF80` GitHub
repository. I used the sample code provided in the repository to learn the library API and typical usage pattern before writing my own sensor read code.

## Project Evolution

This project started with the STHS34PF80 and BME680 sensors wired directly to
the Raspberry Pi 5 for early bring-up and sensor validation. The architecture is
now moving to an ESP32 sensor gateway that reads both sensors over I2C and will
publish readings to the Pi over MQTT. The previous Pi-direct sensor architecture
is preserved in the `pi-only-v1` git tag.

## Current Status

- Raspberry Pi set up and running
- MQTT broker configured
- Publisher/subscriber scripts in progress
- ESP32 integration on hold
- STHS34PF80 soldered and wired
- BME680 soldered, awaiting wiring
- Dashboard in planning

## Project Structure

```
smart-home-sensor/
├── .gitignore
├── LICENSE
├── README.md
├── docs/
│   └── wiring.md
├── esp32/
│   ├── main.py
│   └── sensors/
│       ├── bme680.py
│       └── sths34pf80.py
├── pi/
│   ├── dashboard/
│   │   └── app.py
│   └── mqtt/
│       ├── publisher.py
│       └── subscriber.py
├── sensors/
│   ├── read_bme680.py
│   └── read_sths34pf80.py
```
