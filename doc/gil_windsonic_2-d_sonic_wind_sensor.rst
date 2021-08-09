###################################################################
Serial protocol definition for: GIL Winsonic 2-D Sonic Wind Sensor.
###################################################################

Garry Knight
2021-07-15

Serial Interface & Parameters
=============================

| Serial Interface: RS232
| BAUD: 9600
| Bits: 8
| Parity: None
| Stop Bits: 1
| Flow Control: None
| Data type: ISO8859-1

The GIL Windsonic 2-D Sonic Wind Sensor (Anemometer) measures wind speed and direction.

Data output by the Anemometer instrument is:

    - Wind Speed
    - Wind Direction

Data is output as it is read and calculated by the instrument at a fixed period of approximately ~1.0 seconds.

Example Output Line
===================

'Q,ddd,sss.ss,M,00,checksum'

Line Format
===========

    An output line consists of:

    - ASCII start character.
    - 'Q' Unit Identifier ('Q' is default value).
    - ddd Wind direction.
      Three character, leading zero's integer.
      000-359 degrees.
      Wind direction value is empty ('') when wind speed is below 0.05 m/s.
    - sss.ss Wind speed.
      Six character, floating point, leading zero's.
      0 to 60 m/s.
    - 'M' Units of speed measurement ('M' is m/s default)
    - '00' Status.
    - ASCII end charactor.
    - checksum Exclusive OR of all bytes in the string between and characters.
    - 2-character terminator ('\\r\\n').

Line Length
===========

The line length is not fixed and is dependent upon the value of the wind speed which affects whether or not wind direction can be determined.
Direction cannot be calculated if wind speed is below 0.05 m/s.

Example output line with direction information (wind speed above 0.05 m/s)
--------------------------------------------------------------------------

| 'Q,036,002.57,M,00,checksum'
| In this case, line length is 22 characters.

Example output line without direction information (wind speed below 0.05 m/s)
-----------------------------------------------------------------------------

| 'Q,,000.04,M,00,checksum'
| In this case, line length is 19 characters.

Recommended Integrity Checks
============================

The checksum may be used as an intergrity test. Tests performed on the data may also include line length and expected format of the data.

Timeout may be used to determine if the instrument is connected/disconnected.
Timeout should occur if terminator is not received within the timeout period.
Channel data is continuously output at a rate of ~1.0 seconds per channel.

Split output line by comma delimiter and test for correct number of elements.

Test direction value (if present) and speed value format and that they are convertible to float data type.

Test status value for non-zero ('00') value.
