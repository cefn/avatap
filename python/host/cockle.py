import loader
loader.loadDisplay()

from machine import SPI, Pin
from st7920 import Screen
from faces.font_5x7 import font as smallFont
bigFont = smallFont

#TODO CH sanitise screen++ creation into loader.loadDisplay(), possibly also CockleRFID creation
# prepare screen
screen = Screen(spi=SPI(-1, baudrate=1800000, polarity=0, phase=0, miso=Pin(16), mosi=Pin(5), sck=Pin(4)),
                slaveSelectPin=None, resetDisplayPin=None)
blackPlotter = screen.create_plotter(True)
whitePlotter = screen.create_plotter(False)
smallFont.draw_line(b"Powering Up!", x=32, y=24, plotter=blackPlotter)
screen.redraw()

loader.loadOther()
loader.loadStory(loader.storyUid)

from mfrc522 import MFRC522
#from faces.font_timB14 import font as bigFont
from vault import BankVault
from engines import Engine, dictToCard, cardToDict
from host import Host
from milecastles import Box

class CockleRfid(BankVault):

    def readCard(self, cardUid, unselect=True):
        try:
            cardDict = self.readJson(cardUid, unselect)
            card = dictToCard(cardUid, cardDict)
            return card
        except AssertionError as e:
            return None

    def writeCard(self, card, unselect=True):
        return self.writeJson( cardToDict(card), card.uid, unselect)

def prepareHost(story, boxUid):
    # prepare reader
    readerSpi = SPI(1, baudrate=1800000, polarity=0, phase=0)
    readerSpi.init()
    reader = MFRC522(spi=readerSpi, gpioRst=None, gpioCs=2)
    # wrap hardware in platform-specific API and attach story
    rfid = CockleRfid(reader)
    box = story._get_table(Box)[boxUid]
    engine = Engine(box=box)
    engine.registerStory(story)
    powerPin = Pin(15, Pin.OUT)
    powerPin.value(0)

    # launch box host
    return Host(
        story=story,
        box=box,
        engine=engine,
        screen=screen,
        rfid=rfid,
        smallFont=smallFont,
        bigFont=bigFont,
        blackPlotter=blackPlotter,
        whitePlotter=whitePlotter,
        powerPin=powerPin
    )