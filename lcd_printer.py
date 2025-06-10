"""
hello.py
========

.. figure:: ../_static/hello.jpg
    :align: center

    Test for text_font_converter.

Writes "Hello!" in random colors at random locations on the Display.
https://www.youtube.com/watch?v=atBa0BYPAAc

.. note:: This example requires the following modules:

  .. hlist::
    :columns: 3

    - `st7789py`
    - `tft_config`
    - `vga2_bold_16x32`

"""

import random
import st7789py as st7789
import tft_config
from fonts import vga2_bold_16x32 as font_big
from fonts import vga2_16x16 as font_schmol
from fonts import vga1_bold_16x16 as font_pretty

import time


class LCDPrinter:
    """
    A class to handle printing to the LCD display.
    """
    def __init__(self, tft=None):
        if tft is None:
            tft = tft_config.config(tft_config.WIDE)
            tft.rotation(0)
        self.tft = tft
        self.FIRST_ROW_Y = 110
        self.FIRST_COLUMN_X = 10
        self.tft.fill(st7789.BLACK)  # Clear the screen initially
        self.print_title(st7789.WHITE)  # Print the title initially
        self.print_info("Waiting for data...", 10, self.FIRST_ROW_Y, 
                        st7789.WHITE, font=font_pretty)

   
    def print_text(self, text, x, y, color=st7789.WHITE, font=font_schmol):
        """
        Print text on the TFT display at specified coordinates.
        :param text: The text to print.
        :param x: The x-coordinate for the text.
        :param y: The y-coordinate for the text.
        :param color: The color of the text (default is white).
        :param font: The font to use for the text (default is font_schmol).
        :return: None
        """
        self.tft.text(font, text, x, y, color)

    def print_title(self, color=st7789.WHITE):
        self.tft.fill(st7789.BLACK)
        # Center "Activity" and "Monitor" on separate lines
        screen_width = self.tft.physical_width
        text1 = "Activity"
        text2 = "Monitor"
        # Calculate text width using font_big.WIDTH and len
        text1_width = len(text1) * font_big.WIDTH
        text2_width = len(text2) * font_big.WIDTH
        x1 = (screen_width - text1_width) // 2
        x2 = (screen_width - text2_width) // 2
        self.print_text(text1, x1, self.FIRST_COLUMN_X, color, font=font_big)
        self.print_text(text2, x2, self.FIRST_COLUMN_X + font_big.HEIGHT + 4, 
                        color, font=font_big)


    def print_info(self, text, x, y, color=st7789.WHITE, font=font_pretty):
        """
        Print information text on the TFT display, wrapping words to new lines if they would overflow.
        :param text: The text to print.
        :param x: The x-coordinate for the text.
        :param y: The y-coordinate for the text.
        :param color: The color of the text (default is white).
        :param font: The font to use for the text (default is font_schmol).
        :return: None
        """
        
        screen_width = self.tft.physical_width
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            # Predict width if we add this word
            test_line = (current_line + " " + word).strip()
            test_width = len(test_line) * font.WIDTH
            if test_width + x > screen_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " "
                current_line += word
        if current_line:
            lines.append(current_line)
        for i, line in enumerate(lines):
            self.tft.text(font, line, x, y + i * (font.HEIGHT + 2), color)

            
    def print_usage(self, cpu, ram, disk, msg=None):
        """
        Display CPU, RAM, and DISK usage on the TFT display.
        :param cpu: cpu usage.
        :param ram: ram usage.
        :param disk: disk usage.
        :param msg: additional message to print.
        """

        self.tft.fill(st7789.BLACK)
        # Center "Activity" and "Monitor" on separate lines
        self.print_title(st7789.WHITE)
        self.print_text(f" CPU: {cpu}%", 
                        self.FIRST_COLUMN_X, 
                        self.FIRST_ROW_Y, 
                        st7789.RED, 
                        font=font_schmol)
        
        self.print_text(f" RAM: {ram}%", 
                        self.FIRST_COLUMN_X, 
                        self.FIRST_ROW_Y + font_schmol.HEIGHT + 4, 
                        st7789.GREEN, 
                        font=font_schmol)
        self.print_text(f"DISK: {disk}%", 
                        self.FIRST_COLUMN_X, 
                        self.FIRST_ROW_Y + 2*(font_schmol.HEIGHT + 4), 
                        st7789.BLUE, 
                        font=font_schmol)
        if msg:
            self.print_info(msg, 10, self.FIRST_ROW_Y + 5*(font_schmol.HEIGHT + 4), st7789.WHITE, font=font_pretty)

def main():
    printer = LCDPrinter()
    while True:
        cpu = random.randint(45, 55)
        ram = random.randint(17, 23)
        disk = random.randint(8, 12)
        printer.print_usage(cpu, ram, disk, "Hello, World!")
        time.sleep(3)

if __name__ == "__main__":
    main()