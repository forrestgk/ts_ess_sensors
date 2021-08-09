.. py:currentmodule:: lsst.ts.ess.sensors

.. _lsst.ts.ess.sensors.version_history:

###############
Version History
###############

v0.3.0
======

* Added support for the Omega HX85A and HX85BA humidity sensors.
* Made the FTDI and RpiSerialHat devices work.
* Added exception handling in the sensors code.
* Cleaned up the Python modules.
* Added dcoumentation for the sensor protocols.
* Validating incoming configurations against a JSON schema instead of using very complicated custom code.
* Renamed the project to ts_ess_sensors.

Requires:

* ts_tcpip 0.3.1


v0.2.0
======

* Made the conda package `noarch`.

Requires:

* ts_tcpip 0.3.1


v0.1.0
======

First release of the Environmental Sensors Suite socket server and sensor reading code.

This version already includes many useful things:

* A functioning socket server (for which the ``ts_tcpip`` socket server is used).
* Code that reads the output of the connected sensors and sends the data via the socket server.
* Support for USB and FTDI sensors.
* Added support for connecting to and reading telemetry from multiple sensors.
* Added configuration error handling.

Requires:

* ts_tcpip 0.2.0
