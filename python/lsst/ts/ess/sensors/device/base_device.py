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

__all__ = ["BaseDevice"]

from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Any, Callable, List, Optional, Tuple, Union

from ..constants import Key
from ..response_code import ResponseCode
from ..sensor import BaseSensor
from ..utils import create_done_future
from lsst.ts import salobj


class BaseDevice(ABC):
    """Base class for the different types of Sensor Devices.

    This class holds all common code for the hardware devices. Device specific
    code (for instance for a serial or an FTDI device) needs to be implemented
    in a sub-class.

    Parameters
    ----------
    name: `str`
        The name of the device.
    device_id: `str`
        The hardware device ID to connect to. This can be a physical ID (e.g.
        /dev/ttyUSB0), a serial port (e.g. serial_ch_1) or any other ID used by
        the specific device.
    sensor: `BaseSensor`
        The sensor that produces the telemetry.
    callback_func : `Callable`
        Callback function to receive the telemetry.
    log: `logging.Logger`
        The logger to create a child logger for.
    """

    @abstractmethod
    def __init__(
        self,
        name: str,
        device_id: str,
        sensor: BaseSensor,
        callback_func: Callable,
        log: logging.Logger,
    ) -> None:
        self.name: str = name
        self._device_id: str = device_id
        self._sensor: BaseSensor = sensor
        self._callback_func: Callable = callback_func
        self._telemetry_loop: asyncio.Future = create_done_future()
        self.is_open = False
        self.log = log.getChild(type(self).__name__)

        # Support MockDevice fault state. To be used in unit tests only.
        self._in_error_state: bool = False

    async def open(self) -> None:
        """Generic open function.

        Check if the device is open and, if not, call basic_open. Then start
        the telemetry loop.

        Raises
        ------
        RuntimeError
            In case the device already is open.
        """
        if self.is_open:
            self.log.error("Already open, ignoring.")
        await self.basic_open()
        self.is_open = True

        self.log.debug(f"Starting read loop for {self.name!r} sensor.")
        self._telemetry_loop = asyncio.create_task(self._run())

    @abstractmethod
    async def basic_open(self) -> None:
        """Open the Sensor Device."""
        pass

    async def _run(self) -> None:
        """Run sensor read loop.

        If enabled, loop and read the sensor and pass result to callback_func.
        """
        self.log.debug("Starting sensor.")
        while not self._telemetry_loop.done():
            self.log.debug("Reading data.")
            curr_tai: float = salobj.current_tai()
            response: int = ResponseCode.OK
            try:
                line: str = await self.readline()
            except Exception:
                self.log.exception(f"Exception reading device {self.name}. Continuing.")
                line = f"{self._sensor.terminator}"
                response = ResponseCode.DEVICE_READ_ERROR

            if self._in_error_state:
                response = ResponseCode.DEVICE_READ_ERROR

            sensor_telemetry: List[float] = await self._sensor.extract_telemetry(
                line=line
            )
            output: List[Union[str, float, int]] = [
                self.name,
                curr_tai,
                response,
                *sensor_telemetry,
            ]
            reply = {
                Key.TELEMETRY: output,
            }
            self.log.info(f"Returning {reply}")
            await self._callback_func(reply)

    @abstractmethod
    async def readline(self) -> str:
        """Read a line of telemetry from the device.

        Returns
        -------
        line : `str`
            Line read from the device. Includes terminator string if there is
            one. May be returned empty if nothing was received or partial if
            the readline was started during device reception.
        """
        pass

    async def close(self) -> None:
        """Generic close function.

        Stop the telemetry loop. Then check if the device is open and, if yes,
        call basic_close.
        """
        self.log.debug(f"Stopping read loop for {self.name!r} sensor.")
        self._telemetry_loop.cancel()
        self._telemetry_loop = create_done_future()

        if not self.is_open:
            return
        self.is_open = False
        await self.basic_close()

    @abstractmethod
    async def basic_close(self) -> None:
        """Close the Sensor Device."""
        pass
