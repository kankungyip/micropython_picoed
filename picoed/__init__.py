"""
`picoed`
====================================================

The Pico:ed build-in modules for MicroPython.

"""

from machine import I2C, Pin
from .display import Display, Image
from .button import Button
from .led import Led
from .music import Music

I2C0_SDA = Pin(0)
I2C0_SCL = Pin(1)
BUTTON_A = Pin(20, Pin.IN, Pin.PULL_UP)
BUTTON_B = Pin(21, Pin.IN, Pin.PULL_UP)
LED = Pin(25, Pin.OUT)
BUZZER = Pin(3, Pin.OUT)

i2c = I2C(0, scl=I2C0_SCL, sda=I2C0_SDA)
display = Display(i2c)

button_a = Button(BUTTON_A)
button_b = Button(BUTTON_B)
led = Led(LED)
music = Music(BUZZER)
