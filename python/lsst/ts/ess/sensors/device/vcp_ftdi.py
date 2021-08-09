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

__all__ = ["VcpFtdi"]

import asyncio
import logging
from typing import Callable, Tuple

from pylibftdi import Device, FtdiError

from .base_device import BaseDevice
from ..response_code import ResponseCode
from ..sensor import BaseSensor


class VcpFtdi(BaseDevice):
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
    """

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
        self._vcp: Device = Device(
            self._device_id,
            mode="t",
            encoding="ASCII",
            lazy_open=True,
            auto_detach=False,
        )

    async def basic_open(self) -> None:
        """Open the Sensor Device.

        Opens the virtual communications port and flushes the device input and
        output buffers.

        Raises
        ------
        IOError if virtual communications port fails to open.
        """
        self._vcp.open()
        self._vcp.baudrate = 19600
        if not self._vcp.closed:
            self.log.debug("FTDI device open.")
            self._vcp.flush()
        else:
            self.log.error("Failed to open the FTDI device.")
            raise IOError(f"{self.name}: Failed to open the FTDI device.")

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

        while not line.endswith(self._sensor.terminator):
            line += await loop.run_in_executor(None, self._vcp.read, 1)
        return line

    async def basic_close(self) -> None:
        """Close the Sensor Device.

        Raises
        ------
        IOError if virtual communications port fails to close.
        """
        self._vcp.close()
        if self._vcp.closed:
            self.log.debug("FTDI device closed.")
        else:
            self.log.debug("FTDI device failed to close.")
            raise IOError(f"VcpFtdi:{self.name}: Failed to close the FTDI device.")
