#! /usr/bin/python3

import usb.core
import enum

class Request(enum.Enum):
     STATUS = 5
     SETTING_PARAMETERS = 6
     RECORD_PARAMETERS = 3

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

def send_request(dev, request):
    if isinstance(request, Request):
        return dev.ctrl_transfer(0xa1, 1, 0x0100 + request.value, 0, 0x3d)
    else:
        raise ValueError('Wrong request type')

def main():
    try:
        dev = open_device()
        print(dev)
    except ValueError as e:
        print(e)
        return
    print(format_status(status))

if __name__ == '__main__':
    main()



