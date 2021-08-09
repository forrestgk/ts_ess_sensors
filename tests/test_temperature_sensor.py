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


class TemperatureSensorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_extract_telemetry(self):
        self.num_channels = 4
        self.disconnected_channel = None
        self.missed_channels = 0
        self.name = "TemperatureSensor"
        self.log = logging.getLogger(type(self).__name__)
        sensor = sensors.sensor.TemperatureSensor(self.log, self.num_channels)
        line = f"C00=0021.1234,C01=0021.1220,C02=0021.1249,C03=0020.9990{sensor.terminator}"
        reply = await sensor.extract_telemetry(line=line)
        self.assertListEqual(reply, [21.1234, 21.122, 21.1249, 20.999])
        line = f"C00=0021.1230,C01=0021.1220,C02=9999.9990,C03=0020.9999{sensor.terminator}"
        reply = await sensor.extract_telemetry(line=line)
        self.assertListEqual(reply, [21.123, 21.122, math.nan, 20.9999])
        line = f"0021.1224,C02=0021.1243,C03=0020.9992{sensor.terminator}"
        reply = await sensor.extract_telemetry(line=line)
        self.assertListEqual(reply, [math.nan, math.nan, 21.1243, 20.9992])
        with self.assertRaises(ValueError):
            line = f"0021.1224,C02=0021.1243,C03==0020.9992{sensor.terminator}"
            reply = await sensor.extract_telemetry(line=line)
        line = f"{sensor.terminator}"
        reply = await sensor.extract_telemetry(line=line)
        self.assertListEqual(reply, [math.nan, math.nan, math.nan, math.nan])
