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


class CommandHandlerTestCase(BaseMockTestCase):
    async def asyncSetUp(self):
        self.command_handler = sensors.CommandHandler(
            callback=self.callback, simulation_mode=1
        )
        self.assertIsNone(self.command_handler._configuration)

        # Despite simulation_mode being set to 1, full fledged configuration is
        # needed because of the configuration validation. All device
        # configuration is ignored but the sensor type is not. The main
        # objective is to test multiple sensors at the same time.
        device_config_01 = sensors.DeviceConfig(
            name="Test01",
            num_channels=4,
            dev_type=sensors.DeviceType.FTDI,
            dev_id="ABC",
            sens_type=sensors.SensorType.TEMPERATURE,
        )
        device_config_02 = sensors.DeviceConfig(
            name="Test02",
            dev_type=sensors.DeviceType.FTDI,
            dev_id="ABC",
            sens_type=sensors.SensorType.HX85A,
        )
        device_config_03 = sensors.DeviceConfig(
            name="Test03",
            dev_type=sensors.DeviceType.FTDI,
            dev_id="ABC",
            sens_type=sensors.SensorType.HX85BA,
        )
        self.configuration = {
            sensors.Key.DEVICES: [
                device_config_01.as_dict(),
                device_config_02.as_dict(),
                device_config_03.as_dict(),
            ]
        }
        self.device_configs = {
            device_config_01.name: device_config_01,
            device_config_02.name: device_config_02,
            device_config_03.name: device_config_03,
        }
        self.responses = []

    async def callback(self, response):
        self.responses.append(response)

    def assert_response(self, response_code):
        response = self.responses.pop()
        self.assertEqual(response[sensors.Key.RESPONSE], response_code)

    async def test_configure(self):
        """Test the configuration validation of the CommandHandler."""

        # Test with the configuration as set in asyncSetUp, which is a good
        # configuration.
        await self.command_handler.handle_command(
            command=sensors.Command.CONFIGURE, configuration=self.configuration
        )
        self.assert_response(sensors.ResponseCode.OK)
        self.assertDictEqual(self.configuration, self.command_handler._configuration)

        # The value for sensors.Key.DEVICES may not be empty.
        bad_configuration = {sensors.Key.DEVICES: []}
        await self.command_handler.handle_command(
            command=sensors.Command.CONFIGURE, configuration=bad_configuration
        )
        self.assert_response(sensors.ResponseCode.INVALID_CONFIGURATION)

        # A configuration with several errors that will get tested one by one.
        bad_items = [
            {
                # The mandatory keys sensors.Key.CHANNELS,
                # sensors.Key.DEVICE_TYPE and KEY.SENSOR_TYPE are missing.
                sensors.Key.NAME: "Test1",
            },
            {
                # The mandatory keys sensors.Key.DEVICE_TYPE and
                # sensors.Key.SENSOR_TYPE are missing.
                sensors.Key.NAME: "Test1",
                sensors.Key.CHANNELS: 4,
            },
            {
                # The mandatory key sensors.Key.SENSOR_TYPE is missing.
                sensors.Key.NAME: "Test1",
                sensors.Key.CHANNELS: 4,
                sensors.Key.DEVICE_TYPE: sensors.DeviceType.FTDI,
            },
            {
                # For sensors.DeviceType.FTDI the key
                # sensors.Key.FTDI_ID is mandatory.
                sensors.Key.NAME: "Test1",
                sensors.Key.CHANNELS: 4,
                sensors.Key.DEVICE_TYPE: sensors.DeviceType.FTDI,
                "id": "ABC",
                sensors.Key.SENSOR_TYPE: sensors.SensorType.TEMPERATURE,
            },
            {
                # For sensors.DeviceType.SERIAL the key
                # sensors.Key.SERIAL_PORT is mandatory.
                sensors.Key.NAME: "Test1",
                sensors.Key.CHANNELS: 4,
                sensors.Key.DEVICE_TYPE: sensors.DeviceType.SERIAL,
                "port": "ABC",
                sensors.Key.SENSOR_TYPE: sensors.SensorType.TEMPERATURE,
            },
            {
                # Wrong value for sensors.Key.SENSOR_TYPE.
                sensors.Key.NAME: "Test1",
                sensors.Key.CHANNELS: 4,
                sensors.Key.DEVICE_TYPE: sensors.DeviceType.SERIAL,
                sensors.Key.SERIAL_PORT: "ABC",
                sensors.Key.SENSOR_TYPE: "Temp",
            },
        ]
        for bad_item in bad_items:
            bad_configuration = {sensors.Key.DEVICES: [bad_item]}
            await self.command_handler.handle_command(
                command=sensors.Command.CONFIGURE, configuration=bad_configuration
            )
            self.assert_response(sensors.ResponseCode.INVALID_CONFIGURATION)

    async def test_start(self):
        """Test handling of the start command."""
        await self.command_handler.handle_command(command=sensors.Command.START)
        self.assert_response(sensors.ResponseCode.NOT_CONFIGURED)
        self.assertIsNone(self.command_handler._configuration)
        self.assertFalse(self.command_handler._started)

        await self.command_handler.handle_command(
            command=sensors.Command.CONFIGURE, configuration=self.configuration
        )
        self.assert_response(sensors.ResponseCode.OK)
        self.assertDictEqual(self.configuration, self.command_handler._configuration)
        await self.command_handler.handle_command(command=sensors.Command.START)
        self.assert_response(sensors.ResponseCode.OK)
        self.assertTrue(self.command_handler._started)

    async def test_stop(self):
        """Test handling of the stop command."""
        await self.command_handler.handle_command(command=sensors.Command.STOP)
        self.assert_response(sensors.ResponseCode.NOT_STARTED)
        self.assertIsNone(self.command_handler._configuration)
        self.assertFalse(self.command_handler._started)

        await self.command_handler.handle_command(
            command=sensors.Command.CONFIGURE, configuration=self.configuration
        )
        self.assert_response(sensors.ResponseCode.OK)
        self.assertDictEqual(self.configuration, self.command_handler._configuration)
        await self.command_handler.handle_command(command=sensors.Command.START)
        self.assert_response(sensors.ResponseCode.OK)
        self.assertTrue(self.command_handler._started)

        await self.command_handler.handle_command(command=sensors.Command.STOP)
        self.assert_response(sensors.ResponseCode.OK)
        # Give time to the telemetry_task to get cancelled.
        await asyncio.sleep(0.5)
        self.assertFalse(self.command_handler._started)

    async def test_get_telemetry(self):
        """Test handling of telemetry."""
        await self.command_handler.handle_command(
            command=sensors.Command.CONFIGURE, configuration=self.configuration
        )
        self.assert_response(sensors.ResponseCode.OK)
        self.assertDictEqual(self.configuration, self.command_handler._configuration)
        await self.command_handler.handle_command(command=sensors.Command.START)
        self.assert_response(sensors.ResponseCode.OK)
        self.assertTrue(self.command_handler._started)

        # Give some time to the mock sensor to produce data
        while len(self.responses) < len(self.device_configs):
            await asyncio.sleep(0.5)

        devices_names_checked = set()
        while len(devices_names_checked) != len(self.device_configs):
            reply = self.responses.pop()
            self.name = reply[sensors.Key.TELEMETRY][0]
            devices_names_checked.add(self.name)
            device_config = self.device_configs[self.name]
            self.disconnected_channel = None
            self.missed_channels = 0
            self.in_error_state = False
            reply_to_check = reply[sensors.Key.TELEMETRY]
            if device_config.sens_type == sensors.SensorType.TEMPERATURE:
                self.num_channels = device_config.num_channels
                self.check_temperature_reply(reply_to_check)
            elif device_config.sens_type == sensors.SensorType.HX85A:
                self.check_hx85a_reply(reply_to_check)
            else:
                self.check_hx85ba_reply(reply_to_check)

        await self.command_handler.handle_command(command=sensors.Command.STOP)
        self.assert_response(sensors.ResponseCode.OK)
        # Give time to the telemetry_task to get cancelled.
        await asyncio.sleep(0.5)
        self.assertFalse(self.command_handler._started)
