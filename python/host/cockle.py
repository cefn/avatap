import loader
from machine import SPI, Pin
from mfrc522 import MFRC522
from st7920 import Screen
from vault import BankVault
from engines import dictToCard, cardToDict
from host import Host

class CockleRfid(BankVault):

    def readCard(self, cardUid, unselect=True):
        cardDict = self.readJson(cardUid, unselect)
        card = dictToCard(self.adaptor.cardUid, cardDict)
        return card

    def writeCard(self, card, unselect=True):
        return self.writeJson( cardToDict(card), card.uid, unselect)

def launch(story, boxUid):
    # prepare elements
    spi = SPI(1, baudrate=1800000, polarity=0, phase=0)
    spi.init()
    screen = Screen(spi=spi, slaveSelectPin=Pin(15))
    blackPlotter = screen.create_plotter(False)
    whitePlotter = screen.create_plotter(True)
    rfid = CockleRfid(MFRC522(spi=spi, gpioRst=0, gpioCs=2))

    # configure host which will perform UI cycle
    host = Host(
        story=story,
        box=boxTable[boxUid],
        engine=engine,
        screen=screen,
        rfid=rfid,
        smallFont=smallFont,
        bigFont=bigFont,
        blackPlotter=blackPlotter,
        whitePlotter=whitePlotter,
    )

    # Use 'running' flag in while loop or
    # consider converging on Runnable factory instead
    while True:
        host.gameLoop()


