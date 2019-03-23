# HT-501 usb protocol minimal description

This document describe results of reverse engineering device protocol. I have no access to the official documentation, and this document can contain mistakes.

## Sending requests

Request type is sending in low byte in wValue
05 - read status
06 - read settings param
07 - read record param 

All other fields have the same value:
```
ffff92c123517300 424740455 S Ci:1:011:0 s      a1 01 0105 0000 003d 61 <
                                               bmRequestType 0xa1
                                                 - device to host
                                                 - class
                                                 - interface
                                               bRequest 0x01
                                                 CLEAR_FEATURE
                                               wValue
                                                 0x0105
                                               wIndex
                                                 0000
                                               wLength
                                                 0x003d

```

## Read status

Answer on read status request

Byte offset | Field length | Value
------------|--------------|---------
0           | 1            | cmd_id. Always is 5
1           | 4            | unixtime for record
5           | 2            | Number of record
7           | 2            | Current temperature = (x-400)/10
9           | 2            | Current humidity  = x/10
11          | 2            | Minimal temp alert = (x-400)/10
13          | 2            | Maximum temp alert = (x-400)/10
15          | 2            | Min humidity alert  = x/10
17          | 2            | Max humidity alert  = x/10
19          | 3            | ???
22          | 2            | ???. Similar to alert CO2
24          | 2            | current CO2
26          | 2            | ???
28          | 2            | Alert level CO2
30          | 2            | Status flags

Example
```
ffff92c123517300 424740455 S Ci:1:011:0 s      a1 01 0105 0000 003d 61 <
ffff92c123517300 424740945 C Ci:1:011:0 0      32 = 055c962f 6c016502 6900ef01 90032000 6403b6b0 030007d0 01f10000 07d00002
```
Bytes | value
------|-------
05 | cmd id
5c962f6c  | time '2019-03-23 13:06:52'
0165      | record # 357 
0269      | temperature = (617-400)/10 = 21.7
00ef      | humidity = 23.9
0190      | min temperature = (400-400) = 0
0320      | max temperature = (800-400)/10 = 40.0
0064      | min humidity = 10.0 %
03b6      | max humidity = 95.0 %
b00300    | ???
07d0      | ?? == 2000
01f1      | CO2 value = 497 ppm
0000      | reserved
07d0      | max CO2   = 2000 ppm
0002      | status ???



