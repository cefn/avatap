from agnostic import report_collect, report_import

report_import("faces.font_5x7")
from faces.font_5x7 import font

report_import("st7920")
from st7920 import Screen

report_import("machine")
from machine import Pin

screen = Screen(slaveSelectPin=Pin(15))

def plotter(x, y):
    screen.plot(x, y)

screen.clear()
font.draw_line("Hello World", plotter)
screen.redraw()
report_collect()

report_import("milecastles")
report_import("boilerplate")
report_import("engines")
report_import("engines.console")
report_import("stories.senhouse")
from stories.senhouse import story

from regimes.console import ConsoleSiteEmulator

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