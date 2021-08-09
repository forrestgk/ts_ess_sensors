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

__all__ = ["BaseSensor"]

from abc import ABC, abstractmethod
import logging
from typing import List, Union


class BaseSensor(ABC):
    """Base class for the different types of Sensors.

    This class holds all common code for the sensors. Sensor specific code
    (for instance temperature or wind sensor) needs to be implemented in a
    sub-class.

    Parameters
    ----------
    log: `logging.Logger`
        The logger to create a child logger for.
    num_channels: `int`, optional
        The number of channels that the sensor will produce telemetry for. The
        default value is 0 meaning that the number of channels is not variable.
    """

    @abstractmethod
    def __init__(self, log: logging.Logger, num_channels: int = 0) -> None:
        self.num_channels: int = num_channels
        self.log = log.getChild(type(self).__name__)

        # Data line terminator. In general this is the value used by all
        # sensors but some sensors may need to override this value.
        self.terminator = "\r\n"
        # Data line terminator. In general this is the value used by all
        # sensors but some sensors may need to override this value.
        self.delimiter = ","
        # Character set for the data line. In general this is the value used by
        # all sensors but some sensors may need to override this value.
        self.charset = "ASCII"

    @abstractmethod
    async def extract_telemetry(self, line: str) -> List[float]:
        """Extract the telemetry from a line of Sensor data.

        Returns
        -------
        output: `list`
            A list containing the telemetry as measured by the specific type of
            sensor. The length of the output list is the same as the number of
            channels.
        """
        pass
