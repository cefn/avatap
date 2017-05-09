import random
import os
from agnostic import ticks_ms
from time import sleep
import pyglet
from pyglet.gl import *
from faces.font_5x7 import font
from engines import cardToDict, dictToCard
from engines.avatap import AvatapSiteEmulator
import st7920Emulator, canvas

from stories.corbridge import story

delays = False

class StubRfid:
    def __init__(self, cardUid = None, cardDict=None):
        if cardUid == None:
            self.cardUid = os.urandom(6)
        else:
            self.cardUid = cardUid

        self.cardDict = cardDict

    def readPlayer(self):
        # delay between 0 and 1 second
        if delays:
            sleep(random.uniform(0,1))
        if self.cardDict:
            # return the tag and card
            return dictToCard(self.cardUid, self.cardDict)
        else:
            return None

    def writePlayer(self, card):
        # delay between 0 and 1 second
        if delays:
            sleep(random.uniform(0, 1))
        if card.uid == self.cardUid:
            self.cardDict = cardToDict(card)
        else:
            raise AssertionError("Wrong tag")

def gameLoop(engine, rfid):
    card = rfid.readPlayer()
    if card is None:
        card = story.createBlankCard(rfid.cardUid)
    engine.handleCard(card)
    rfid.writePlayer(card)

if __name__ == "__main__":

    window = pyglet.window.Window(width=1024, height=512)

    screen = st7920Emulator.PillowScreen()

    siteEmulator = AvatapSiteEmulator(
        story = story,
        smallFont=font,
        bigFont=font,
        screen=screen,
        blackPlotter=screen.create_plotter(canvas.black),
        whitePlotter=screen.create_plotter(canvas.white),
    )

    rfid = StubRfid()
    boxUids = list(siteEmulator.engines.keys())
    global stamp
    stamp = ticks_ms()
    def fuzzLoop(passed):
        global stamp
        try:
            boxUid = random.choice(boxUids)
            engine = siteEmulator.engines[boxUid]
            gameLoop(engine, rfid)
        except AssertionError as ae:
            print(AssertionError.__name__ + str(ae))
        print(ticks_ms() - stamp)
        stamp = ticks_ms()

    @window.event
    def on_draw():
        pyglet.gl.glClearColor(255,255,255,255)
        # assists with scaling textures in expected (blocky) way, following https://gamedev.stackexchange.com/questions/20297/how-can-i-resize-pixel-art-in-pyglet-without-making-it-blurry
        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        window.clear()
        screen.pygletSprite.draw()

    pyglet.clock.schedule(fuzzLoop)

    pyglet.app.run()