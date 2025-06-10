#!/usr/bin/env python
# -*- encoding=iso-8859-2 -*-
# Written by Wojciech M. Zabołotny <wzab01@gmail.com>
# Copyleft 2024 W.M. Zabołotny
# This is a PUBLIC DOMAIN code
#
# The code is somehow based on:
# https://stackoverflow.com/questions/44290837/how-to-interact-with-usb-device-using-pyusb

import usb.core
import usb.util
import struct
import time
import signal

# Globals are kept in a single variable 
# That trick enables accessing them from 
# various routines...

class glbs:
  pass
glb = glbs()

glb.runflag = True

# find our device
dev = usb.core.find(idVendor=0x303a, idProduct=0x4001)

# was it found?
if dev is None:
    raise ValueError('Device not found')

# find our interface
for cfg in dev:
   for intf in cfg:
      if usb.util.get_string(dev,intf.iInterface) == 'WZ1':
         # This is our interface
         my_intf = intf
         my_intfn = intf.bInterfaceNumber

# try default conf
print("trying to claim interface")
try:
    usb.util.claim_interface(dev, my_intfn)
    print("claimed interface")
except usb.core.USBError as e:
    print("Error occurred claiming " + str(e))
    sys.exit("Error occurred on claiming")

glb.eps=my_intf.endpoints()

def on_sig_int(sig,frame):
    glb.runflag = False

signal.signal(signal.SIGINT, on_sig_int)

epin=glb.eps[1]
epout=glb.eps[0]
epin2=glb.eps[3]
epout2=glb.eps[2]

epout.write(b"CPU:30;RAM:20;DISK:10")
res=epin.read(1000)
print(res.tobytes())
epout2.write(b"CPU:40;RAM:50;DISK:30")
res=epin2.read(1000)
print(res.tobytes())

