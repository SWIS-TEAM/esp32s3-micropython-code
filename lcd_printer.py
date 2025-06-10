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
        self.colors = [
            st7789.RED, st7789.GREEN, st7789.BLUE, st7789.YELLOW,
            st7789.CYAN, st7789.MAGENTA]

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
        """
        Print the title "Usage Monitor" on the TFT display.
        :param color: The color of the title text (default is white).
        :return: None
        """

        self.tft.fill(st7789.BLACK)
        # Center "Activity" and "Monitor" on separate lines
        screen_width = self.tft.physical_width
        text1 = "Usage"
        text2 = "Monitor"
        # Calculate text width using font_big.WIDTH and len
        text1_width = len(text1) * font_big.WIDTH
        text2_width = len(text2) * font_big.WIDTH
        x1 = (screen_width - text1_width) // 2
        x2 = (screen_width - text2_width) // 2
        self.print_text(text1, x1, self.FIRST_COLUMN_X, color, font=font_big)
        self.print_text(text2, x2, self.FIRST_COLUMN_X + font_big.HEIGHT + 4, 
                        color, font=font_big)
        
    def clear_display_under_title(self):
        """
        Clear the display area under the title.
        This method fills the area below the title with black color.
        :return: None
        """
        screen_height = self.tft.physical_height
        screen_width = self.tft.physical_width
        title_height = 2 * (font_big.HEIGHT + 4)
        # Fill the area below the title with black color
        self.tft.fill_rect(0, title_height, screen_width, 
                           screen_height - title_height, st7789.BLACK)


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

            
    def print_usage(self, usage_dict):
        """
        Display CPU, RAM, and DISK usage on the TFT display.
        :param usage_dict: A dictionary containing usage data with keys "User", "System", "Idle", etc.
        """

        # Clear the display area under the title
        self.clear_display_under_title()

        # Do not clear the whole screen; only clear rectangles where values are printed
        screen_width = self.tft.physical_width
        order = ["User", "System", "Idle", "RAM_USED", "OUT_OF"]
        max_height = 0
        for idx, key in enumerate(order):
            if key in usage_dict:
                value = usage_dict[key]
                color = self.colors[idx % len(self.colors)]
                y = self.FIRST_ROW_Y + idx * (font_schmol.HEIGHT * 2 + 8)
                max_height += y
                key_text = f"{key}:"
                value_text = f"{value}"
                key_width = len(key_text) * font_schmol.WIDTH
                value_width = len(value_text) * font_schmol.WIDTH
                key_x = (screen_width - key_width) // 2
                value_x = (screen_width - value_width) // 2

                self.print_text(key_text, 
                    key_x, 
                    y, 
                    color, 
                    font=font_schmol)
                self.print_text(value_text, 
                    value_x, 
                    y + font_schmol.HEIGHT + 2, 
                    color, 
                    font=font_schmol)

def main():
    printer = LCDPrinter()
    while True:
        cpu = random.randint(45, 55)
        ram = random.randint(17, 23)
        disk = random.randint(8, 12)
        printer.print_usage({
            "User": f"{cpu}%",
            "System": f"{ram}%",
            "Idle": f"{disk}%",
            "RAM_USED": f"{random.randint(10, 30)}%",
            "OUT_OF": f"{random.randint(1, 5)}GB"
        })
        time.sleep(3)

if __name__ == "__main__":
    main()