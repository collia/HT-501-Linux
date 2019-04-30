#! /usr/bin/python3

import ht_status
import ht_device
import argparse
import time

def _init_paratemers():
    parser = argparse.ArgumentParser(description='Get information from CO2 meter.')
    parser.add_argument('-M', '--monitor',  action='store_true',
                        help='continiusly read and prints device values')
    parser.add_argument('-p', '--period',  default=1,
                        help='time between reads')

    parser.add_argument('-o', '--output',choices=['text', 'table', 'csv', 'json'],
                        default='text',
                        help='output format')

    args = parser.parse_args()
    #print(args)
    #print("m={} p={}".format(args.monitor, args.period))

    if args.monitor:
        return (int(args.period), args.output)
    else:
        return  (None, args.output)
    

def main():
    period, mode = _init_paratemers()
    try:
        dev = ht_device.open_device()
        if period != None:
            while True:
                status = ht_status.get_status(dev)
                print(ht_status.format_status[mode](status))
                time.sleep(period)
        else:
            status = ht_status.get_status(dev)
            print(ht_status.format_status[mode](status))    
    except ValueError as e:
        print(e)
        return
    

if __name__ == '__main__':
    main()

