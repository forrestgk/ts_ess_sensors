===================================================
Serial protocol definition for: Omega HX85A Sensor.
===================================================

Garry Knight
2021-06-30

Serial Interface & Parameters
=============================

| Serial Interface: RS232
| BAUD: 19200
| Bits: 8
| Parity: None
| Stop Bits: 1
| Flow Control: None
| Data type: ISO8859-1

Bi-directional communication is allowed.
Writes to the instrument may be used to command interface options, but by default Omega HX85A continuously outputs serial data in terminated lines and no interface changes are therefore necessary.
Writes to the HX85A instrument from the protocol converter are not required.

Data is output as it is read and calculated by the instrument at a fixed period of approximately 1.35 seconds.
Data output by the HX85A instrument are:

    - Relative Humidity (Range 5% to 95%)
    - Air Temperature (Range -20C to +120C)
    - Dew Point (Range -60C to + 40C)

Example Output Line
===================

'%RH=38.86,AT°C=24.32,DP°C=9.57\\n\\r'

Line Format
===========

An output line consists of:

    - Data values are prefixed by identifiers and '='.
    - Relative humidity prefix: '%RH='
    - Air temperature prefix: 'AT°C='
      Note that the degree symbol is hex F8.
    - Dew point prefix: 'DP°C='
      Note that the degree symbol is hex F8.

Data values are comma delimited.

The line is terminated by '\\n\\r'.
This is unusual, in that the characters '\\r' and '\\n' characters are reversed from common practice.
The termination characters are also (and unusually) not sent immediately following the line, but appear 1 ms preceding the following line.
This may require some care in managing the receiver code in the protocol converter or avoiding using these characters as the line terminator.

Line Length
===========

The line is a variable length line.
This is due to variable size of the data values which have no padding/leading spaces or zeroes, but precision is fixed to two decimal places.

Recommended Integrity Checks
============================

Lines are continuously output every ~1.35 seconds.
Timeout may be used to determine if instrument is connected/disconnected.
Timeout should occur if terminator is not received within the timeout period.
Recommended minimum timeout is 1.6 seconds.

Split line by comma delimiter and test that there are three elements.

Test fixed preamble/identifier for each data value.

Value errors are not defined in the manual and since the unit is self-contained it is not clear what is reported in the case of error.
Test for non-numeric value or out-of-range values.
