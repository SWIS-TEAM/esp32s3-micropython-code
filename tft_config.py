# tft_config.py
from machine import Pin, SPI
import st7789py as st7789

# Your display pins (SPI3)
def config(mode=None):
    spi = SPI(
        2,                             # SPI3
        baudrate=80_000_000,
        polarity=1,
        phase=1,
        sck=Pin(40),
        mosi=Pin(45),
    )

    return st7789.ST7789(
        spi,
        240,
        320,
        reset=Pin(39, Pin.OUT),
        cs=Pin(42, Pin.OUT),
        dc=Pin(41, Pin.OUT),
        backlight=Pin(5, Pin.OUT),
        rotation=0,
    )

WIDE = 0  # Used by example for optional orientation logic
