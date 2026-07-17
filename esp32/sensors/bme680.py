# BME680 (I2C address 0x76) - MicroPython driver
# Written by hand, ported from register-level understanding developed
# on the Pi CircuitPython version. Not yet implemented.
import time

from machine import I2C, Pin

try:
    from micropython import const
except ImportError:
    const = lambda value: value