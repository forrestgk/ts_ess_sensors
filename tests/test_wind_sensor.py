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

import asyncio
import logging
import math
import unittest

from lsst.ts.ess import sensors

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)


class WindSensorTestCase(unittest.IsolatedAsyncioTestCase):
    def create_wind_sensor_line(
        self, speed: str, direction: str, valid_checksum: bool = True
    ) -> str:
        """Create a line of output as can be expected from a wind sensor."""
        checksum_string: str = (
            sensors.sensor.UNIT_IDENTIFIER
            + self.wind_sensor.delimiter
            + direction
            + self.wind_sensor.delimiter
            + speed
            + self.wind_sensor.delimiter
            + sensors.sensor.WINDSPEED_UNIT
            + self.wind_sensor.delimiter
            + sensors.sensor.GOOD_STATUS
            + self.wind_sensor.delimiter
        )
        checksum: int = 0
        for i in checksum_string:
            checksum ^= ord(i)

        # Mock a bad checksum
        if not valid_checksum:
            checksum = 0

        line = (
            sensors.sensor.START_CHARACTER
            + checksum_string
            + sensors.sensor.END_CHARACTER
            + f"{checksum:02x}"
            + self.wind_sensor.terminator
        )
        return line

    async def test_extract_telemetry(self) -> None:
        self.num_channels = 4
        self.disconnected_channel = None
        self.missed_channels = 0
        self.name = "WindSensor"
        self.log = logging.getLogger(type(self).__name__)
        self.wind_sensor = sensors.sensor.WindSensor(self.log)

        wind_data = ("015.00", "010")
        line = self.create_wind_sensor_line(speed=wind_data[0], direction=wind_data[1])
        reply = await self.wind_sensor.extract_telemetry(line=line)
        self.assertAlmostEqual(float(wind_data[0]), reply[0])
        self.assertAlmostEqual(float(wind_data[1]), reply[1])

        wind_data = ("001.00", "")
        line = self.create_wind_sensor_line(speed=wind_data[0], direction=wind_data[1])
        reply = await self.wind_sensor.extract_telemetry(line=line)
        self.assertAlmostEqual(float(wind_data[0]), reply[0])
        self.assertTrue(math.isnan(reply[1]))

        wind_data = ("015.00", "010")
        line = self.create_wind_sensor_line(
            speed=wind_data[0], direction=wind_data[1], valid_checksum=False
        )
        reply = await self.wind_sensor.extract_telemetry(line=line)
        self.assertTrue(math.isnan(reply[0]))
        self.assertTrue(math.isnan(reply[1]))

        line = f"{self.wind_sensor.terminator}"
        reply = await self.wind_sensor.extract_telemetry(line=line)
        self.assertTrue(math.isnan(reply[0]))
        self.assertTrue(math.isnan(reply[1]))
