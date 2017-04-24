from time import sleep
from agnostic import collect, report_collect, report_import
from math import floor
from os import urandom

report_import("faces.font_5x7")
from faces.font_5x7 import font

report_import("st7920")
from st7920 import Screen

report_import("machine")
from machine import Pin

screen = Screen(slaveSelectPin=Pin(15))

def plot(x, y):
    screen.plot(x, y)

screen.clear()
font.draw_line("Hello World", plot)
screen.redraw()
report_collect()

report_import("milecastles")
report_import("boilerplate")
report_import("engine")
report_import("consoleEngine")
report_import("stories.senhouse")
from stories.senhouse import story

from consoleEngine import ConsoleSiteEmulator

emulator = ConsoleSiteEmulator(story=story)
report_collect()

report_import("mfrc522")
from mfrc522 import MFRC522

rdr = MFRC522(0, 2, 4, 5, 14)

(stat, tag_type) = rdr.request(rdr.REQIDL)
if stat == rdr.OK:
    (stat, raw_uid) = rdr.anticoll()
    if stat == rdr.OK:
        para = "ID is\n0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
        screen.clear()
        font.draw_para(para, plotter)
        screen.redraw()

def log2approx(val):
    val = floor(val)
    approx = 0
    while val != 0:
        val &= ~ (1 << approx)
        approx = approx + 1
    return approx


def randint(minVal, maxVal=None):
    if (maxVal != None):
        return minVal + randint(maxVal - minVal)
    else:
        maxVal = minVal
    byteCount = (log2approx(maxVal) // 8) + 1  # each byte is 8 powers of two
    val = 0
    randBytes = urandom(byteCount)
    idx = 0
    while idx < len(randBytes):
        val |= randBytes[idx] << (idx * 8)
        idx += 1
    del randBytes
    return val % maxVal

def fuzz():
    emulator.handleInput("a")
    while True:
        emulator.handleInput(command=str(randint(1,4)))
        report_collect()
        sleep(1)