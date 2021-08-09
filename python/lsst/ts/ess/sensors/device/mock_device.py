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

__all__ = ["MockDevice"]

import asyncio
import logging
import random
from typing import Callable, Tuple

from .base_device import BaseDevice
from ..constants import (
    DISCONNECTED_VALUE,
    MockDewPointConfig,
    MockHumidityConfig,
    MockPressureConfig,
    MockTemperatureConfig,
)
from ..response_code import ResponseCode
from ..sensor import BaseSensor, Hx85aSensor, Hx85baSensor, TemperatureSensor


class MockDevice(BaseDevice):
    """Mock Sensor Device.

    Parameters
    ----------
    name: `str`
        The name of the device.
    device_id: `str`
        The hardware device ID to connect to.
    sensor: `BaseSensor`
        The sensor that produces the telemetry.
    callback_func : `Callable`
        Callback function to receive the telemetry.
    log: `logging.Logger`
        The logger to create a child logger for.
    disconnected_channel: `int`, optional
        The channel number for which this class will mock a disconnection.
    missed_channels: `int`, optional
        The number of channels to not output to mock connecting to the sensor
        in the middle of receiving data from it.
    in_error_state: `bool`, optional
        The sensor produces an error (True) or not (False) when being read.
    """

    def __init__(
        self,
        name: str,
        device_id: str,
        sensor: BaseSensor,
        callback_func: Callable,
        log: logging.Logger,
        disconnected_channel: int = None,
        missed_channels: int = 0,
        in_error_state: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            device_id=device_id,
            sensor=sensor,
            callback_func=callback_func,
            log=log,
        )
        self._disconnected_channel = disconnected_channel
        self._missed_channels = missed_channels
        self._in_error_state = in_error_state

    async def basic_open(self) -> None:
        """Open the Sensor Device."""
        pass

    def _format_temperature(self, i: int):
        """Creates a formatted string representing a temperature for the given
        channel.

        Parameters
        ----------
        i: `int`
            The 0-based temperature channel.
        Returns
        -------
        s: `str`
            A string representing a temperature.
        """
        if i < self._missed_channels:
            return ""

        prefix = f"C{i:02d}="
        value = random.uniform(MockTemperatureConfig.min, MockTemperatureConfig.max)
        if i == self._disconnected_channel:
            value = float(DISCONNECTED_VALUE)
        return f"{prefix}{value:09.4f}"

    def _format_hbx85_humidity(self, index: int):
        if index < self._missed_channels:
            return ""
        else:
            prefix = "%RH="
            value = random.uniform(MockHumidityConfig.min, MockHumidityConfig.max)
            return f"{prefix}{value:5.2f}"

    def _format_hbx85_temperature(self, index: int):
        if index < self._missed_channels:
            return ""
        else:
            prefix = "AT°C="
            value = random.uniform(MockTemperatureConfig.min, MockTemperatureConfig.max)
            return f"{prefix}{value:6.2f}"

    def _format_hbx85_dew_point(self, index: int):
        if index < self._missed_channels:
            return ""
        else:
            prefix = "DP°C="
            value = random.uniform(MockDewPointConfig.min, MockDewPointConfig.max)
            return f"{prefix}{value:5.2f}"

    def _format_hbx85_air_pressure(self, index: int):
        if index < self._missed_channels:
            return ""
        else:
            prefix = "Pmb="
            value = random.uniform(MockPressureConfig.min, MockPressureConfig.max)
            return f"{prefix}{value:7.2f}"

    async def readline(self) -> str:
        """Read a line of telemetry from the device.

        Returns
        -------
        line : `str`
            Line read from the device. Includes terminator string if there is
            one. May be returned empty if nothing was received or partial if
            the readline was started during device reception.
        """
        # Mock the time needed to output telemetry.
        await asyncio.sleep(1)

        # Mock a sensor that produces an error when being read.
        if self._in_error_state:
            return f"{self._sensor.terminator}"

        channel_strs = []
        if isinstance(self._sensor, TemperatureSensor):
            channel_strs = [
                self._format_temperature(i) for i in range(0, self._sensor.num_channels)
            ]
        elif isinstance(self._sensor, Hx85aSensor):
            channel_strs = [
                self._format_hbx85_humidity(index=0),
                self._format_hbx85_temperature(index=1),
                self._format_hbx85_dew_point(index=2),
            ]
        elif isinstance(self._sensor, Hx85baSensor):
            channel_strs = [
                self._format_hbx85_humidity(index=0),
                self._format_hbx85_temperature(index=1),
                self._format_hbx85_air_pressure(index=2),
            ]

        self.log.debug(f"channel_strs = {channel_strs}")

        # Reset self._missed_channels because truncated data only happens when
        # data is being output while connecting.
        self._missed_channels = 0
        return self._sensor.delimiter.join(channel_strs) + self._sensor.terminator

    async def basic_close(self) -> None:
        """Close the Sensor Device."""
        pass
