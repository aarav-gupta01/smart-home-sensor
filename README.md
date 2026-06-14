# Smart Home Sensor Network

A comprehensive smart home sensor network built on a Raspberry Pi 5, enabling real-time environmental monitoring and presence detection with MQTT-based communication.

## Overview

This project creates an intelligent IoT sensor network for smart home automation. An ESP32 microcontroller reads environmental and occupancy data from multiple sensors, which is then published via MQTT to a Raspberry Pi 5 acting as the central broker. The Raspberry Pi logs the data persistently and serves it through a local web dashboard for real-time monitoring and analytics.

## System Architecture

### Hardware Components

- **Raspberry Pi 5**: Central hub, MQTT broker, data logger, and dashboard server
- **ESP32**: Sensor gateway with WiFi connectivity
- **BME680 Sensor**: Comprehensive environmental monitoring
  - Temperature
  - Humidity
  - Atmospheric Pressure
  - Volatile Organic Compound (VOC) detection
- **STHS34PF80 Sensor**: Presence/occupancy detection

### Communication Flow

```
[Sensors] → [ESP32] → [WiFi + MQTT] → [Raspberry Pi 5]
                                            ↓
                                    [Data Logger]
                                            ↓
                                    [Web Dashboard]
```

## Features

- **Multi-sensor Environmental Monitoring**: Track temperature, humidity, pressure, and air quality
- **Presence Detection**: Real-time occupancy sensing with the STHS34PF80
- **MQTT Protocol**: Lightweight, reliable communication between ESP32 and Raspberry Pi
- **Data Persistence**: Continuous logging of sensor readings for historical analysis
- **Web Dashboard**: Local visualization of real-time and historical sensor data
- **Smart Home Ready**: Foundation for automation rules and integrations

## Project Status

**Early Development** - This project is in its initial phases. Core architecture and hardware integration work is planned.

## Planned Milestones

1. **Phase 1**: ESP32 sensor integration and MQTT communication
2. **Phase 2**: Raspberry Pi MQTT broker setup and data logging
3. **Phase 3**: Web dashboard development and visualization
4. **Phase 4**: Data analytics and reporting features
5. **Phase 5**: Smart home automation integrations

## Requirements

### Hardware

- Raspberry Pi 5 with power supply
- ESP32 development board
- BME680 environmental sensor module
- STHS34PF80 presence sensor module
- WiFi router (for ESP32 connectivity)
- Micro USB or USB-C cables
- Breadboard and jumper wires (for prototyping)

### Software (Planned)

- Python 3.8+ (for Raspberry Pi)
- Arduino IDE or PlatformIO (for ESP32)
- MQTT broker (Mosquitto or similar)
- Database (SQLite or InfluxDB)
- Web framework (Flask, FastAPI, or similar)
- Node.js (optional, for web dashboard)

## Getting Started

_Instructions will be added as the project develops._

### Installation

_Coming soon_

### Configuration

_Coming soon_

### Running the Project

_Coming soon_

## Project Structure

```
smart-home-sensor/
├── README.md
├── LICENSE
├── docs/                    # Documentation
├── esp32/                   # ESP32 firmware
│   ├── src/
│   └── config/
├── raspberry-pi/            # Raspberry Pi applications
│   ├── mqtt-broker/
│   ├── data-logger/
│   └── web-dashboard/
├── hardware/                # Hardware schematics and BOM
├── tests/                   # Test suites
└── scripts/                 # Utility and setup scripts
```

## Sensor Specifications

### BME680
- Temperature: -40°C to +85°C
- Humidity: 0% to 100%
- Pressure: 300 hPa to 1100 hPa
- VOC: Detectable air quality changes
- Interface: I2C/SPI

### STHS34PF80
- Presence Detection: Up to 4 meters
- Temperature Sensing: -20°C to +80°C
- Field of View: ~110°
- Interface: I2C

## Networking

- **Protocol**: MQTT over TCP/IP
- **Default Port**: 1883 (or 8883 for TLS)
- **QoS Levels**: 0, 1, 2
- **Topic Structure**: `/home/[room]/[sensor]/[reading_type]`

## Data Logging

- Persistent storage of all sensor readings
- Timestamped entries for historical analysis
- Support for data export and analytics

## Dashboard Features (Planned)

- Real-time sensor value display
- Historical graphs and trends
- Alerts and notifications
- Multi-room support
- Mobile-responsive design

## Contributing

Contributions are welcome! For now, as the project is in its early stages, please:

1. Open an issue to discuss major changes
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] ESP32 firmware development
- [x] MQTT broker configuration
- [ ] Data logging system
- [ ] Web dashboard UI/UX design
- [ ] Data visualization
- [ ] Automation rule engine
- [ ] Mobile app support
- [ ] Cloud integration (optional)

## Troubleshooting

_Will be expanded as common issues are encountered._

## References and Resources

- [BME680 Datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf)
- [STHS34PF80 Datasheet](https://www.st.com/resource/en/datasheet/sths34pf80.pdf)
- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [MQTT Protocol](https://mqtt.org/)

## Contact & Support

For questions or suggestions, please open an issue on this repository.

---

**Last Updated**: June 2026  
**Project Status**: Early Development
