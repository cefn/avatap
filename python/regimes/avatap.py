# Example VFS-based debug cycle while developing this file
# screen /dev/ttyUSB0 115200
# import os; os.mkdir('regimes'); os.mkdir('engines')
# for PATH in "loader.py" "regimes/__init__.py" "regimes/avatap.py" "engines/__init__.py" "engines/avatap.py" ; do ampy --port /dev/ttyUSB0 put $PATH $PATH ; done
# screen /dev/ttyUSB0 115200
# from regimes.avatap import runBox; runBox("1")
import loader
loader.loadAll()
import agnostic
from faces.font_5x7 import font
from st7920 import Screen
from mfrc522 import MFRC522
from machine import Pin,SPI
import milecastles
from engines import dictToCard, cardToDict
from engines.avatap import AvatapEngine
from vault import BankVault
#TODO CH normalise this story module info into one place (e.g. loader, or via milecastles.loadStory)
from stories.corbridge import story
agnostic.collect()

spi = SPI(1, baudrate=1000000, polarity=0, phase=0)
spi.init()
agnostic.collect()

reader = MFRC522(spi=spi, gpioRst=0, gpioCs=2)
agnostic.collect()

vault = BankVault(reader)
agnostic.collect()

screen = Screen(spi=spi, slaveSelectPin=Pin(15))
agnostic.collect()

# TODO CH remove this test function (actual plotter is in avatap engine)
def plotter(x,y):
    screen.plot(x,y)

# TODO CH remove this test function
def generatorFactory():
    yield "Starting!\n"

def runBox(boxUid):

    agnostic.collect()
    #TODO CH remove these test lines
    screen.clear()
    font.draw_generator(generatorFactory(), plotter)
    screen.redraw()

    agnostic.collect()

    boxUid = str(boxUid) # handle case of passing a number

    boxEngine = AvatapEngine(
        box=story.lookupBox(boxUid),
        screen=screen,
        font=font,
    )
    boxEngine.registerStory(story)
    agnostic.collect()

    while True:
        agnostic.report_collect()
        try:
            tagUid = vault.awaitPresence()
            try:
                cardDict = vault.readJson(tagUid=tagUid)
                if "storyUid" not in cardDict or cardDict["storyUid"] is not loader.storyUid:
                    cardDict = None # existing card data incompatible
            except Exception as e:
                if type(e) is KeyboardInterrupt:
                    raise e
                else:
                    print(e)
                    cardDict = None # couldn't read card for some reason

            if cardDict is not None:
                print("JSON Good")
                card = dictToCard(tagUid, cardDict)
            else:
                print("JSON Bad")
                card = story.createBlankCard(tagUid)

            agnostic.collect()

            boxEngine.handleCard(card)
            print("Handled Card")
            vault.writeJson(cardToDict(card), tagUid=tagUid, unselect=True)
            print("Written JSON")
            vault.awaitAbsence()
            print("Card removed")
        except AssertionError as ae:
            print(type(ae).__name__ + str(ae))
        except KeyboardInterrupt:
            break