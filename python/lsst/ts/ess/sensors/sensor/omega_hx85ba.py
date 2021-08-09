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

__all__ = ["Hx85baSensor"]

import asyncio
import logging
import math
from typing import List, Optional, Union

from ..constants import DISCONNECTED_VALUE
from ..response_code import ResponseCode
from .base_sensor import BaseSensor

"""The number of output values for this sensor is 3."""
NUM_VALUES = 3


class Hx85baSensor(BaseSensor):
    """Omega HX85BA Humidity Sensor.

    Perform protocol conversion for Omega HX85BA Humidity instruments. Serial
    data is output by the instrument once per second with the following
    format:

        '%RH=38.86,AT°C=24.32,Pmb=911.40<\n><\r>'

    where:

        %RH=        Relative Humidity prefix.
        dd.dd       Relative Humidity value (Range 5% to 95%).
        AT°C=       Air Temperature prefix.
        -ddd.dd     Air Temperature value (Range -20C to +120C).
        Pmb=        Barometric Pressure prefix.
        ddd.dd      Barometric Pressure value (10mbar to 1100mbar).
        <LF><CR>    2-character terminator ('\n\r').

    The placeholders shown for the values are displaying the maximum width for
    those values. The values are not prepended with zeros and only show a sign
    in case of a negative value.

    Parameters
    ----------
    log: `logger`
        The logger for which to create a child logger.
    """

    def __init__(
        self,
        log: logging.Logger,
    ) -> None:
        super().__init__(log=log)

        # Override default value.
        self.terminator = "\n\r"
        # Override default value.
        self.charset = "ISO-8859-1"

    async def extract_telemetry(self, line: str) -> List[float]:
        """Extract the telemetry from a line of Sensor data.

        Parameters
        ----------
        line: `str`
            A line of comma separated telemetry.

        Returns
        -------
        output: `list`
            A list containing the telemetry as measured by the sensor.
        """
        self.log.debug("extract_telemetry")
        stripped_line: str = line.strip(self.terminator)
        line_items = stripped_line.split(self.delimiter)
        output = []
        for line_item in line_items:
            telemetry_items = line_item.split("=")
            if len(telemetry_items) == 1:
                output.append(math.nan)
            elif len(telemetry_items) == 2:
                output.append(float(telemetry_items[1]))
            else:
                raise ValueError(
                    f"At most one '=' symbol expected in telemetry item {line_item}"
                )

        # When the connection is first made, it may be done while the sensor is
        # in the middle of outputting data. In that case, only a partial string
        # with the final channels will be received and the missing leading
        # channels need to be filled with NaN.
        while len(output) < NUM_VALUES:
            output.insert(0, math.nan)
        return output
