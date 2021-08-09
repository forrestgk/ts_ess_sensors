===================================================================
Serial protocol definition for: SEL Temperature Sensor Instruments.
===================================================================

Garry Knight.
2021-08-08

Serial Interface & Parameters
=============================

| Serial Interface: RS232
| BAUD: 19200
| Bits: 8
| Parity: None
| Stop Bits: 1
| Flow Control: None
| Data type: ISO8859-1

Straight Engineering Limited (SEL) Temperature instruments are multi-channel measurement instruments.
The number of channels and sensor type vary by model.
The instruments are read only.

There are two types of instruments utilizing either thermocouple sensors or RTD sensors.
The read protocol is affected only by the number of sensor channels and sensor type.

Data output by the SEL temperature instruments are:

    - Temperature \* n channels

Data for each channel is output as it is read and calculated by the instrument at a fixed period of approximately ~0.167 seconds.
A line terminator is added to the serial output of the final channel once all channels have been read.

Example Output Line For 4-Channel Instrument
============================================

RTD Instruments:
'C01=0032.1443,C02=0033.0320,C03=-001.3020,C04=-201.0000\\r\\n'

Thermocouple Instruments:
'C00=0025.43,C01=0032.1443,C02=0033.0320,C03=-001.3020,C04=9999.9990\\r\\n'

The measurement and output line for a RTD instrument occurs over time as:

    - ... 0.167 second delay ...
    - 'C01=0032.1443,'
    - ... 0.167 second delay ...
    - 'C02=0033.0320,'
    - ... 0.167 second delay ...
    - 'C03=-001.3020,'
    - ... 0.167 second delay ...
    - 'C04=-201.0000\\r\\n'

The measurement and output line for a thermocouple instrument occurs over time as:

    - ... 0.167 second delay ...
    - 'C00=0025.4300,'
    - ... 0.167 second delay ...
    - 'C01=0032.1443,'
    - ... 0.167 second delay ...
    - 'C02=0033.0320,'
    - ... 0.167 second delay ...
    - 'C03=-001.3020,'
    - ... 0.167 second delay ...
    - 'C04=9999.9990\\r\\n'

Line Format
===========

A line consists of:

    - Channel data * n channels, delimited by comma.
    - The line is terminated immediately following the final channel data value by \\r\\n.

Channel data is in the form 'Cxx=snnn.nnnn', consisting of a prefix followed by a decimal value.

The channel data prefix is four characters:

    - 'Cxx='.
    - 'C' is the unit, Celcius.
    - 'xx' is a two character decimal integer channel number with leading zero.

Channel '00' is reserved only for thermocouple instruments that also read the internal temperature reference value.
Both thermocouple and RTD instrument sensor instruments input channels are indexed from '01', but thermocouple instruments include reference channel '00' in their output.
See "Line Length" section later in this document. '=' fixed equals sign.

The temperature value is nine characters long and in the fixed form:

    - 'snnn.nnnn'.
    - 's' is the sign. Where a negative value is '-' and positive is '0' thru '9'.
    - 'n' is '0' thru '9'.
    - '.' decimal point character is fixed in the fifth position of the value.

Channel Error or Disconnected Value
-----------------------------------
The instrument can report an error for any temperature channel. The error value commonly represents that the sensor is disconnected.
Due to the nature of operation of thermocouple and RTD measurements, the instrument error value differs between the two instrument types.
A thermocouple instrument reports an error value of: '-201.0000'
A RTD instrument reports an error value of: '9999.9990'

Line Length
===========
The line length is fixed, but dependent upon the number of channels and instrument sensor type.
The presence of the reference value (indicating thermocouple instrument) may be determined by checking for channel number '00' as the first data value.
The data output for each channel is a fixed length of 13 characters excluding delimiter.

| Delimiter length: 1
| Terminator length: 2

Output Line Length For 4-Channel RTD Instrument
-----------------------------------------------
'C01=0032.1443,C02=0033.0320,C03=-001.3020,C04=9999.9990\r\n'

In this case the line length may be calculated as:

    - ((Number of channels + 1) * 14)

Output Line Length For 4-Channel Thermocouple Instrument With Internal Reference Output
---------------------------------------------------------------------------------------
'C00=0024.4550,C01=0032.1443,C02=0033.0320,C03=-001.3020,C04=-201.0000\r\n'

In this case the line length may be calculated as:

    - ((Number of channels + 1) * 14) + 1

Thermocouple instruments provide the internal temperature reference value as channel '00'.
In this case the line will appear to have an extra channel ('C00') at the beginning of the output line.
The presence of the reference value, indicating thermocouple instrument, may be determined by checking the channel number of the first data value.

Recommended Integrity Checks
============================
There is no checksum or other form of integrity test supplied by the instrument in each output line.
Tests performed on the data should be performed on the basis of line length and expected format of the data.

Timeout may be used to determine if the instrument is connected/disconnected.
Timeout should occur if terminator is not received within the timeout period.
Channel data is continuously output at a rate of 0.167 seconds per channel.
A four channel RTD instrument therefore takes 4 * 0.167 = ~0.67 seconds to complete a line.
A four channel thermocouple instrument therefore takes (4 + 1) * 0.167 = ~0.835 seconds to complete a line.
A timeout check may be applied to a terminated line with timeout value based upon number of channels read by the instrument.

Split output line by comma delimiter and test for correct number of channels.

Test fixed preamble for each channel number.

Test channel temperature value format and that they are convertible to float data type.
