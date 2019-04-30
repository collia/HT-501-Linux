#! /usr/bin/python3

import struct
import datetime
import ht_device
import json

def parse_parameters_pkt_1(data):
    fmt = '>BBB10s38s2sHB3sH'
    fmt_names = ['cmd_id',
                 'packet_id',
                 'address',
                 'serial',
                 'test_name',
                 'unknown_1',
                 'total_records',
                 'record_interval',
                 'unknown_2',
                 'min_temperature_alert'
                 
    ]
    #print(data)
    ar = struct.unpack(fmt, bytearray(data))
    #print([hex(i) for i in ar])
    fields = dict(zip(fmt_names, ar))

    try:
        fields['serial'] = fields['serial'].decode('ascii')
    except ValueError as e:
        fields['serial'] = [hex(i) for i in fields['serial']]
    fields['test_name'] = fields['test_name'].decode('utf-16')
    fields['unknown_1'] = [hex(i) for i in fields['unknown_1']]
    fields['unknown_2'] = [hex(i) for i in fields['unknown_2']]
    fields['min_temperature_alert'] = (fields['min_temperature_alert'] - 400)/10
    
    return fields

def parse_parameters_pkt_2(data):
    fmt = '>BBHHHBIBIH2sH7sB29s'
    fmt_names = ['cmd_id',
                 'packet_id',
                 'max_temperature_alert',
                 'min_humidity_alert',
                 'max_humidity_alert',
                 'unknown_3',
                 'setting_time',
                 'record_type',
                 'start_time',
                 'test_records',
                 'unknown_4',
                 'CO2_alert',
                 'unknown_5',
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

    fields['min_humidity_alert'] = fields['min_humidity_alert']/10
    fields['max_humidity_alert'] = fields['max_humidity_alert']/10

    fields['unknown'] = [hex(i) for i in fields['unknown']]

    fields['unknown_4'] = [hex(i) for i in fields['unknown_4']]
    fields['unknown_5'] = [hex(i) for i in fields['unknown_5']]
    return fields
    
def _get_parameters(dev, parameters_type):
    ret = ht_device.send_request(dev, parameters_type)
    status_1 = parse_parameters_pkt_1(ret)

    if status_1['cmd_id'] != parameters_type:
        raise ValueError('Wrong returned cmd_id {} != {}'.format(status_1['cmd_id'], parameters_type))
    if status_1['packet_id'] != 0:
        raise ValueError('Wrong returned packet_id {} != 0'.format(status_1['packet_id']))

    #print(status_1)
    ret = ht_device.send_request(dev, parameters_type)
    status_2 = parse_parameters_pkt_2(ret)

    if status_2['cmd_id'] != parameters_type:
        raise ValueError('Wrong returned cmd_id {} for second request'.format(status_2['cmd_id']))
    if status_2['packet_id'] != 1:
        raise ValueError('Wrong returned packet_id {} != 1'.format(status_2['packet_id']))
    #print(status_2)
    status_1.update(status_2)
    del status_1['cmd_id']
    del status_1['packet_id']
    return status_1

def get_seting_parameters(dev):
    return _get_parameters(dev, ht_device.Request.SETTING_PARAMETERS)

def get_record_parameters(dev):
    return _get_parameters(dev, ht_device.Request.RECORD_PARAMETERS)


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
def _format_status_json(status):
    return json.dumps(status)

format_parameters= {
    'text'  : _format_parameters_text,
    'json'   : _format_status_json}
    
    
def main():
    try:
        dev = ht_device.open_device()
        print("Setting parameters:")
        status = get_seting_parameters(dev)
        print(format_parameters['json'](status))

        print("Recorded parameters:")
        status = get_record_parameters(dev)
        print(format_parameters['json'](status))
        
    except ValueError as e:
        print(e)
        return
    #print(format_status['table'](status))

if __name__ == '__main__':
    main()

    #assert format_status['text'](parse_status([0x05,0x5c,0x96,0x2f,0x6c,0x01,0x65,0x02,0x69,0x00,0xef,0x01,0x90,0x03,0x20,0x00,0x64,0x03,0xb6,0xb0,0x03,0x00,0x07,0xd0,0x01,0xf1,0x00,0x00,0x07,0xd0,0x00,0x02])) == '#357(2019-03-23 13:06:52): T=21.7 RH=23.9 CO2=497'
