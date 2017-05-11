from agnostic import collect, report_collect, report_import

report_import("faces.font_5x7")
from faces.font_5x7 import font

report_import("vault")

report_import("st7920")
from st7920 import Screen
report_import("machine")
from machine import Pin, SPI

report_import("mfrc522")
from mfrc522 import MFRC522

spi = SPI(1, baudrate=1800000, polarity=0, phase=0)
spi.init()
collect()

rdr = MFRC522(spi=spi, gpioRst=0, gpioCs=2)
collect()

screen = Screen(spi=spi, slaveSelectPin=Pin(15))
collect()

def plotter(x, y):
    screen.plot(x, y)

def show(msg):
    screen.clear()
    font.draw_para(msg, plotter)
    screen.redraw()
    collect()

startSack = {
    "epona": False,
    "mars": False,
    "superhorse": False,
    "eponapoints": 0,
    "marspoints": 0,
    "hours": 0,
}

incrementKey = "eponapoints"

# cards have 16 sectors * 4 blocks/sector * 16 bytes/block = 1024 bytes.
# [theoretical] Data transfer of 106 kbit/s
# Anti-collision handles multiple cards present
# Write endurance 100.000 cycles