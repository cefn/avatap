import agnostic
from mfrc522 import MFRC522
agnostic.collect()
from st7920 import Screen
agnostic.collect()
from faces.font_5x7 import font
agnostic.collect()
from machine import Pin,SPI
agnostic.collect()

readerSpi = SPI(1, baudrate=1800000, polarity=0, phase=0)
readerSpi.init()
agnostic.collect()

"""
screenMiso = Pin(12, Pin.IN)
screenMosi = Pin(13, Pin.OUT)
screenSck = Pin(14, Pin.OUT)
"""

"""
screenMiso = Pin(12)
screenMosi = Pin(13)
screenSck = Pin(14)
screenSpi = SPI(-1, baudrate=1800000, polarity=0, phase=0, miso=screenMiso, mosi=screenMosi, sck=screenSck)
"""

screenSpi = readerSpi
agnostic.collect()

rdr = MFRC522(spi=readerSpi, gpioRst=0, gpioCs=2) # equivalent to reset D3 and CableSelect D4
agnostic.collect()

screen = Screen(spi=screenSpi, slaveSelectPin=Pin(15), resetDisplayPin=Pin(5))
agnostic.collect()

def plotter(x,y):
    if x < 128 and y < 64:
        screen.plot(x,y, set=True)
    else:
        print("Out of bounds {},{}".format(x,y))

def show(para):
    print("Showing...")
    print(para)
    screen.clear()
    font.draw_para(para, plotter)
    screen.redraw()

def run():
    show(b"Hello world")
    while True:
        agnostic.collect()
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                para = b"ID is\n0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                show(para)