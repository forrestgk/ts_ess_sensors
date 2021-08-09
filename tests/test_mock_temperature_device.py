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
import unittest

from lsst.ts.ess import sensors
from base_mock_test_case import BaseMockTestCase

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
)


class MockDeviceTestCase(BaseMockTestCase):
    async def _callback(self, reply):
        logging.info(f"Received reply {reply!r}")
        self.reply = reply

    async def _check_mock_temperature_device(self):
        """Check the working of the MockDevice."""
        self.data = None
        self.log = logging.getLogger(type(self).__name__)
        tempt_sensor = sensors.sensor.TemperatureSensor(
            num_channels=self.num_channels, log=self.log
        )
        mock_device = sensors.device.MockDevice(
            name=self.name,
            device_id="MockDevice",
            sensor=tempt_sensor,
            callback_func=self._callback,
            log=self.log,
            disconnected_channel=self.disconnected_channel,
            missed_channels=self.missed_channels,
            in_error_state=self.in_error_state,
        )

        await mock_device.open()

        # First read of the telemetry to verify that handling of truncated data
        # is performed correctly if the MockDevice is instructed to produce
        # such data.
        self.reply = None
        while not self.reply:
            await asyncio.sleep(0.1)
        reply_to_check = self.reply[sensors.Key.TELEMETRY]
        self.check_temperature_reply(reply_to_check)

        # Reset self.missed_channels for the second read otherwise the check
        # will fail.
        if self.missed_channels > 0:
            self.missed_channels = 0

        # First read of the telemetry to verify that no more truncated data is
        # produced is the MockDevice was instructed to produce such data.
        self.reply = None
        while not self.reply:
            await asyncio.sleep(0.1)
        reply_to_check = self.reply[sensors.Key.TELEMETRY]
        self.check_temperature_reply(reply_to_check)

        await mock_device.close()

    async def test_mock_temperature_device(self):
        """Test the MockDevice with a nominal configuration, i.e. no
        disconnected channels and no truncated data.
        """
        self.name = "MockSensor"
        self.num_channels = 4
        self.disconnected_channel = None
        self.missed_channels = 0
        self.in_error_state = False
        await self._check_mock_temperature_device()

    async def test_mock_temperature_device_with_disconnected_channel(self):
        """Test the MockDevice with one disconnected channel and no truncated
        data.
        """
        self.name = "MockSensor"
        self.num_channels = 4
        self.disconnected_channel = 2
        self.missed_channels = 0
        self.in_error_state = False
        await self._check_mock_temperature_device()

    async def test_mock_temperature_device_with_truncated_output(self):
        """Test the MockDevice with no disconnected channels and truncated data
        for two channels.
        """
        self.name = "MockSensor"
        self.num_channels = 4
        self.disconnected_channel = None
        self.missed_channels = 2
        self.in_error_state = False
        await self._check_mock_temperature_device()

    async def test_mock_temperature_device_in_error_state(self):
        """Test the MockDevice in error state meaning it will only return empty
        strings.
        """
        self.name = "MockSensor"
        self.num_channels = 4
        self.disconnected_channel = None
        self.missed_channels = 0
        self.in_error_state = True
        await self._check_mock_temperature_device()
