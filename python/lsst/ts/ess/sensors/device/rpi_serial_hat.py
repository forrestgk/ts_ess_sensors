# This file is part of ts_ess_sensors.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["RpiSerialHat"]

import asyncio
import logging
from typing import Callable, Tuple

import RPi.GPIO as gpio
import serial

from .base_device import BaseDevice
from ..response_code import ResponseCode
from ..sensor import BaseSensor


class RpiSerialHat(BaseDevice):
    """USB Virtual Communications Port (VCP) for FTDI device.

    Parameters
    ----------
    device_id: `str`
        The hardware device ID to connect to. This can be a physical ID (e.g.
        /dev/ttyUSB0), a serial port (e.g. serial_ch_1) or any other ID used by
        the specific device.
    sensor: `BaseSensor`
        The sensor that produces the telemetry.
    callback_func : `Callable`
        Callback function to receive instrument output.

    Notes
    -----
    This is a skeleton class that will be implemented further as soon as I get
    my hands on a raspberry pi with a serial hat.
    """

    # Define gpio channel numbers (Broadcomm mode)
    PIN_U4_ON: int = 17
    PIN_U4_DOUT: int = 18
    PIN_U4_DIRN: int = 3
    PIN_U5_ON: int = 23
    PIN_U5_DIN: int = 24
    PIN_U6_ON: int = 11
    PIN_U6_DIN: int = 7
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)

    # Define gpio pin state control
    STATE_TRX_ON: bool = True
    STATE_TRX_OFF: bool = False

    STATE_DIRN_TX: bool = True
    STATE_DIRN_RX: bool = False
    STATE_DOUT_HI: bool = True
    STATE_DOUT_LO: bool = False

    # Define serial transceiver module UART's and pins, then map to physical
    # connectors. serial device, module ON pin, module DIN pin, module DOUT
    # pin, module DIRN pin (RS-422).
    u4_ser1_config = "/dev/ttyS0", PIN_U4_ON, None, PIN_U4_DOUT, PIN_U4_DIRN
    u5_ser1_config = "/dev/ttyAMA1", PIN_U5_ON, PIN_U5_DIN, None, None
    u5_ser2_config = "/dev/ttyAMA2", PIN_U5_ON, PIN_U5_DIN, None, None
    u6_ser1_config = "/dev/ttyAMA0", PIN_U6_ON, PIN_U6_DIN, None, None
    u6_ser2_config = "/dev/ttyAMA3", PIN_U6_ON, PIN_U6_DIN, None, None

    serial_ports = {
        "serial_ch_0": u4_ser1_config,
        "serial_ch_1": u6_ser1_config,
        "serial_ch_2": u5_ser1_config,
        "serial_ch_3": u5_ser2_config,
        "serial_ch_4": u6_ser2_config,
    }

    def __init__(
        self,
        name: str,
        device_id: str,
        sensor: BaseSensor,
        callback_func: Callable,
        log: logging.Logger,
    ) -> None:
        super().__init__(
            name=name,
            device_id=device_id,
            sensor=sensor,
            callback_func=callback_func,
            log=log,
        )
        if self._device_id in RpiSerialHat.serial_ports:
            (
                self._ser_port,
                self._pin_on,
                self._pin_din,
                self._pin_dout,
                self._pin_dirn,
            ) = RpiSerialHat.serial_ports[self._device_id]
            try:
                self._ser = serial.Serial()
                self._ser.port = self._ser_port
                self.log.debug(f"Port: {self._ser.port}")
            except serial.SerialException as e:
                self.log.exception(e)
                # Unrecoverable error, so propagate error
                raise e
            else:
                # Setup GPIO
                if self._pin_on:
                    self._rpi_pin_setup(self._pin_on, gpio.OUT)
                if self._pin_dout:
                    self._rpi_pin_setup(self._pin_dout, gpio.OUT)  # type: ignore
                if self._pin_din:
                    self._rpi_pin_setup(self._pin_din, gpio.IN)  # type: ignore
                if self._pin_dirn:
                    self._rpi_pin_setup(self._pin_dirn, gpio.OUT)  # type: ignore

                # Turn on transceiver module and default other pin states
                if self._pin_on:
                    self._rpi_pin_state(self._pin_on, RpiSerialHat.STATE_TRX_ON)
                if self._pin_dout:
                    self._rpi_pin_state(self._pin_dout, RpiSerialHat.STATE_DOUT_LO)  # type: ignore
                if self._pin_dirn:
                    self._rpi_pin_state(self._pin_dirn, RpiSerialHat.STATE_DIRN_RX)  # type: ignore

                self.log.info(
                    f"RpiSerialHat:{name}: First instantiation using serial channel id: '{self._device_id}'."
                )
        else:
            self.log.error(
                f"RpiSerialHat:{name}: Error: A serial channel named '{self._device_id}' does not exist."
            )
            raise IndexError(
                f"RpiSerialHat:{name}: Error: A serial channel named '{self._device_id}' does not exist."
            )

    def _rpi_pin_setup(self, rpi_pin: int, pin_type: int) -> None:
        """Setup a GPIO pin.

        Parameters
        ----------
        rpi_pin: `int`
            The pin number.
        pin_type: `int`
            The pin type.
        """
        try:
            gpio.setup(rpi_pin, pin_type)
        except RuntimeError:
            self.log.exception("Error setting up GPIO pin.")

    def _rpi_pin_state(self, rpi_pin: int, state: bool) -> None:
        """Set a pin state.

        Parameters
        ----------
        rpi_pin: `int`
            The pin number.
        state: `bool`
            high = True, low = False.
        """
        try:
            gpio.output(rpi_pin, state)
        except RuntimeError:
            self.log.exception(
                "Error writing to GPIO output. GPIO channel has not been setup."
            )

    def _rpi_pin_cleanup(self, rpi_pin: int) -> None:
        """Cleanup a GPIO pin.

        Parameters
        ----------
        rpi_pin: `int`
            The pin number.
        """
        try:
            gpio.cleanup(rpi_pin)
        except RuntimeError:
            self.log.exception("GPIO pin cleanup error.")

    async def basic_open(self) -> None:
        """Open and configure serial port.
        Open the serial communications port and set BAUD.

        Raises
        ------
        IOError if serial communications port fails to open.
        """
        if not self._ser.is_open:
            try:
                self._ser.open()
                self._ser.baudrate = 19600
                self.log.info("Serial port opened.")
            except serial.SerialException as e:
                self.log.exception("Serial port open failed.")
                raise e
        else:
            self.log.info("Port already open!")

    async def readline(self) -> str:
        """Read a line of telemetry from the device.

        Returns
        -------
        line : `str`
            Line read from the device. Includes terminator string if there is
            one. May be returned empty if nothing was received or partial if
            the readline was started during device reception.
        """
        line: str = ""

        # get event loop to run blocking tasks
        loop = asyncio.get_event_loop()

        if self._pin_dirn:
            self._rpi_pin_state(self._pin_dirn, RpiSerialHat.STATE_DIRN_RX)  # type: ignore
        while not line.endswith(self._sensor.terminator):
            ch = await loop.run_in_executor(None, self._ser.read, 1)
            line += ch.decode(self._sensor.charset)
        return line

    async def basic_close(self) -> None:
        """Close the Sensor Device.

        Raises
        ------
        IOError if virtual communications port fails to close.
        """
        if self._ser.is_open:
            self._ser.close()
            self.log.exception("Serial port closed.")
        else:
            self.log.info("Serial port already closed.")
