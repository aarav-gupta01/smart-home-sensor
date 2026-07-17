import time

from machine import I2C, Pin # type: ignore

try:
    from micropython import const # type: ignore
except ImportError:
    const = lambda value: value


# ESP32-WROOM-32 default I2C pins. Confirm these against the physical wiring.
DEFAULT_I2C_ID = const(0)
DEFAULT_SDA_PIN = const(21)
DEFAULT_SCL_PIN = const(22)
DEFAULT_I2C_FREQ = const(100000)


# Register addresses
_LPF1 = const(0x0C)
_LPF2 = const(0x0D)
_WHO_AM_I = const(0x0F)
_AVG_TRIM = const(0x10)
_CTRL1 = const(0x20)
_CTRL2 = const(0x21)
_STATUS = const(0x23)
_FUNC_STATUS = const(0x25)
_TOBJECT_L = const(0x26)
_TAMBIENT_L = const(0x28)
_TOBJ_COMP_L = const(0x38)
_TPRESENCE_L = const(0x3A)
_TMOTION_L = const(0x3C)
_TAMB_SHOCK_L = const(0x3E)

# Embedded function registers
_FUNC_CFG_ADDR = const(0x08)
_FUNC_CFG_DATA = const(0x09)
_PAGE_RW = const(0x11)

# Embedded function addresses
_EMBEDDED_RESET_ALGO = const(0x2A)

# Device ID
_DEVICE_ID = const(0xD3)

# Low-pass filter configuration options
LPF_ODR_DIV_9 = const(0x00)
LPF_ODR_DIV_20 = const(0x01)
LPF_ODR_DIV_50 = const(0x02)
LPF_ODR_DIV_100 = const(0x03)
LPF_ODR_DIV_200 = const(0x04)
LPF_ODR_DIV_400 = const(0x05)
LPF_ODR_DIV_800 = const(0x06)

# Ambient temperature averaging options
AVG_T_8 = const(0x00)
AVG_T_4 = const(0x01)
AVG_T_2 = const(0x02)
AVG_T_1 = const(0x03)

# Object temperature averaging options
AVG_TMOS_2 = const(0x00)
AVG_TMOS_8 = const(0x01)
AVG_TMOS_32 = const(0x02)
AVG_TMOS_128 = const(0x03)
AVG_TMOS_256 = const(0x04)
AVG_TMOS_512 = const(0x05)
AVG_TMOS_1024 = const(0x06)
AVG_TMOS_2048 = const(0x07)

# Output data rate options
ODR_POWER_DOWN = const(0x00)
ODR_0_25_HZ = const(0x01)
ODR_0_5_HZ = const(0x02)
ODR_1_HZ = const(0x03)
ODR_2_HZ = const(0x04)
ODR_4_HZ = const(0x05)
ODR_8_HZ = const(0x06)
ODR_15_HZ = const(0x07)
ODR_30_HZ = const(0x08)


class STHS34PF80:
    def __init__(self, i2c, address=0x5a):
        self.i2c = i2c
        self.address = address

        device_id = self._read_u8(_WHO_AM_I)
        if device_id != _DEVICE_ID:
            raise RuntimeError(
                "Failed to find STHS34PF80 at 0x%02X; chip ID 0x%02X"
                % (address, device_id)
            )

        self.reset()

        # Same startup configuration as the CircuitPython Pi-side version.
        self.object_averaging = AVG_TMOS_32
        self.ambient_averaging = AVG_T_8
        self.motion_lpf = LPF_ODR_DIV_20
        self.presence_lpf = LPF_ODR_DIV_50
        self.temperature_lpf = LPF_ODR_DIV_100
        self.data_rate = ODR_2_HZ
        self.block_data_update = True

    def _read(self, register, length=1):
        return self.i2c.readfrom_mem(self.address, register, length)

    def _write_u8(self, register, value):
        self.i2c.writeto_mem(self.address, register, bytes([value & 0xFF]))

    def _read_u8(self, register):
        return self._read(register, 1)[0]

    def _read_i16(self, register):
        data = self._read(register, 2)
        value = data[0] | (data[1] << 8)
        if value & 0x8000:
            value -= 0x10000
        return value

    def _read_bits(self, register, offset, width):
        mask = ((1 << width) - 1) << offset
        return (self._read_u8(register) & mask) >> offset

    def _write_bits(self, register, offset, width, value):
        mask = ((1 << width) - 1) << offset
        current = self._read_u8(register)
        current &= ~mask
        current |= (value << offset) & mask
        self._write_u8(register, current)

    def _read_bit(self, register, bit):
        return bool(self._read_u8(register) & (1 << bit))

    def _write_bit(self, register, bit, value):
        current = self._read_u8(register)
        if value:
            current |= 1 << bit
        else:
            current &= ~(1 << bit)
        self._write_u8(register, current)

    def reset(self):
        self._write_bit(_CTRL2, 7, True)
        time.sleep_ms(5)
        self._algorithm_reset()

    def _algorithm_reset(self):
        self._write_embedded_function(_EMBEDDED_RESET_ALGO, bytes([0x01]))

    def _write_embedded_function(self, addr, data):
        current_odr = self._odr
        self._safe_set_odr(current_odr, ODR_POWER_DOWN)

        self._write_bit(_CTRL2, 4, True)

        page_rw = self._read_u8(_PAGE_RW)
        self._write_u8(_PAGE_RW, page_rw | 0x40)
        self._write_u8(_FUNC_CFG_ADDR, addr)
        for byte in data:
            self._write_u8(_FUNC_CFG_DATA, byte)
        self._write_u8(_PAGE_RW, page_rw & ~0x40)

        self._write_bit(_CTRL2, 4, False)
        self._safe_set_odr(ODR_POWER_DOWN, current_odr)

    def _safe_set_odr(self, current_odr, new_odr):
        if new_odr > ODR_POWER_DOWN:
            self._odr = ODR_POWER_DOWN
            self._algorithm_reset()
        elif current_odr > ODR_POWER_DOWN:
            self._read_u8(_FUNC_STATUS)

            start = time.ticks_ms()
            while not self.data_ready:
                if time.ticks_diff(time.ticks_ms(), start) > 1000:
                    break
                time.sleep_ms(1)

            self._odr = ODR_POWER_DOWN
            self._read_u8(_FUNC_STATUS)

        self._odr = new_odr

    @property
    def data_ready(self):
        return self._read_bit(_STATUS, 2)

    @property
    def temperature_shock(self):
        return self._read_bit(_FUNC_STATUS, 0)

    @property
    def motion(self):
        return self._read_bit(_FUNC_STATUS, 1)

    @property
    def presence(self):
        return self._read_bit(_FUNC_STATUS, 2)

    @property
    def object_temperature(self):
        return self._read_i16(_TOBJECT_L)

    @property
    def ambient_temperature(self):
        return self._read_i16(_TAMBIENT_L) / 100.0

    @property
    def compensated_object_temperature(self):
        return self._read_i16(_TOBJ_COMP_L)

    @property
    def presence_value(self):
        return self._read_i16(_TPRESENCE_L)

    @property
    def motion_value(self):
        return self._read_i16(_TMOTION_L)

    @property
    def temperature_shock_value(self):
        return self._read_i16(_TAMB_SHOCK_L)

    @property
    def block_data_update(self):
        return self._read_bit(_CTRL1, 4)

    @block_data_update.setter
    def block_data_update(self, value):
        self._write_bit(_CTRL1, 4, value)

    @property
    def _odr(self):
        return self._read_bits(_CTRL1, 0, 4)

    @_odr.setter
    def _odr(self, value):
        self._write_bits(_CTRL1, 0, 4, value)

    @property
    def data_rate(self):
        return self._odr

    @data_rate.setter
    def data_rate(self, value):
        if value < ODR_POWER_DOWN or value > ODR_30_HZ:
            raise ValueError("Invalid output data rate")
        current_odr = self._odr
        self._safe_set_odr(current_odr, value)

    @property
    def motion_lpf(self):
        return self._read_bits(_LPF1, 0, 3)

    @motion_lpf.setter
    def motion_lpf(self, value):
        self._write_bits(_LPF1, 0, 3, value)

    @property
    def presence_lpf(self):
        return self._read_bits(_LPF2, 3, 3)

    @presence_lpf.setter
    def presence_lpf(self, value):
        self._write_bits(_LPF2, 3, 3, value)

    @property
    def temperature_lpf(self):
        return self._read_bits(_LPF2, 0, 3)

    @temperature_lpf.setter
    def temperature_lpf(self, value):
        self._write_bits(_LPF2, 0, 3, value)

    @property
    def ambient_averaging(self):
        return self._read_bits(_AVG_TRIM, 4, 2)

    @ambient_averaging.setter
    def ambient_averaging(self, value):
        self._write_bits(_AVG_TRIM, 4, 2, value)

    @property
    def object_averaging(self):
        return self._read_bits(_AVG_TRIM, 0, 3)

    @object_averaging.setter
    def object_averaging(self, value):
        self._write_bits(_AVG_TRIM, 0, 3, value)


def make_i2c(i2c_id=DEFAULT_I2C_ID, sda=DEFAULT_SDA_PIN, scl=DEFAULT_SCL_PIN):
    return I2C(i2c_id, sda=Pin(sda), scl=Pin(scl), freq=DEFAULT_I2C_FREQ)


def main():
    i2c = make_i2c()
    sths34pf80 = STHS34PF80(i2c)

    while True:
        if sths34pf80.data_ready:
            ambient_temp = sths34pf80.ambient_temperature
            object_temp = sths34pf80.object_temperature
            comp_object_temp = sths34pf80.compensated_object_temperature

            presence_value = sths34pf80.presence_value
            motion_value = sths34pf80.motion_value
            temp_shock_value = sths34pf80.temperature_shock_value

            presence = sths34pf80.presence
            motion = sths34pf80.motion
            temp_shock = sths34pf80.temperature_shock

            print("Ambient Temperature: %.2f C" % ambient_temp)
            print("Object Temperature: %s" % object_temp)
            print("Compensated Object Temperature: %s" % comp_object_temp)
            print(
                "Presence Value: %s %s"
                % (presence_value, "[DETECTED]" if presence else "[NOT DETECTED]")
            )
            print(
                "Motion Value: %s %s"
                % (motion_value, "[DETECTED]" if motion else "[NOT DETECTED]")
            )
            print(
                "Temperature Shock Value: %s %s"
                % (temp_shock_value, "[DETECTED]" if temp_shock else "[NOT DETECTED]")
            )
        time.sleep(1)


if __name__ == "__main__":
    main()
