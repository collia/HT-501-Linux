#! /usr/bin/python3

import struct
import datetime
import ht_device


def parse_parameters_pkt_1(data):
    fmt = '>BBB10s30s18s'
    fmt_names = ['cmd_id',
                 'packet_id',
                 'address',
                 'serial',
                 'test_name',
                 'unknown']
    #print(data)
    ar = struct.unpack(fmt, bytearray(data))
    #print([hex(i) for i in ar])
    fields = dict(zip(fmt_names, ar))

    fields['serial'] = fields['serial'].decode('ascii')
    fields['test_name'] = fields['test_name'].decode('utf-16')
    fields['unknown'] = [hex(i) for i in fields['unknown']]
    
    return fields

def parse_parameters_pkt_2(data):
    fmt = '>BBHHHBIBIHHH7sB29s'
    fmt_names = ['cmd_id',
                 'packet_id',
                 'max_temperature_alert',
                 'min_humidity_alert',
                 'max_humidity_alert',
                 'unknown_1',
                 'setting_time',
                 'record_type',
                 'start_time',
                 'test_records',
                 'unknown_2',
                 'CO2_alert',
                 'unknown_3',
                 'flags',
                 'unknown']
    #print(data)
    ar = struct.unpack(fmt, bytearray(data))
    #print([hex(i) for i in ar])
    fields = dict(zip(fmt_names, ar))

    
    fields['setting_time'] = str(datetime.datetime.utcfromtimestamp(fields['setting_time']))
    if fields['record_type'] == 0:
        fields['record_type']='manually'
    else:
        fields['record_type']='immediately'
    fields['start_time'] = str(datetime.datetime.utcfromtimestamp(fields['start_time']))

    fields['max_temperature_alert'] = (fields['max_temperature_alert'] - 400)/10
    #fields['max_temp'] = (fields['max_temp'] - 400)/10

    fields['min_humidity_alert'] = fields['min_humidity_alert']/10
    fields['max_humidity_alert'] = fields['max_humidity_alert']/10

    fields['unknown'] = [hex(i) for i in fields['unknown']]
    fields['unknown_3'] = [hex(i) for i in fields['unknown_3']]
    return fields
    
def get_seting_parameters(dev):
    ret = ht_device.send_request(dev, ht_device.Request.SETTING_PARAMETERS)
    status = parse_parameters_pkt_1(ret)
    if status['cmd_id'] != 6:
        raise ValueError('Wrong returned cmd_id {} != {}'.format(status['cmd_id'], ht_device.Request.SETTING_PARAMETERS))
    if status['packet_id'] != 0:
        raise ValueError('Wrong returned packet_id {} != 0'.format(status['packet_id']))

    print(status)
    ret = ht_device.send_request(dev, ht_device.Request.SETTING_PARAMETERS)
    status = parse_parameters_pkt_2(ret)

    if status['cmd_id'] != 6:
        raise ValueError('Wrong returned cmd_id {} for second request'.format(status['cmd_id']))
    if status['packet_id'] != 1:
        raise ValueError('Wrong returned packet_id {} != 1'.format(status['packet_id']))

    
    print(status)    
    return status

def _format_parameters_text(status):
    #print(status)
    result = '#{}({}): T={} RH={} CO2={}'.format(
        status['record'],
        status['time'],
        status['temperature'],
        status['RH'],
        status['CO2'])
    return result
        
# def _format_status_table(status):
#     #print(status)
#     result = '#{:0>5d}    {:20s}   {:>2.1f}C   {:>2.1f}%  {:>4}'.format(
#         status['record'],
#         status['time'],
#         status['temperature'],
#         status['RH'],
#         status['CO2'])
#     return result

# def _format_status_csv(status):
#     #print(status)
#     result = '{},{},{},{},{}'.format(
#         status['record'],
#         status['time'],
#         status['temperature'],
#         status['RH'],
#         status['CO2'])
#     return result

format_parameters= {
    'text'  : _format_parameters_text}
    
    
    
def main():
    try:
        dev = ht_device.open_device()
        status = get_seting_parameters(dev)
    except ValueError as e:
        print(e)
        return
    #print(format_status['table'](status))

if __name__ == '__main__':
    main()

    #assert format_status['text'](parse_status([0x05,0x5c,0x96,0x2f,0x6c,0x01,0x65,0x02,0x69,0x00,0xef,0x01,0x90,0x03,0x20,0x00,0x64,0x03,0xb6,0xb0,0x03,0x00,0x07,0xd0,0x01,0xf1,0x00,0x00,0x07,0xd0,0x00,0x02])) == '#357(2019-03-23 13:06:52): T=21.7 RH=23.9 CO2=497'
