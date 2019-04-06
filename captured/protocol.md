# HT-501 usb protocol minimal description

This document describe results of reverse engineering device protocol. I have no access to the official documentation, and this document can contain mistakes.

## Sending requests

Request type is sending in low byte in wValue
05 - read status
06 - read settings parameters
07 - read record parameters

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
5           | 2            | record number
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

### Example
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


## Read parameters

Answer for set and recorded parameters has the same format. one difference is command ID.
Read parameters consist of two onswer packets, so it should be sent two requests.

Answer on read set parameters request 0

Byte offset | Field length | Value
------------|--------------|---------
0           | 1            | cmd_id. Always is 6 for set parameters request and 7 for recorded parameters
1           | 1            | packet id 0
2           | 1            | address
3           | 10           | serial number ascii string
13          | 18           | test name. UTF-16 stringv(all bytes is 2 bytes length)
31          | 1            | trailing byte?



Answer on read set parameters request 1

Byte offset | Field length | Value
------------|--------------|---------
0           | 1            | cmd_id. Always is 6 for set parameters request and 7 for recorded parameters
1           | 1            | packet id 1
2           | 2            | Maximum temp alert = (x-400)/10
4           | 2            | Min humidity alert  = x/10
6           | 2            | Max humidity alert  = x/10
8           | 1            | ??
9           | 4            | setting time. unix time format
13          | 1            | immediately/manually. manually=0, immediately=1
14          | 4            | start time. unix time format
18          | 2            | Test records
20          | 2            | ??
22          | 2            | Maximum CO2 level
24          | 7            | ????
31          | 1            | flags

Also somewhere should be information about Total records and records interval. 

### Example

```
ffff951b801dff00 2347178639 S Ci:1:005:0 s a1   01 0106 0000 003d 61 <
ffff951b801dff00 2347179708 C Ci:1:005:0 0 61   = 06000131 32333435 36373839 3062006c 00610062 006c0061 0062006c 00610000
ffff951c7cd7ccc0 2347179938 S Ci:1:005:0 s a1   01 0106 0000 003d 61 <
ffff951c7cd7ccc0 2347180783 C Ci:1:005:0 0 61   = 06010320 006403b6 005c977c 4a005c97 7c4a0000 000007d0 00000000 00000002
```

Packet 1
Bytes | value
------|-------
06    | answer for command 6
00    | packet id 0 in ans
01    | address 1
31 32333435 36373839 30 | serial number "1234567890"
62006c 00610062 006c0061 0062006c 006100 | test name "blablabla"
00 | trailling zero


Packet 2
Bytes | value
------|-------
06    | answer for command 6
00    | packet id 0 in ans
01    | address 1
0320  | 800=40.0+40 -> max temperature limit
0064  | 100=10.0    -> min RH
03b6  | 950=95.6    -> max RH
00    | ?? 
5c977c 4a | setting time 2019-03-24 12:47:06
00    | immediately/manually. manually = 0
5c97 7c4a | start time 2019-03-24 12:47:06
0000      | test records 0
0000      | ????
07d0      | max CO2 = 2000
00000000  | ??
00000002  | ??
