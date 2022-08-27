"""
`picoed.display`
====================================================

MicroPython driver for the Pico:ed matrix display.

"""

import utime
from micropython import const
from .is31fl3731 import IS31FL3731

OFFSET_BYTES = const(2)
FONT_BYTES = const(7)
BLANK_FONT = b'\x7f\x41\x41\x41\x41\x41\x7f\x00'
FONTS_BIN = '/picoed/fonts.bin'


class Image():
    """An image to show on the Pico:ed LED display."""

    NO = b"\x00\x00\x00\x00\x00\x41\x22\x14\x08\x14\x22\x41\x00\x00\x00\x00\x00"
    SQUARE = b"\x00\x00\x00\x00\x00\x00\x3E\x22\x22\x22\x3E\x00\x00\x00\x00\x00\x00"
    RECTANGLE = b"\xFF\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\xFF"
    RHOMBUS = b"\x00\x00\x00\x00\x00\x08\x14\x22\x41\x22\x14\x08\x00\x00\x00\x00\x00"
    TARGET = b"\x00\x00\x00\x00\x00\x08\x1C\x36\x63\x36\x1C\x08\x00\x00\x00\x00\x00"
    CHESSBOARD = b"\x2A\x55\x2A\x55\x2A\x55\x2A\x55\x2A\x55\x2A\x55\x2A\x55\x2A\x55\x2A"
    HAPPY = b"\x00\x00\x00\x00\x10\x20\x46\x40\x40\x40\x46\x20\x10\x00\x00\x00\x00"
    SAD = b"\x00\x00\x00\x00\x40\x22\x12\x10\x10\x10\x12\x22\x40\x00\x00\x00\x00"
    YES = b"\x00\x00\x00\x00\x00\x00\x08\x10\x20\x10\x08\x04\x02\x00\x00\x00\x00"
    HEART = b"\x00\x00\x00\x00\x00\x0E\x1F\x3F\x7E\x3F\x1F\x0E\x00\x00\x00\x00\x00"
    TRIANGLE = b"\x00\x00\x40\x60\x50\x48\x44\x42\x41\x42\x44\x48\x50\x60\x40\x00\x00"
    CHAGRIN = b"\x00\x00\x00\x00\x22\x14\x08\x40\x40\x40\x08\x14\x22\x00\x00\x00\x00"
    SMILING_FACE = b"\x00\x00\x00\x00\x00\x06\x36\x50\x50\x50\x36\x06\x00\x00\x00\x00\x00"
    CRY = b"\x60\x70\x70\x38\x02\x02\x64\x50\x50\x50\x64\x02\x02\x38\x70\x70\x60"
    DOWNCAST = b"\x00\x00\x00\x02\x0A\x11\x08\x40\x40\x40\x08\x11\x0A\x02\x00\x00\x00"
    LOOK_RIGHT = b"\x00\x00\x00\x00\x00\x00\x00\x26\x2F\x06\x00\x06\x0F\x06\x00\x00\x00"
    LOOK_LEFT = b"\x00\x00\x00\x06\x0F\x06\x00\x06\x2F\x26\x00\x00\x00\x00\x00\x00\x00"
    TONGUE = b"\x00\x00\x00\x00\x04\x12\x14\x70\x70\x70\x16\x16\x00\x00\x00\x00\x00"
    PEEK_RIGHT = b"\x00\x00\x04\x04\x04\x0C\x0C\x40\x40\x40\x04\x04\x04\x0C\x0C\x00\x00"
    PEEK_LEFT = b"\x00\x00\x0C\x0C\x04\x04\x04\x40\x40\x40\x0C\x0C\x04\x04\x04\x00\x00"
    TEAR_EYES = b"\x00\x00\x00\x06\x7F\x06\x20\x40\x40\x40\x20\x06\x7F\x06\x00\x00\x00"
    PROUD = b"\x01\x07\x0F\x0F\x0F\x0F\x47\x41\x41\x41\x27\x0F\x0F\x0F\x0F\x07\x01"
    SNEER_LEFT = b"\x00\x00\x00\x0C\x08\x0C\x2C\x40\x40\x40\x2C\x08\x0C\x0C\x00\x00\x00"
    SNEER_RIGHT = b"\x00\x00\x00\x0C\x0C\x08\x2C\x40\x40\x40\x2C\x0C\x08\x0C\x00\x00\x00"
    SUPERCILIOUS_LOOK = b"\x00\x00\x00\x0E\x0C\x0E\x00\x20\x20\x20\x00\x0E\x0C\x0E\x00\x00\x00"
    EXCITED = b"\x60\x70\x70\x3E\x01\x06\x30\x50\x50\x50\x30\x06\x01\x3E\x70\x70\x60"

    def __new__(cls, value=None):
        if value is not None and isinstance(value, str):
            data = []
            for y in range(7):
                if y < 6:
                    if value[(y + 1) * 18 - 1] != ":":
                        raise ValueError('Each line of data must be separated with a ":"')
                for x in range(17):
                    data.append([x, y, int(value[y * 18 + x])])
            return data
        else:
            return [[0, 0, 0]]


class Display(IS31FL3731):
    """Supports the Pico:ed display"""

    width = 17
    height = 7

    _current_frame = 0

    def _init(self, frames=None):
        super()._init(frames)
        with open(FONTS_BIN, 'rb') as f:
            self._fonts_offset = int.from_bytes(f.read(OFFSET_BYTES), 'little')  # 字库前两位是字模的地址偏移
            f.seek(OFFSET_BYTES)
            self._fonts = f.read(self._fonts_offset - OFFSET_BYTES).decode('utf-8')  # 字库的字典，用于查找字模
    
    def _find_font(self, value, f):
        if not self._fonts:
            return None

        index_font = self._fonts.find(value)
        if index_font < 0:
            return None

        seek_font_offset = self._fonts_offset + index_font * FONT_BYTES
        f.seek(seek_font_offset)  # 移动到字模的地址
        font_bytes = f.read(FONT_BYTES)
        # 为了对齐每个字模的长度，部分字模前后有 b'\x00' 填充，这里去掉
        return font_bytes.strip(b'\x00')

    @staticmethod
    def pixel_addr(x, y):
        """Translates an x, y coordinate to a pixel index."""
        if x > 8:
            x = 17 - x
            y += 8
        else:
            y = 7 - y
        return x * 16 + y

    def _draw(self, buffer, brightness):
        self._current_frame = 0 if self._current_frame else 1
        self.frame(self._current_frame, show=False)
        self.fill(0)
        for x in range(self.width):
            col = buffer[x]
            for y in range(self.height):
                bit = 1 << y & col
                if bit:
                    self.pixel(x, y, brightness)
        self.frame(self._current_frame, show=True)

    def clear(self):
        """Clears the LED display."""
        self.fill(0)

    def scroll(self, value, brightness=30, fonts=None, fps=15):
        """Scrolls a number or text on the LED display."""
        if brightness < 0:
            brightness = 0
        if brightness > 255:
            brightness = 255

        text_buf = bytearray()
        buf = bytearray(self.width)

        with open(FONTS_BIN, 'rb') as f:
            for char in str(value):
                if char == " ":
                    text_buf += b"\x00" * 4 # 空格
                else:
                    font = self._find_font(char, f)
                    if not font and fonts: # 缺字时查找自定义的字库
                        font = fonts[char]
                    if font:
                        text_buf += font + b'\x00' # 字间距 1 列
                    else:
                        text_buf += BLANK_FONT # 缺字（空白字）

        if len(text_buf) <= self.width:
            for buf_index in range(len(text_buf)):
                buf[buf_index] = text_buf[buf_index]
            self._draw(buf, brightness)
        else:
            frame_time = 1000 // fps
            for text_index in range(len(text_buf) + self.width):
                start = utime.ticks_ms()
                for buf_index in range(len(buf) - 1):
                    buf[buf_index] = buf[buf_index + 1]
                if text_index < len(text_buf):
                    buf[len(buf) - 1] = text_buf[text_index]
                self._draw(buf, brightness)
                # 帧率控制
                idle_time = frame_time - utime.ticks_diff(utime.ticks_ms(), start)
                if idle_time > 0:
                    utime.sleep_ms(int(idle_time))

    def show(self, value, brightness=30):
        """Shows images, letters or digits on the LED display."""
        if isinstance(value, (int, float, str)):
            self.scroll(value, brightness)

        elif isinstance(value, bytes):
            self._draw(value, brightness)
        else:
            self._current_frame = 0 if self._current_frame else 1
            self.frame(self._current_frame, show=False)
            self.fill(0)
            for pixel in value:
                self.pixel(pixel[0], pixel[1], int(pixel[2] * 255 / 9))
            self.frame(self._current_frame, show=True)
