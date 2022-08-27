"""
`picoed.button`
====================================================

MicroPython driver for the Pico:ed built-in buttons.

"""


class Button():
    """"Supports the Pico:ed button"""

    def __init__(self, pin):
        self._pin = pin
        self._last_pressed = False

    def is_pressed(self):
        """Returns True when the key is pressed"""
        return not self._pin.value()

    def was_pressed(self):
        """Returns True when the key was pressed"""
        if not self._pin.value() and not self._last_pressed:
            self._last_pressed = True
            return True
        if self._pin.value():
            self._last_pressed = False
        return False
