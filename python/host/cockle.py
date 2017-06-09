import loader
loader.loadAll()
from machine import SPI, Pin
from mfrc522 import MFRC522
from st7920 import Screen
from faces.font_5x7 import font as smallFont
bigFont = smallFont
#from faces.font_timB14 import font as bigFont
from vault import BankVault
from engines import Engine, dictToCard, cardToDict
from host import Host
from milecastles import Box

from stories.corbridge import story

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
    # prepare elements
    spi = SPI(1, baudrate=1800000, polarity=0, phase=0)
    spi.init()
    screen = Screen(spi=spi, slaveSelectPin=Pin(15))
    blackPlotter = screen.create_plotter(True)
    whitePlotter = screen.create_plotter(False)
    reader = MFRC522(spi=spi, gpioRst=0, gpioCs=2)
    rfid = CockleRfid(reader)
    box = story._get_table(Box)[boxUid]
    engine = Engine(box=box)
    engine.registerStory(story)

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
    )

def runBox(boxUid):
    # configure host
    boxHost = prepareHost(story, boxUid)
    # perform UI cycle
    while boxHost.running:
        boxHost.gameLoop()

if __name__ == "__main__":
    print("Running Main")
    runBox("1")