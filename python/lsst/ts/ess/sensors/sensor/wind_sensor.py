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

__all__ = [
    "WindSensor",
    "DEFAULT_DIRECTION_VAL",
    "DEFAULT_SPEED_VAL",
    "GOOD_STATUS",
    "END_CHARACTER",
    "START_CHARACTER",
    "UNIT_IDENTIFIER",
    "WINDSPEED_UNIT",
]

import asyncio
import logging
import math
import re
from typing import List, Optional, Union

from ..constants import DISCONNECTED_VALUE
from ..response_code import ResponseCode
from .base_sensor import BaseSensor

"""ASCII start character."""
START_CHARACTER: str = "\x02"

"""Unit Identifier."""
UNIT_IDENTIFIER: str = "Q"

"""Windspeed unit."""
WINDSPEED_UNIT: str = "M"

"""Default status."""
GOOD_STATUS: str = "00"

"""ASCII end charactor."""
END_CHARACTER = "\x03"

"""Default value for the wind direction."""
DEFAULT_DIRECTION_VAL: str = "999"

"""Default value for the wind speed."""
DEFAULT_SPEED_VAL: str = "9999.9990"


class WindSensor(BaseSensor):
    """Wind Sensor.

    Perform protocol conversion for Gill Windsonic Ultrasonic Anemometer
    instruments. The instrument is assumed to use its default message format -
    "Gill - Polar, Continuous" as documented in Gill Windsonic Doc No 1405 PS
    0019 Issue 28.
    Serial data is output by the anemometer once per second with the following
    format:

        '<STX>Q,ddd,sss.ss,M,00,<ETX>checksum<CR><LF>'

    where:

        <STX>       ASCII start character.
        'Q'         Unit Identifier ('Q' is default value).
        ddd         Wind direction. Three character, leading zero's integer.
                    000-359 degrees. Wind direction value is empty ('') when
                    wind speed is below 0.05 m/s.
        sss.ss      Wind speed. Six character, floating point, leading zero's.
                    0 to 60 m/s.
        'M'         Unit of speed measurement ('M' is m/s default)
        '00'        Status.
        <ETX>       ASCII end charactor.
        checksum    Exclusive OR of all bytes in the string between <STX> and
                    <ETX> characters.
        <CR><LF>    2-character terminator ('\r\n').

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

        # Regex pattern to process a line of telemetry.
        self.telemetry_pattern = re.compile(
            rf"^{START_CHARACTER}{UNIT_IDENTIFIER}{self.delimiter}(?P<direction>\d{{3}})?{self.delimiter}"
            rf"(?P<speed>\d{{3}}\.\d{{2}}){self.delimiter}{WINDSPEED_UNIT}{self.delimiter}"
            rf"(?P<status>\d{{2}}){self.delimiter}"
            rf"{END_CHARACTER}(?P<checksum>[0-9a-fA-F]{{2}}){self.terminator}$"
        )

    async def extract_telemetry(self, line: str) -> List[float]:
        """Extract the wind telemetry from a line of Sensor data."""
        m = re.search(self.telemetry_pattern, line)
        if m:
            direction_str = m.group("direction") if m.group("direction") else ""
            speed_str = m.group("speed")
            status = m.group("status")
            checksum_val = int(m.group("checksum"), 16)

            if status != GOOD_STATUS:
                self.log.error(
                    f"Expected status {GOOD_STATUS} but received {status}. Continuing."
                )

            checksum_string = f"Q,{direction_str},{speed_str},M,{status},"
            checksum: int = 0
            for i in checksum_string:
                checksum ^= ord(i)

            if checksum != checksum_val:
                self.log.error(
                    f"Computed checksum {checksum} is not equal to telemetry checksum {checksum_val}."
                )
                speed = math.nan
                direction = math.nan
            else:
                if speed_str == DEFAULT_SPEED_VAL:
                    speed = math.nan
                else:
                    speed = float(speed_str)
                if direction_str == DEFAULT_DIRECTION_VAL or direction_str == "":
                    direction = math.nan
                else:
                    direction = int(direction_str)
        elif line == f"{self.terminator}":
            speed = math.nan
            direction = math.nan
        else:
            raise ValueError(f"Received an unparsable line {line}")
        return [speed, direction]
