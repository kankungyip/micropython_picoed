# SPDX-FileCopyrightText: Copyright ELECFREAKS
# SPDX-License-Identifier: MIT

"""
`picoed.led`
====================================================

MicroPython driver for the Pico:ed built-in LED.

"""


class Led:
    """Supports the Pico:ed built-in LED"""

    def __init__(self, pin):
        self._pin = pin
        self.on = self._pin.on
        self.off = self._pin.off
        self.toggle = self._pin.toggle
