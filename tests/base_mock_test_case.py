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

__all__ = ["BaseMockTestCase"]

import math
import unittest

from lsst.ts.ess import sensors


class BaseMockTestCase(unittest.IsolatedAsyncioTestCase):
    def check_hx85a_reply(self, reply):
        device_name = reply[0]
        time = reply[1]
        response_code = reply[2]
        resp = reply[3:]

        self.assertEqual(self.name, device_name)
        self.assertGreater(time, 0)
        if self.in_error_state:
            self.assertEqual(sensors.ResponseCode.DEVICE_READ_ERROR, response_code)
        else:
            self.assertEqual(sensors.ResponseCode.OK, response_code)
        self.assertEqual(len(resp), 3)
        for i in range(0, 3):
            if i < self.missed_channels or self.in_error_state:
                self.assertTrue(math.isnan(resp[i]))
            else:
                if i == 0:
                    self.assertLessEqual(sensors.MockHumidityConfig.min, resp[i])
                    self.assertLessEqual(resp[i], sensors.MockHumidityConfig.max)
                elif i == 1:
                    self.assertLessEqual(sensors.MockTemperatureConfig.min, resp[i])
                    self.assertLessEqual(resp[i], sensors.MockTemperatureConfig.max)
                else:
                    self.assertLessEqual(sensors.MockDewPointConfig.min, resp[i])
                    self.assertLessEqual(resp[i], sensors.MockDewPointConfig.max)

    def check_hx85ba_reply(self, reply):
        device_name = reply[0]
        time = reply[1]
        response_code = reply[2]
        resp = reply[3:]

        self.assertEqual(self.name, device_name)
        self.assertGreater(time, 0)
        if self.in_error_state:
            self.assertEqual(sensors.ResponseCode.DEVICE_READ_ERROR, response_code)
        else:
            self.assertEqual(sensors.ResponseCode.OK, response_code)
        self.assertEqual(len(resp), 3)
        for i in range(0, 3):
            if i < self.missed_channels or self.in_error_state:
                self.assertTrue(math.isnan(resp[i]))
            else:
                if i == 0:
                    self.assertLessEqual(sensors.MockHumidityConfig.min, resp[i])
                    self.assertLessEqual(resp[i], sensors.MockHumidityConfig.max)
                elif i == 1:
                    self.assertLessEqual(sensors.MockTemperatureConfig.min, resp[i])
                    self.assertLessEqual(resp[i], sensors.MockTemperatureConfig.max)
                else:
                    self.assertLessEqual(sensors.MockPressureConfig.min, resp[i])
                    self.assertLessEqual(resp[i], sensors.MockPressureConfig.max)

    def check_temperature_reply(self, reply):
        device_name = reply[0]
        time = reply[1]
        response_code = reply[2]
        resp = reply[3:]

        self.assertEqual(self.name, device_name)
        self.assertGreater(time, 0)
        if self.in_error_state:
            self.assertEqual(sensors.ResponseCode.DEVICE_READ_ERROR, response_code)
        else:
            self.assertEqual(sensors.ResponseCode.OK, response_code)
        self.assertEqual(len(resp), self.num_channels)
        for i in range(0, self.num_channels):
            if i < self.missed_channels or self.in_error_state:
                self.assertTrue(math.isnan(resp[i]))
            elif i == self.disconnected_channel:
                self.assertTrue(math.isnan(resp[i]))
            else:
                self.assertLessEqual(sensors.MockTemperatureConfig.min, resp[i])
                self.assertLessEqual(resp[i], sensors.MockTemperatureConfig.max)
