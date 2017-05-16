import string
import random
from os import urandom
from time import sleep
from threading import Thread
import pyglet
from agnostic import ticks_ms
from faces.font_5x7 import font as smallFont
from faces.font_ncenB18 import font as bigFont
from engines import cardToDict, dictToCard
from engines.avatap import AvatapEngine
import st7920Emulator

from milecastles import Box

from stories.corbridge import story

from host import Host, hostDelay

def randomCardUid():
    return urandom(6)

defaultNumCards = 4
defaultDelay = 1.0

pollDelay = 0.01

presenceDelay = defaultDelay
readDelay = defaultDelay
writeDelay = defaultDelay
absenceDelay = defaultDelay

# TODO CH make queued, not polling
class LaptopRfid:
    def __init__(self, adaptor, boxUid):
        self.adaptor = adaptor
        self.boxUid = boxUid

    def awaitPresence(self, cardUid=None):
        while self.adaptor.boxUid != self.boxUid or self.adaptor.cardUid is None:
            sleep(pollDelay)
        hostDelay(presenceDelay)
        if cardUid is not None and self.adaptor.cardUid != cardUid:
            raise AssertionError("Wrong Tag")
        return self.adaptor.cardUid

    def readCard(self, cardUid=None):
        hostDelay(readDelay)
        if self.adaptor.boxUid != self.boxUid or self.adaptor.cardUid is None:
            raise AssertionError("No Tag")
        if cardUid is not None and self.adaptor.cardUid != cardUid:
            raise AssertionError("Wrong Tag")
        card = dictToCard(self.adaptor.cardUid, self.adaptor.cardDictMap[self.adaptor.cardUid])
        return card

    def writeCard(self, card):
        hostDelay(writeDelay)
        if self.adaptor.boxUid != self.boxUid or self.adaptor.cardUid is None:
            raise AssertionError("No Tag")
        if self.adaptor.cardUid != card.uid:
            raise AssertionError("Wrong Tag")
        self.adaptor.cardDictMap[self.adaptor.cardUid]=cardToDict(card)

    def awaitAbsence(self):
        while self.adaptor.boxUid == self.boxUid and self.adaptor.cardUid is not None:
            sleep(pollDelay)
        hostDelay(absenceDelay)

class KeyboardState:
    def __init__(self, story, cardDictMap=None):
        # populate boxes from story
        boxTable = story._get_table(Box)
        numBoxes = len(boxTable)

        # populate card dicts if not provided
        if cardDictMap is None:
            cardDictMap = dict()
            for cardPos in range(defaultNumCards):
                cardUid = randomCardUid()
                cardDictMap[cardUid] = cardToDict(story.createBlankCard(cardUid))

        self.cardDictMap = cardDictMap

        self.boxKeyMap = dict()
        self.cardKeyMap = dict()

        self.boxUid = None
        self.cardUid = None

        # boxes map to number keys
        for boxUid in [str(boxIndex + 1) for boxIndex in range(numBoxes)]: # names start at 1
            assert boxUid in boxTable, "Boxes don't have numerical uids"
            pygletCode = getattr(pyglet.window.key, "_{}".format(boxUid))
            self.boxKeyMap[pygletCode] = boxUid

        # cards map to letter keys
        cardUids = list(cardDictMap.keys())
        cardUids.sort() # order as ascii strings
        for cardPos,cardUid in enumerate(cardUids):
            pygletCode = getattr(pyglet.window.key, string.ascii_uppercase[cardPos])
            self.cardKeyMap[pygletCode] = cardUids[cardPos]

    def on_key_press(self, symbol, modifiers):
        if symbol in self.boxKeyMap:
            self.boxUid = self.boxKeyMap[symbol]
        if symbol in self.cardKeyMap:
            self.cardUid = self.cardKeyMap[symbol]

    def on_key_release(self, symbol, modifiers):
        if symbol in self.boxKeyMap:
            self.boxUid = None
        if symbol in self.cardKeyMap:
            self.cardUid = None

    def create_rfid(self, boxUid):
        adaptor = self
        return LaptopRfid(adaptor, boxUid)

if __name__ == "__main__":

    boxTable = story._get_table(Box)

    keyState = KeyboardState(story)

    hosts = dict()
    screens = list()

    def createRun(host):
        def run():
            while host.box.uid in hosts:
                try:
                    host.gameLoop()
                except Exception as e:
                    print(type(e).__name__ + str(e))
                    if type(e) is not AssertionError:
                        raise e
        return run

    boxUids = list(boxTable.keys())
    boxUids.sort()
    for boxUid in boxUids:
        box = story.lookupBox(boxUid)
        rfid = keyState.create_rfid(boxUid) # TODO can simplify by creating window last, or does RFID need window beforehand?
        screen = st7920Emulator.PillowScreen()
        blackPlotter = screen.create_plotter(False)
        whitePlotter = screen.create_plotter(True)
        engine = AvatapEngine(
            box=box,
            screen=screen,
            smallFont=smallFont,
            blackPlotter=blackPlotter
        )
        engine.registerStory(story)
        host = Host(
            story = story,
            box = boxTable[boxUid],
            engine=engine,
            screen=screen,
            rfid = rfid,
            smallFont=smallFont,
            bigFont=bigFont,
            blackPlotter=blackPlotter,
            whitePlotter=whitePlotter,
        )
        hosts[boxUid] = host
        screens.append(screen)
        hostRun = createRun(host)
        hostThread = Thread(target=hostRun, daemon=True)
        hostThread.start()

    window = st7920Emulator.createPygletWindow(screens)
    window.push_handlers(keyState)

    @window.event
    def on_close(*a):
        # remove all hosts
        for boxUid in list(hosts.keys()):
            del hosts[boxUid]

    # blocking run
    pyglet.app.run()