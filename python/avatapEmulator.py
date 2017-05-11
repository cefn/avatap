import random
import os
from time import sleep
from threading import Thread
import pyglet
from agnostic import ticks_ms
from faces.font_5x7 import font as smallFont
from faces.font_ncenB18 import font as bigFont
from engines import cardToDict, dictToCard
from engines.avatap import AvatapSiteEmulator
import st7920Emulator, canvas

from stories.corbridge import story

delays = False
def randomDelay(maxDelay=1):
    if delays:
        sleep(random.uniform(0, maxDelay))

class StubRfid:
    def __init__(self, cardUid = None, cardDict=None):
        if cardUid == None:
            self.cardUid = os.urandom(6)
        else:
            self.cardUid = cardUid

        self.cardDict = cardDict

    def awaitPresence(self):
        randomDelay()
        return self.cardUid

    def readPlayer(self):
        randomDelay()
        if self.cardDict:
            # return the tag and card
            return dictToCard(self.cardUid, self.cardDict)
        else:
            return None

    def writePlayer(self, card):
        randomDelay()
        if card.uid == self.cardUid:
            self.cardDict = cardToDict(card)
        else:
            raise AssertionError("Wrong tag")

    def awaitAbsence(self):
        randomDelay()

def toast(engine, para):
    x = 0
    y = 0
    y -= 6 # vertical offset for bigFont
    dX, dY = engine.bigFont.draw_para(para, engine.blackPlotter, x=x, y=y, lineHeight=32)
    box = (x,y,x + dX, y+ dY) # weird offset logic (redraw uses last coord, not upper bound)
    engine.screen.redraw(*box)
    return box

def label(engine, line):
    labelWidth = engine.smallFont.line_cols(line)
    labelHeight = engine.smallFont.height
    left = engine.screen.width - labelWidth - 1
    top = engine.screen.height - labelHeight - 1
    right = left + labelWidth + 2
    bottom = top + labelHeight + 2
    screen.fill_rect(left - 2, top - 2, right, bottom, False) # color box in black
    engine.smallFont.draw_line(line, x=left + 1, y=top + 1, plotter=engine.whitePlotter)
    box = (left, top, right, bottom)
    engine.screen.redraw(*box)
    return box

def wipeRect(engine, dirtyBox, set=True):
    engine.screen.fill_rect(*dirtyBox, set=set)
    engine.screen.redraw(*dirtyBox)

def gameLoop(engine, rfid):
    toastBox = toast(engine, b"Place Tag\nBelow")
    cardUid = rfid.awaitPresence()
    wipeRect(engine, toastBox)
    labelBox = label(engine, b"Reading tag...")
    card = rfid.readPlayer()
    if card is None:
        card = story.createBlankCard(rfid.cardUid)
    wipeRect(engine, labelBox)
    engine.handleCard(card)
    labelBox = label(engine, b"Writing tag")
    rfid.writePlayer(card)
    wipeRect(engine, labelBox)
    labelBox = label(engine, b"Ready to Remove")
    rfid.awaitAbsence()
    wipeRect(engine, labelBox)
    labelBox = label(engine, b"Tag Removed")
    engine.screen.clear()
    engine.screen.redraw()

if __name__ == "__main__":

    screen = st7920Emulator.PillowScreen()

    window = st7920Emulator.createPygletWindow(screen)

    siteEmulator = AvatapSiteEmulator(
        story = story,
        smallFont=smallFont,
        bigFont=bigFont,
        screen=screen,
        blackPlotter=screen.create_plotter(set=False),
        whitePlotter=screen.create_plotter(set=True),
    )

    rfid = StubRfid()
    boxUids = list(siteEmulator.engines.keys())
    global stamp, fuzz
    stamp = ticks_ms()
    fuzz = True
    def fuzzLoop():
        while fuzz:
            global stamp
            try:
                boxUid = random.choice(boxUids)
                engine = siteEmulator.engines[boxUid]
                gameLoop(engine, rfid)
            except AssertionError as ae:
                print(type(ae).__name__ + str(ae))
            #print(ticks_ms() - stamp)
            stamp = ticks_ms()

    @window.event
    def on_close(*a):
        global fuzz
        fuzz = False

    fuzzThread = Thread(target=fuzzLoop)
    fuzzThread.start()

    # blocking run
    pyglet.app.run()
