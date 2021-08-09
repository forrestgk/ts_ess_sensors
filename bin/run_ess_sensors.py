#!/usr/bin/env python

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

import asyncio
import logging

from lsst.ts.ess.sensors import SocketServer

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
    level=logging.DEBUG,
)


async def main():
    """Main method that, when executed in stand alone mode, starts the socket
    server.

    The SocketServer automatically stops once the client exits and at that
    moment this script will exit as well.
    """
    logging.info("main method")
    # An arbitrarily chosen port. Nothing special about it.
    host = "0.0.0.0"
    port = 5000
    logging.info("Constructing the sensor server.")
    # Simulation mode 0 means "connect to the real sensors."
    # Set simulation_mode to 1 to enable simulation mode and connect to a mock
    # sensor.
    srv = SocketServer(host=host, port=port, simulation_mode=0)
    logging.info("Starting the sensor server.")
    await srv.start_task
    await srv.server.wait_closed()


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG
    )

    try:
        logging.info("Calling main method")
        asyncio.run(main())
    except (asyncio.CancelledError, KeyboardInterrupt):
        pass
