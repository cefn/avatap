import random
import os
from time import sleep
from faces.5x7 import font
from engines import cardToDict, dictToCard
from engines.avatap import AvatapSiteEmulator
from stories.corbridge import story

import pillow, canvas

class StubRfid:
    def __init__(self, tagUid = None, cardDict=None):
        if self.tagUid == None:
            self.tagUid = os.urandom(6)
        else:
            self.tagUid = tagUid

        self.cardDict = cardDict

    def readPlayer(self):
        # delay between 0 and 1 second
        sleep(random.uniform(1))
        # return the tag and card
        return self.tagUid, dictToCard(self.cardDict)

    def writePlayer(self, tagUid, card):
        # delay between 0 and 1 second
        sleep(random.uniform(1))
        if tagUid == self.tagUid:
            self.cardDict = cardToDict(story, card)
        else:
            raise AssertionError("Wrong tag")

def fuzzEngine(engine, rfid):
    tagUid, card = rfid.readPlayer()
    if card is None:
        card = story.createBlankCard(tagUid)
    engine.handleCard(card)
    rfid.writePlayer(tagUid=tagUid, card=card)

if __name__ == "__main__":

    screen = pillow.PillowScreen()

    siteEmulator = AvatapSiteEmulator(
        smallFont=font,
        bigFont=font,
        screen=screen,
        blackPlotter=screen.create_plotter(canvas.black),
        whitePlotter=screen.create_plotter(canvas.white),
    )

    rfid = StubRfid()

    while True:
        print("About to fuzz")
        boxUid = random.choice(siteEmulator.engines.keys())
        engine = siteEmulator.engines[boxUid]
        fuzzEngine(engine)
        print("Fuzzed")