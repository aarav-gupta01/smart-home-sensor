# Smart Home Sensor Network

A work-in-progress smart-home sensing system built around an ESP32 and a
Raspberry Pi 5. The ESP32 reads a BME680 environmental sensor and an
STHS34PF80 infrared presence sensor over one shared I2C bus and publishes
their readings as JSON over Wi-Fi and MQTT to a Mosquitto broker on the
Raspberry Pi.

The full sensor-to-broker path is working and hardware-verified. The longer-term
goal is to persist those readings and display them in a web dashboard; neither
is implemented yet.

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
- `esp32/publisher.py` provides importable Wi-Fi and MQTT helpers:
  `connect_network()`, `connect_client()`, and `publish_data(client, topic,
  data)`. It has no top-level side effects, so `main.py` can import it safely.
- `esp32/main.py` brings up Wi-Fi and the MQTT client once before the read
  loop, then publishes one JSON object per sensor per reading, each to its own
  topic. Verified end to end on live hardware: both topics arrive at the
  subscriber with complete payloads.
- `pi/mqtt/subscriber.py` subscribes to `roomsensor/#`, so one script receives
  both sensors, and prints every key in each decoded payload.
- Wi-Fi credentials live in a gitignored `hidden.py` that is never committed.
  Non-secret settings live in per-device config modules.

Not implemented yet:

- Wi-Fi or MQTT reconnection handling
- Persisting readings to a database
- The web dashboard
- Complete wiring documentation
- Automated tests

`pi/dashboard/app.py` and `docs/wiring.md` are still empty placeholders for that
future work.

## Architecture

Current data path:

```text
BME680 (0x76) ---------\
                       +-- shared I2C --> ESP32 --> Wi-Fi/MQTT --> Mosquitto --> pi/mqtt/subscriber.py
STHS34PF80 (0x5A) ----/
```

Planned data path:

```text
Sensors --> ESP32 --> Wi-Fi/MQTT --> Mosquitto --> database --> web dashboard
```

`esp32/main.py` owns the application flow: it requests the I2C bus, creates both
sensor objects, brings up Wi-Fi and MQTT, and runs the only infinite read loop.
The sensor modules provide the device classes and register access; they do not
start their own application loops. `esp32/publisher.py` provides connection and
publish helpers but never runs anything on import. Keeping coordination in one
place lets both devices safely share the bus and gives the MQTT link a single
owner.

Each sensor's payload is built and published inside the block that read it,
rather than assembled together at the end of the loop. This matters because the
two sensors have different read models: a skipped STHS34PF80 read must produce
no message at all, not a message rebuilt from the previous iteration's
still-bound variables. Keeping the publish next to its own read makes stale
republishing structurally impossible.

## Hardware and Active Configuration

| Component | Current role | Planned role |
|---|---|---|
| Raspberry Pi 5 | Runs the Mosquitto MQTT broker | Hosts the web dashboard |
| ESP32 | Runs MicroPython, acts as the shared-I2C sensor gateway, and publishes real sensor readings over Wi-Fi and MQTT | Reconnects automatically after a Wi-Fi or broker drop |
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

## Message Payloads

Each reading produces one JSON object containing all of that sensor's fields,
published to that sensor's own topic. One message maps to one row, so the shape
carries over directly when database persistence is added.

`roomsensor/bme680`, published every loop iteration:

| Key | Type | Notes |
|---|---|---|
| `temperature` | float | Degrees Celsius, includes the `-5` offset |
| `gas` | int | Gas resistance in ohms, uncalibrated |
| `humidity` | float | Relative humidity, percent |
| `pressure` | float | hPa |
| `altitude` | float | Meters, derived from `sea_level_pressure` |

`roomsensor/sths34pf80`, published only when `data_ready` is set:

| Key | Type | Notes |
|---|---|---|
| `ambient_temp` | float | Degrees Celsius |
| `presence` | bool | Detection flag |
| `presence_value` | int | Raw presence register value |
| `motion` | bool | Detection flag |
| `motion_value` | int | Raw motion register value |
| `temp_shock` | bool | Detection flag |
| `temp_shock_value` | int | Raw temperature-shock register value |

Both the boolean flag and the raw value are sent for each STHS34PF80 signal.
The flag is easier to read directly; the raw value cannot be recovered from the
flag afterwards, so both are recorded.

The two topics publish at different rates. The BME680 message goes out on every
iteration; the STHS34PF80 message only when the sensor reports new data.

## Running the ESP32 Firmware

Publishing is part of the boot sequence, so `publisher.py`, `config_esp32.py`,
and `hidden.py` are all required for `main.py` to run.

1. Flash a compatible MicroPython build onto the ESP32.
2. Copy `esp32/main.py` to `/main.py` on the board.
3. Copy `esp32/publisher.py` and `esp32/config_esp32.py` to the board root. The
   board's filesystem is flat, so these sit alongside `main.py` rather than in
   an `esp32/` directory, and the imports inside them are written accordingly.
4. Copy `esp32/sensors/bme680.py` and `esp32/sensors/sths34pf80.py` into a
   `/sensors/` directory on the board, preserving the repository layout.
5. Create a `hidden.py` at the board root defining two variables, `SSID` and
   `PASSWORD`, holding the Wi-Fi network name and password. This file is
   gitignored and is not in the repository, so it must be written by hand on
   each board. Editing the copy in the working tree does not update the board;
   re-save it to the device after any change.
6. Ensure `umqtt.simple` is available on the board. Check with
   `import umqtt.simple` at the REPL; if it raises `ImportError`, install
   `micropython-umqtt.simple` through Thonny's package manager.
7. Connect both sensors to the configured SDA/SCL pins, power, and ground.
8. Reset the board. It prints the I2C scan, then `Connecting...`, then the
   assigned IP, and begins publishing.

The ESP32 firmware carries its sensor drivers in the repository and does not
need the CircuitPython sensor packages used by the historical Raspberry Pi
scripts.

### Running the subscriber

Run `pi/mqtt/subscriber.py` on any machine with `paho-mqtt` installed and
network access to the broker. It subscribes to `roomsensor/#`, so it receives
both sensors through a single subscription, and prints the topic followed by
every key and value in the decoded payload.

`mosquitto_sub -h 192.168.68.70 -t 'roomsensor/#' -v` is a useful independent
check when diagnosing whether a problem is on the publishing or the receiving
side.

### Troubleshooting the Wi-Fi connection

The Wi-Fi wait in `connect_network()` is an unbounded loop that only tests
`isconnected()`, so a failure to associate presents as an indefinite hang after
`Connecting...` with no diagnostic. To find the cause, interrupt with Ctrl+C
(not Ctrl+D, which soft-reboots and clears globals) and query the interface at
the REPL:

```python
import network
w = network.WLAN(network.STA_IF)
print(w.active(), w.isconnected(), w.status())
```

A `status()` of `1001` is `STAT_CONNECTING`: the radio is parked mid-association
and a soft reset will not clear it. Power-cycle the board. `201` means the
access point was not found, `202` a wrong password; check the board's own copy
of `hidden.py`, which can drift from the one in the working tree.

One environment-specific cause of a persistent `1001`: on a Mac, adjacent USB-C
ports commonly share a power budget, and a Thunderbolt device on one port can
starve its neighbor. The Wi-Fi radio draws the highest current in the system,
so it fails while lower-current paths — I2C sensor reads and the serial console
— keep working normally, which disguises a power problem as a network problem.
Powering the board from a dedicated USB wall adapter avoids this entirely and
is the right arrangement for unattended operation.

## Firmware Output and Measurement Notes

On startup, the firmware prints the I2C scan. With both sensors connected, their
decimal addresses are `90` and `118`. It then prints `Connecting...` and the
`ifconfig()` tuple once Wi-Fi associates.

The per-reading print statements from the testing phase are retained in
`main.py` but commented out, so the serial console stays quiet during normal
operation and readings are observed at the subscriber instead. Uncomment them
when debugging sensor values directly on the board.

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
|   |-- main.py                   # Active firmware entry point, read and publish loop
|   |-- publisher.py              # Wi-Fi + MQTT helpers imported by main.py
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
        `-- subscriber.py         # Wildcard MQTT subscriber, decodes JSON payloads
```

Not shown, because it is gitignored and never committed: `hidden.py`, holding
the `SSID` and `PASSWORD` variables. A copy is needed at the root of any board
that runs `main.py`.

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

- The main loop sleeps for one second between iterations, and each BME680 field
  access triggers its own forced measurement with an enforced minimum interval,
  so a full iteration takes noticeably longer than one second. The loop does not
  consume every sample produced by the STHS34PF80's 2 Hz configuration.
- The five BME680 fields in a single message come from five separate
  measurements taken a few hundred milliseconds apart, not one atomic sample.
  This is acceptable for room climate but means a message is not a single
  instant in time.
- The embedded-function page-switch timing in the STHS34PF80 driver references
  ST application note AN5867. That sequencing has worked in hardware testing,
  but it has not been independently verified against the application note and
  remains provisional.
- Validation currently depends on live hardware testing because the repository
  does not yet contain automated tests.
- Neither the Wi-Fi connection nor the MQTT connection is re-established if it
  drops. `client.publish()` raises `OSError` on a dead socket, and nothing in
  the read loop catches it, so a single broker restart or access-point handover
  ends the loop and the board goes silent until it is power-cycled. This matters
  on a mesh network, where the access point can hand a client between nodes.
- The Wi-Fi wait is an unbounded loop with no timeout that only tests
  `isconnected()`, so a wrong password or an unreachable access point hangs the
  board with no diagnostic output. See the troubleshooting steps above.
- The MQTT client ID is a fixed string. A broker closes an existing session when
  a second connection claims the same ID, so a reconnect implementation must
  account for the old session being displaced, and two publishers cannot run
  concurrently.
- The publisher and subscriber agree on JSON key names only by convention.
  Nothing enforces the contract. The subscriber iterates whatever keys arrive,
  so a mismatch is not currently fatal, but it will matter once readings are
  written to fixed database columns.
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
