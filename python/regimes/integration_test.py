from faces.font_5x7 import font
from st7920 import Screen
from mfrc522 import MFRC522
from machine import Pin,SPI
import agnostic

agnostic.collect()

spi = SPI(1, baudrate=1800000, polarity=0, phase=0)
spi.init()
agnostic.collect()

rdr = MFRC522(spi=spi, gpioRst=0, gpioCs=2)
agnostic.collect()

screen = Screen(spi=spi, slaveSelectPin=Pin(15))
agnostic.collect()

def plotter(x,y):
    if x < 128 and y < 64:
        screen.plot(x,y)
    else:
        print("Out of bounds {},{}".format(x,y))

def show(para):
    screen.clear()
    font.draw_para(para, plotter)
    screen.redraw()

def run():
    show("Hello world")
    while True:
        agnostic.collect()
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                para = "ID is\n0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                show(para)