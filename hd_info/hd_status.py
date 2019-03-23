#! /usr/bin/python3

import usb.core
import struct
import datetime

def open_device():
    dev = usb.core.find(idVendor=0x10c4, idProduct=0x82cd)
    if dev is None:
        raise ValueError('Our device is not connected')
    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    dev.set_configuration()
    return dev

def parse_status(data):
    fmt = '>BIHHHHHHHxxxxxHxxHH'
    fmt_names = ['cmd_id',
                 'time',
                 'record',
                 'temperature',
                 'RH',
                 'min_temp',
                 'max_temp',
                 'min_RH',
                 'max_RH',
                 'CO2',
                 'alert_CO2',
                 'flags']
    ar = struct.unpack(fmt, data)
    #print([hex(i) for i in ar])
    fields = dict(zip(fmt_names, ar))
    fields['time'] = str(datetime.datetime.utcfromtimestamp(fields['time']))
    fields['temperature'] = (fields['temperature'] - 400)/10
    fields['min_temp'] = (fields['min_temp'] - 400)/10
    fields['max_temp'] = (fields['max_temp'] - 400)/10

    fields['RH'] = fields['RH']/10
    fields['min_RH'] = fields['min_RH']/10
    fields['max_RH'] = fields['max_RH']/10
    
    return fields

def get_status(dev):
    ret = dev.ctrl_transfer(0xa1, CLEAR_FEATURE, 0x0105, 0, 0x3d)
    status = parse_status(ret)
    if status['cmd_id'] != 5:
        raise ValueError('Wrong returned cmd_id {status[\'cmd_id\']}')

def format_status(status):
    #print(status)
    result = '#{}({}): T={} RH={} CO2={}'.format(
        status['record'],
        status['time'],
        status['temperature'],
        status['RH'],
        status['CO2'])
    return result
        
    
    
def main():
    try:
        dev = open_device()
        status = get_status(dev)
    except ValueError as e:
        print(e)
        return
    print(format_status(status))

if __name__ == '__main__':
    main()

    print(format_status(parse_status(b'\x05\x5c\x96\x2f\x6c\x01\x65\x02\x69\x00\xef\x01\x90\x03\x20\x00\x64\x03\xb6\xb0\x03\x00\x07\xd0\x01\xf1\x00\x00\x07\xd0\x00\x02')))
