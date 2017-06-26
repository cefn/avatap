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

screenMiso = Pin(16)
screenMosi = Pin(5)
screenSck = Pin(4)
screenSpi = SPI(-1, baudrate=1800000, polarity=0, phase=0, miso=screenMiso, mosi=screenMosi, sck=screenSck)
agnostic.collect()

rdr = MFRC522(spi=readerSpi, gpioRst=None, gpioCs=2) # equivalent to reset D3 (was CableSelect D4)
agnostic.collect()

screen = Screen(spi=screenSpi, slaveSelectPin=None, resetDisplayPin=None) # GPIO15 alleged SS in hardware driver! ( https://tttapa.github.io/ESP8266/Chap04%20-%20Microcontroller.html )
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