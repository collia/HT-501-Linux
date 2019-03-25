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
    dev.reset()
    if dev.is_kernel_driver_active(0) == True:
        dev.detach_kernel_driver(0)
    cfg = dev.get_active_configuration()
    #print(cfg)
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
    ar = struct.unpack(fmt, bytearray(data))
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
    ret = dev.ctrl_transfer(0xa1, 1, 0x0105, 0, 0x3d)
    
    status = parse_status(ret)
    if status['cmd_id'] != 5:
        raise ValueError('Wrong returned cmd_id {}'.format(status['cmd_id']))
    return status

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

    assert format_status(parse_status([0x05,0x5c,0x96,0x2f,0x6c,0x01,0x65,0x02,0x69,0x00,0xef,0x01,0x90,0x03,0x20,0x00,0x64,0x03,0xb6,0xb0,0x03,0x00,0x07,0xd0,0x01,0xf1,0x00,0x00,0x07,0xd0,0x00,0x02])) == '#357(2019-03-23 13:06:52): T=21.7 RH=23.9 CO2=497'
