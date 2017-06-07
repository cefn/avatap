import os
import random
from time import sleep
from milecastles import AnonymousContainer, required

delayActive = True

def hostDelay(delay):
    if delayActive:
        sleep(delay)

def randomDelay(maxDelay=1):
    hostDelay(random.uniform(0, maxDelay))

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
    running = True

    def displayGeneratedText(self, generator):
        self.screen.clear()
        self.smallFont.draw_generator(generator, self.blackPlotter)
        self.screen.redraw()

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

    # TODO CH add 'Replace for next page' behaviour
    # TODO CH add 'special control tag' handling behaviour
    def gameLoop(self):
        toastRect = self.toast(b"PLACE TAG\n  TO READ")
        cardUid = self.rfid.awaitPresence()
        self.wipeRect(toastRect)
        labelRect = self.label(b"Loading Game...")
        card = self.rfid.readCard(cardUid=cardUid)
        if card is None:
            card = self.story.createBlankCard(cardUid)
        self.wipeRect(labelRect)
        self.engine.handleCard(card)
        labelRect = self.label(b"Saving Game...")
        self.rfid.writeCard(card)
        self.wipeRect(labelRect)
        labelRect = self.label(b"Lift & Replace for more")
        self.rfid.awaitAbsence()
        self.wipeRect(labelRect)
        labelRect = self.label(b"Tag Removed")
        self.screen.clear()
        self.screen.redraw()

    def createRunnable(self):
        def run():
            while self.running:
                try:
                    self.gameLoop()
                except Exception as e:
                    print(type(e).__name__ + str(e))
                    if type(e) is not AssertionError:
                        raise e
        return run