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

__all__ = ["DeviceConfig"]

from typing import Dict, Union

from .constants import DeviceType, Key, SensorType


class DeviceConfig:
    """Configuration for a device.

    Parameters
    ----------
    name: `str`
        The name of the device.
    dev_type: `str`
        The type of device.
    dev_id: `str`
        The ID of the device.
    sens_type: `str`
        The type of sensor.
    num_channels: `int`, optional
        The number of channels the output data, or 0 indicating that the number
        of channels is not configurable for this type of device.

    """

    def __init__(
        self,
        name: str,
        dev_type: str,
        dev_id: str,
        sens_type: str,
        num_channels: int = 0,
    ) -> None:
        self.name = name
        self.num_channels = num_channels
        self.dev_type = dev_type
        self.dev_id = dev_id
        self.sens_type = sens_type

    def as_dict(self) -> Dict[str, Union[str, int]]:
        """Return a dict with the instance attributes and their values as
        key-value pairs.

        Returns
        -------
        device_config_as_dict: `dict`
            A dictionary of key-value pairs representing the instance
            attributes and their values.
        """
        device_config_as_dict: Dict[str, Union[str, int]] = {
            Key.NAME: self.name,
            Key.DEVICE_TYPE: self.dev_type,
            Key.SENSOR_TYPE: self.sens_type,
        }

        # FTDI devices have an FTDI ID and Serial devices have a serial port.
        if self.dev_type == DeviceType.FTDI:
            device_config_as_dict[Key.FTDI_ID] = self.dev_id
        elif self.dev_type == DeviceType.SERIAL:
            device_config_as_dict[Key.SERIAL_PORT] = self.dev_id
        else:
            raise ValueError(f"Received unknown DeviceType {self.dev_type}")

        # Only temperature sensors have a configurable number of channels.
        if self.sens_type == SensorType.TEMPERATURE:
            device_config_as_dict[Key.CHANNELS] = self.num_channels
        return device_config_as_dict
