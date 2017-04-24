from faces.font_5x7 import font
from st7920 import Screen
from mfrc522 import MFRC522
from machine import Pin

rdr = MFRC522(0, 2, 4, 5, 14)
screen = Screen(slaveSelectPin=Pin(15))

def plotter(x,y):
    if x < 128 and y < 46:
        screen.plot(x,y)
    else:
        print("Out of bounds {},{}".format(x,y))

def run():
    while True:
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                para = "ID is\n0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                screen.clear()
                font.draw_para(para, plotter)
                screen.redraw()