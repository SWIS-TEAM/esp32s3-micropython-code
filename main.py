# MicroPython USB WZab1 module
# MIT license; Copyright (c) 2024 Wojciech Zabolotny
# Based on examples from 
# https://github.com/projectgus/micropython-lib/tree/feature/usbd_python/micropython/usb
# MIT license; Copyright (c) 2023 Paul Hamshere, 2023-2024 Angus Gratton
# Modified by Piotr Baprawski and Piotr Polnau for SWIS25L Project.

from micropython import schedule
from usb.device.core import Interface, Buffer
from lcd_printer import LCDPrinter
import usb.device



_EP_IN_FLAG = const(1 << 7)
NUM_ITFS = const(1)
NUM_EPS = const(4)  # 4 endpoints (2 IN and 2 OUT)


class WZab1Interface(Interface):
    """
    Base class to implement a USB WZab1 device in Python.
    This class handles USB transfers and provides a simple interface for
    sending and receiving data over USB.
    """
    def __init__(self,rxlen=3000, txlen=3000):
        super().__init__()
        self.ep_out = None # RX direction (host to device)
        self.ep_in = None # TX direction (device to host)
        self.ep_c_out = None # RX direction (host to device)
        self.ep_c_in = None # TX direction (device to host)
        self._rx = Buffer(rxlen)
        self._tx = Buffer(txlen)
        self._rx_c = Buffer(rxlen)
        self._tx_c = Buffer(txlen)
        self.lcd_printer = LCDPrinter()
    
    def _tx_xfer(self):
        # Keep an active IN transfer to send data to the host, whenever
        # there is data to send.
        if self.is_open() and not self.xfer_pending(self.ep_in) and self._tx.readable():
            self.submit_xfer(self.ep_in, self._tx.pend_read(), self._tx_cb)

    def _tx_cb(self, ep, res, num_bytes):
        #print(num_bytes,self._tx._n)
        if res == 0:
            self._tx.finish_read(num_bytes)
        self._tx_xfer()

    def _rx_xfer(self):
        # Keep an active OUT transfer to receive messages from the host
        if self.is_open() and not self.xfer_pending(self.ep_out) and self._rx.writable():
            self.submit_xfer(self.ep_out, self._rx.pend_write(), self._rx_cb)

    def _rx_cb(self, ep, res, num_bytes):
        #print("rx:"+str(num_bytes)+"\n")
        if res == 0:
            self._rx.finish_write(num_bytes)
            schedule(self._on_rx, ep)
        self._rx_xfer()

    def _tx_c_xfer(self):
        # Keep an active IN transfer to send data to the host, whenever
        # there is data to send.
        if self.is_open() and not self.xfer_pending(self.ep_c_in) and self._tx_c.readable():
            self.submit_xfer(self.ep_c_in, self._tx_c.pend_read(), self._tx_c_cb)

    def _tx_c_cb(self, ep, res, num_bytes):
        #print(num_bytes,self._tx_c._n)
        if res == 0:
            self._tx_c.finish_read(num_bytes)
        self._tx_c_xfer()

    def _rx_c_xfer(self):
        # Keep an active OUT transfer to receive messages from the host
        if self.is_open() and not self.xfer_pending(self.ep_c_out) and self._rx_c.writable():
            self.submit_xfer(self.ep_c_out, self._rx_c.pend_write(), self._rx_c_cb)

    def _rx_c_cb(self, ep, res, num_bytes):
        # Same here
        if res == 0:
            self._rx_c.finish_write(num_bytes)
            schedule(self._on_rx_c, ep)
        self._rx_c_xfer()
   
    def _on_rx(self, ep):
        # Receive received data. Called via micropython.schedule, outside of the USB callback function.
        m = self._rx.pend_read()
        dt = bytes(m)        
        self._rx.finish_read(len(m))

        # Extract the data and print it on the LCD
        try:
            parts = dt.decode('utf-8').split(';')
            usage_dict = {}
            for part in parts:
                part = part.strip()
                key, value = part.split(':')
                key = key.strip()
                value = value.strip()
                usage_dict[key] = value
            self.lcd_printer.print_usage(usage_dict)

            # Send a response back to the host
            m = self._tx.write(b"Data received successfully")
            self._tx_xfer()
        except (ValueError, IndexError):
            # If the data is not in the expected format, send an error message
            m = self._tx.write(b"Error: Invalid data format")
            self._tx_xfer()
        

    def _on_rx_c(self, ep):
        # Receive received data. Called via micropython.schedule, outside of the USB callback function.
        m = self._rx_c.pend_read()
        dt = bytes(m)        
        self._rx_c.finish_read(len(m))
        # check if data is correctly formatted
        try:
            parts = dt.decode('utf-8').split(';')
            usage_dict = {}
            for part in parts:
                part = part.strip()
                key, value = part.split(':')
                key = key.strip()
                value = value.strip()
                usage_dict[key] = value
            self.lcd_printer.print_usage(usage_dict)

            # Send a response back to the host
            m = self._tx_c.write(b"Data received successfully")
            self._tx_c_xfer()
        except (ValueError, IndexError):
            # If the data is not in the expected format, send an error message
            m = self._tx_c.write(b"Error: Invalid data format")
            self._tx_c_xfer()

    def desc_cfg(self, desc, itf_num, ep_num, strs):
        strs.append("WZ1")
        desc.interface(itf_num, 4, iInterface = len(strs)-1)
        self.ep_out = ep_num
        self.ep_in = (ep_num) | _EP_IN_FLAG
        self.ep_c_out = ep_num+1
        self.ep_c_in = (ep_num+1) | _EP_IN_FLAG
        desc.endpoint(self.ep_out,"bulk",64,0)
        desc.endpoint(self.ep_in,"bulk",64,0)
        desc.endpoint(self.ep_c_out,"bulk",64,0)
        desc.endpoint(self.ep_c_in,"bulk",64,0)
        
    def num_itfs(self):
        return NUM_ITFS
        
    def num_eps(self):
        return NUM_EPS

    def on_open(self):
        super().on_open()

        # kick off any transfers that may have queued while the device was not open
        self._tx_xfer()
        self._rx_xfer()
        self._tx_c_xfer()
        self._rx_c_xfer()


if __name__ == "__main__":
    wz = WZab1Interface()
    usb.device.get().init(wz, builtin_driver=True)
