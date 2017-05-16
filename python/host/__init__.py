import os
import random
from time import sleep
from engines import cardToDict, dictToCard
from milecastles import AnonymousContainer, required

delays = False
def randomDelay(maxDelay=1):
    if delays:
        sleep(random.uniform(0, maxDelay))

"""
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

    def readCard(self):
        randomDelay()
        if self.cardDict:
            # return the tag and card
            return dictToCard(self.cardUid, self.cardDict)
        else:
            return None

    def writeCard(self, card):
        randomDelay()
        if card.uid == self.cardUid:
            self.cardDict = cardToDict(card)
        else:
            raise AssertionError("Wrong tag")

    def awaitAbsence(self):
        randomDelay()

"""

class Host(AnonymousContainer):
    box = required
    story = required
    screen = required
    rfid = required
    engine = required
    smallFont = required
    bigFont = required
    blackPlotter = required
    whitePlotter = required

    def toast(self, para):
        x = 0
        y = 0
        y -= 6 # vertical offset for bigFont
        dX, dY = self.bigFont.draw_para(para, self.blackPlotter, x=x, y=y, lineHeight=32)
        rect = (x,y,x + dX, y+ dY) # weird offset logic (redraw uses last coord, not upper bound)
        self.screen.redraw(*rect)
        return rect

    def label(self, line):
        labelWidth = self.smallFont.line_cols(line)
        labelHeight = self.smallFont.height
        left = self.screen.width - labelWidth - 1
        top = self.screen.height - labelHeight - 1
        right = left + labelWidth + 2
        bottom = top + labelHeight + 2
        self.screen.fill_rect(left - 2, top - 2, right, bottom, False) # color box in black
        self.smallFont.draw_line(line, x=left + 1, y=top + 1, plotter=self.whitePlotter)
        box = (left, top, right, bottom)
        self.screen.redraw(*box)
        return box

    def wipeRect(self, dirtyBox, set=True):
        self.screen.fill_rect(*dirtyBox, set=set)
        self.screen.redraw(*dirtyBox)

    def gameLoop(self):
        toastRect = self.toast(b"Place Tag\nBelow")
        cardUid = self.rfid.awaitPresence()
        self.wipeRect(toastRect)
        labelRect = self.label(b"Reading tag...")
        card = self.rfid.readCard(cardUid=cardUid)
        if card is None:
            card = self.story.createBlankCard(cardUid)
        self.wipeRect(labelRect)
        self.engine.handleCard(card)
        labelRect = self.label(b"Writing tag")
        self.rfid.writeCard(card)
        self.wipeRect(labelRect)
        labelRect = self.label(b"Ready to Remove")
        self.rfid.awaitAbsence()
        self.wipeRect(labelRect)
        labelRect = self.label(b"Tag Removed")
        self.screen.clear()
        self.screen.redraw()
