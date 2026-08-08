# Smart Home Sensor Network

A work-in-progress smart-home sensing system built around an ESP32 and a
Raspberry Pi 5. The ESP32 currently reads a BME680 environmental sensor and an
STHS34PF80 infrared presence sensor over one I2C bus and prints their readings
to its serial console.

The longer-term goal is for the ESP32 to publish those readings over Wi-Fi and
MQTT to a Mosquitto broker on the Raspberry Pi, where they can be displayed in
a web dashboard. The Wi-Fi and MQTT link now works end to end as a standalone
script with a hardcoded test payload, but it is not yet driven by real sensor
readings, and the dashboard is not implemented.

## Current Status

Implemented and hardware-tested locally:

- MicroPython is running on the ESP32 (`ESP32_GENERIC` build).
- Both sensors are detected on the shared I2C bus: STHS34PF80 at `0x5A` and
  BME680 at `0x76`.
- `esp32/main.py` initializes both sensors and services them in one continuous
  loop.
- Both sensor drivers and the combined read loop have been tested with live
  hardware.
- Mosquitto is configured and running on the Raspberry Pi.
- `esp32/publisher.py` connects the ESP32 to Wi-Fi and publishes a hardcoded
  JSON test payload to the broker. Verified end to end against
  `pi/mqtt/subscriber.py`, which
  receives the message, decodes it with `json.loads()`, and prints a value from
  it.
- Wi-Fi credentials live in a gitignored `hidden.py` that is never committed.
  Non-secret settings live in per-device config modules.

Not implemented yet:

- Publishing real sensor readings. `esp32/publisher.py` sends a hardcoded
  `{"distance": 42}` test payload, publishes once, and exits. It is a
  standalone script and is not imported or called by `esp32/main.py`, so no
  measurement from either sensor has crossed MQTT yet.
- Wi-Fi or MQTT reconnection handling
- The web dashboard
- Complete wiring documentation
- Automated tests

`pi/dashboard/app.py` and `docs/wiring.md` are still empty placeholders for that
future work.

## Architecture

Current data path:

```text
BME680 (0x76) ---------\
                       +-- shared I2C --> ESP32 --> serial output
STHS34PF80 (0x5A) ----/
```

Separately, and not yet joined to the path above:

```text
esp32/publisher.py --> Wi-Fi/MQTT --> Mosquitto on Raspberry Pi --> pi/mqtt/subscriber.py
```

Planned data path:

```text
Sensors --> ESP32 --> Wi-Fi/MQTT --> Mosquitto on Raspberry Pi --> web dashboard
```

`esp32/main.py` owns the application flow: it requests the I2C bus, creates both
sensor objects, and runs the only infinite read loop. The sensor modules provide
the device classes and register access; they do not start their own application
loops. Keeping coordination in one place lets both devices safely share the bus
and leaves one location for future MQTT publishing.

Joining the two paths is the next step: the Wi-Fi and MQTT setup in
`esp32/publisher.py` needs to become importable functions that `main.py` calls
once before its read loop, with the publish call moving inside the loop and
taking real readings.

## Hardware and Active Configuration

| Component | Current role | Planned role |
|---|---|---|
| Raspberry Pi 5 | Runs the Mosquitto MQTT broker | Hosts the web dashboard |
| ESP32 | Runs MicroPython, acts as the shared-I2C sensor gateway, and publishes a test payload over Wi-Fi and MQTT | Publishes real sensor readings |
| BME680 | Measures temperature, relative humidity, barometric pressure, and gas resistance | No change |
| STHS34PF80 | Reports ambient temperature, presence, motion, and temperature-shock signals | No change |

The active hardware configuration is defined in `esp32/main.py` and
`esp32/sensors/sths34pf80.py`:

| Setting | Value |
|---|---|
| I2C controller | `0` |
| SDA | GPIO `32` |
| SCL | GPIO `33` |
| I2C frequency | `100000` Hz |
| STHS34PF80 address | `0x5A` |
| BME680 address | `0x76` |
| STHS34PF80 data rate | 2 Hz |
| Main-loop delay | 1 second |
| BME680 temperature offset | `-5` degrees Celsius |
| Sea-level pressure used for altitude | `1013.25` hPa |

The `make_i2c()` helper has GPIO 21/22 defaults, but `main.py` deliberately
overrides them with the active GPIO 32/33 wiring. Update the call in `main.py`
if the physical wiring changes.

The MQTT settings are duplicated in two config modules, one next to each
consumer, because the ESP32 and the Raspberry Pi have separate filesystems:

| Setting | Value | Defined in |
|---|---|---|
| Broker address | `192.168.68.70` | both config modules |
| Broker port | `1883` | both config modules |
| BME680 topic | `roomsensor/bme680` | both config modules |
| STHS34PF80 topic | `roomsensor/sths34pf80` | both config modules |
| MQTT client ID | `freenove_esp32` | `esp32/config_esp32.py` only |

The client ID identifies a single connection to the broker and must be unique
per device; two clients sharing one ID will disconnect each other. It is
therefore deliberately absent from the Raspberry Pi config, where `paho-mqtt`
generates its own.

Wi-Fi credentials are not in either config module. They belong in a `hidden.py`
that is listed in `.gitignore` and never committed; see the setup steps below.

## Running the ESP32 Firmware

1. Flash a compatible MicroPython build onto the ESP32.
2. Copy `esp32/main.py` to `/main.py` on the board.
3. Copy `esp32/sensors/bme680.py` and `esp32/sensors/sths34pf80.py` into a
   `/sensors/` directory on the board, preserving the repository layout.
4. Connect both sensors to the configured SDA/SCL pins, power, and ground.
5. Reset the board and open its serial console to view the scan and readings.

The ESP32 firmware carries its sensor drivers in the repository and does not
need the CircuitPython sensor packages used by the historical Raspberry Pi
scripts.

### Running the MQTT test publisher

`esp32/publisher.py` is currently run by hand and is not part of the boot
sequence. To run it:

1. Copy `esp32/publisher.py` and `esp32/config_esp32.py` to the board root. The
   board's filesystem is flat, so these sit alongside `main.py` rather than in
   an `esp32/` directory, and the imports inside them are written accordingly.
2. Create a `hidden.py` at the board root defining two variables, `SSID` and
   `PASSWORD`, holding the Wi-Fi network name and password. This file is
   gitignored and is not in the repository, so it must be written by hand on
   each board. Editing the copy in the working tree does not update the board;
   re-save it to the device after any change.
3. Ensure `umqtt.simple` is available on the board. Check with
   `import umqtt.simple` at the REPL; if it raises `ImportError`, install
   `micropython-umqtt.simple` through Thonny's package manager.
4. Start `pi/mqtt/subscriber.py` on a machine with `paho-mqtt` installed and
   network access to the broker.
5. Run `publisher.py` on the board. It connects to Wi-Fi, prints the assigned
   IP, publishes one test message, and disconnects. The subscriber should print
   the topic and the received value.

## Firmware Output and Measurement Notes

On startup, the firmware prints the I2C scan. With both sensors connected, their
decimal addresses are `90` and `118`. It then prints:

- STHS34PF80 ambient temperature and raw presence, motion, and
  temperature-shock values with detected/not-detected labels
- BME680 temperature, gas resistance, relative humidity, pressure, and an
  altitude estimate

The two sensors use different read models:

- The STHS34PF80 runs at 2 Hz with block-data-update enabled. `main.py` checks
  `data_ready` before reading its output registers.
- The BME680 driver performs a forced measurement when a measurement property
  is read and waits for fresh sensor data internally. It does not expose a
  `data_ready` flag.

The BME680 reports gas resistance in ohms; the current firmware does not convert
that measurement into a calibrated VOC or indoor-air-quality score. Its
temperature correction and sea-level pressure are installation-specific
calibration values. Adjust both before relying on temperature or altitude in a
different environment.

The STHS34PF80 driver's `object_temperature` and
`compensated_object_temperature` properties expose signed raw radiometric
register counts from `TOBJECT` and `TOBJ_COMP`; they are not calibrated degrees
Celsius. Converting them to an absolute object temperature requires calibration
information that is not available in the public datasheet, so `main.py`
intentionally does not display them. `ambient_temperature`, which uses the
documented 100 LSB/degree Celsius sensitivity, is displayed.

## Project Structure

```text
smart-home-sensor/
|-- README.md
|-- LICENSE
|-- docs/
|   `-- wiring.md                 # Placeholder
|-- esp32/
|   |-- main.py                   # Active firmware entry point and read loop
|   |-- publisher.py              # Standalone Wi-Fi + MQTT test publisher
|   |-- config_esp32.py           # Broker address, port, topics, client ID
|   `-- sensors/
|       |-- bme680.py             # I2C-only MicroPython BME680 driver
|       `-- sths34pf80.py         # Register-level STHS34PF80 driver
|-- Pi-Only-Sensors/              # Archived Raspberry Pi sensor experiments
|   |-- read_bme680.py
|   `-- read_sths34pf80.py
`-- pi/
    |-- dashboard/
    |   `-- app.py                # Placeholder
    `-- mqtt/
        |-- config_mqtt.py        # Broker address, port, topics
        `-- subscriber.py         # MQTT subscriber, decodes JSON payloads
```

Not shown, because it is gitignored and never committed: `hidden.py`, holding
the `SSID` and `PASSWORD` variables. A copy is needed at the root of any board
that runs `publisher.py`.

## Project Evolution and Legacy Version

The first version connected both sensors directly to the Raspberry Pi using
CircuitPython libraries. That version is preserved in the `pi-only-v1` Git tag
and in `Pi-Only-Sensors/` while the ESP32 path is completed.

These archived scripts are not part of the active runtime:

- `Pi-Only-Sensors/read_bme680.py` initializes the BME680 but does not yet read
  or print measurements.
- `Pi-Only-Sensors/read_sths34pf80.py` contains the former Raspberry Pi polling
  loop and depends on `board` and `adafruit_sths34pf80`.

## Known Limitations

- The current main loop sleeps for one second between iterations, so it does not
  consume every sample produced by the STHS34PF80's 2 Hz configuration.
- The embedded-function page-switch timing in the STHS34PF80 driver references
  ST application note AN5867. That sequencing has worked in hardware testing,
  but it has not been independently verified against the application note and
  remains provisional.
- Validation currently depends on live hardware testing because the repository
  does not yet contain automated tests.
- `esp32/publisher.py` publishes a hardcoded payload once and exits. It shares
  no code with `esp32/main.py`, so the sensor loop and the MQTT link have never
  run together.
- Neither the Wi-Fi connection nor the MQTT connection is re-established if it
  drops. The Wi-Fi wait is an unbounded loop with no timeout, so a wrong
  password or an unreachable access point hangs the board with no diagnostic.
  This matters on a mesh network, where the access point can hand a client
  between nodes.
- The publisher and subscriber agree on JSON key names only by convention.
  Nothing enforces the contract, so a mismatch surfaces at runtime as a
  `KeyError` inside the subscriber's callback.
- The broker address and topic names are duplicated across
  `esp32/config_esp32.py` and `pi/mqtt/config_mqtt.py` and can drift apart. The
  two devices have separate filesystems, so a single shared module is not
  possible.
- Mosquitto is running without authentication or TLS. Any device on the local
  network can publish to or subscribe to any topic.

## Attribution and AI Assistance

### AI assistance

The register map, bit-field definitions, and embedded-function page-access
mechanism in `esp32/sensors/sths34pf80.py` were generated by Codex directly
from the STHS34PF80 datasheet, since no MicroPython port of this sensor
exists. I reviewed and verified this against the datasheet but did not write
it from scratch myself.

The core sequencing logic — `reset()`, `_algorithm_reset()`,
`_write_embedded_function()`, and `_safe_set_odr()` — I studied in detail and
can independently explain against Section 11 of the datasheet.

The STHS34PF80 polling loop in `esp32/main.py` was written by me, after
studying the example usage in Adafruit's CircuitPython STHS34PF80 repository
to learn the sensor's typical read pattern. The structure follows that
example fairly closely at the flow level, though the register-level
implementation is independent.

### Third-party driver

`esp32/sensors/bme680.py` is adapted from
[robert-hh's MicroPython port](https://github.com/robert-hh/BME680-Micropython)
of Adafruit's BME680 driver, originally by Limor "Ladyada" Fried. This project
uses only its I2C implementation, so the SPI class was removed. The upstream
MIT copyright and license notice remain in the driver.

## License

This project is licensed under the [MIT License](LICENSE).
