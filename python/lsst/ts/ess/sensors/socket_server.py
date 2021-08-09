from __future__ import annotations

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

__all__ = ["SocketServer"]

import asyncio
import json
import logging
import socket
import typing

from .command_handler import CommandHandler
from lsst.ts import tcpip


class SocketServer(tcpip.OneClientServer):
    """A server for exchanging messages that talks over TCP/IP.

    Upon initiation a socket server is set up which waits for incoming
    commands. When an exit command is received, the socket server will exit.
    All other commands are dispatched to the command handler.

    Parameters
    ----------
    host : `str` or `None`
        IP address for this server.
        If `None` then bind to all network interfaces.
    port : `int`
        IP port for this server. If 0 then use a random port.
    simulation_mode : `int`, optional
        Simulation mode. The default is 0: do not simulate.
    """

    valid_simulation_modes = (0, 1)

    def __init__(
        self,
        host: typing.Optional[str],
        port: int,
        simulation_mode: int = 0,
        family: socket.AddressFamily = socket.AF_UNSPEC,
    ) -> None:
        self.name = "EnvSensor"
        if simulation_mode not in self.valid_simulation_modes:
            raise ValueError(
                f"simulation_mode={simulation_mode} "
                f"not in valid_simulation_modes={self.valid_simulation_modes}"
            )

        self.simulation_mode = simulation_mode
        self.read_loop_task: asyncio.Future = asyncio.Future()
        self.log: logging.Logger = logging.getLogger(type(self).__name__)

        self.command_handler: CommandHandler = CommandHandler(
            callback=self.write, simulation_mode=self.simulation_mode
        )
        super().__init__(
            name=self.name,
            host=host,
            port=port,
            log=self.log,
            connect_callback=self.connected_callback,
            family=family,
        )

    def connected_callback(self, server: SocketServer) -> None:
        """A client has connected or disconnected."""
        self.read_loop_task.cancel()
        if server.connected:
            self.log.info("Client connected.")
            self.read_loop_task = asyncio.create_task(self.read_loop())
        else:
            self.log.info("Client disconnected.")

    async def write(self, data: dict) -> None:
        """Write the data appended with a newline character.

        The data are encoded via JSON and then passed on to the StreamWriter
        associated with the socket.

        Parameters
        ----------
        data: `dict`
            The data to write.
        """
        self.log.debug(f"Writing data {data}")
        st = json.dumps({**data})
        self.log.debug(st)
        self.writer.write(st.encode() + tcpip.TERMINATOR)
        await self.writer.drain()
        self.log.debug("Done")

    async def read_loop(self) -> None:
        """Read commands and output replies."""
        try:
            self.log.info(f"The read_loop begins connected? {self.connected}")
            while self.connected:
                self.log.debug("Waiting for next incoming message.")
                try:
                    line = await self.reader.readuntil(tcpip.TERMINATOR)
                    line = line.decode().strip()
                    self.log.debug(f"Read command line: {line!r}")
                    items = json.loads(line)
                    cmd = items["command"]
                    kwargs = items["parameters"]
                    if cmd == "exit":
                        await self.exit()
                    elif cmd == "disconnect":
                        await self.disconnect()
                    else:
                        await self.command_handler.handle_command(cmd, **kwargs)

                except asyncio.IncompleteReadError:
                    self.log.exception("Read error encountered. Retrying.")

        except Exception:
            self.log.exception("read_loop failed")

    async def disconnect(self) -> None:
        await self.close_client()

    async def exit(self) -> None:
        """Stop the TCP/IP server."""
        self.log.info("Closing server")
        await self.close()

        self.log.info("Done closing")
