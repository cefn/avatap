from time import sleep
from milecastles import GoalPage, AnonymousContainer, required
import agnostic

awaitLift =     b"LIFT & REPLACE for more"
awaitReplace =  b"Now REPLACE for more..."
awaitLeave =    b"REMOVE when ready"

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
    powerPin = required
    running = True
    expectStay = False

    def displayGeneratedText(self, generator):
        self.screen.clear()
        (x,y) = self.smallFont.draw_generator(generator, self.blackPlotter)
        self.redraw((0,0,x,y))

    def toast(self, para, redraw=True):
        x = 0
        y = 0
        dX, dY = self.bigFont.draw_para(para, self.blackPlotter, x=x, y=y)
        rect = (x,y,x + dX, y + dY) # compensate for weird offset logic? (redraw uses last coord, not upper bound)
        if redraw:
            self.redraw(rect)
        return rect

    def label(self, line, redraw=True):
        labelWidth = self.smallFont.line_cols(line)
        labelHeight = self.smallFont.height
        right = self.screen.width
        bottom = self.screen.height
        left = right - (labelWidth + 2)
        top = bottom - (labelHeight + 2)
        self.screen.fill_rect(left, top, right, bottom, set=True) # color box in black
        self.smallFont.draw_line(line, x=left + 1, y=top + 1, plotter=self.whitePlotter)
        rect = (left, top, right, bottom)
        if redraw:
            self.redraw(rect)
        return rect

    def wipeRect(self, dirtyRect, set=False):
        self.screen.fill_rect(*dirtyRect, set=set)
        self.redraw(dirtyRect)

    # allows overriding of redraw
    def redraw(self, dirtyRect=None):
        if dirtyRect is not None:
            self.screen.redraw(*dirtyRect)
        else:
            self.screen.redraw()

    # TODO CH add 'special control tag' handling behaviour, based around host 'expectWipeNext'
    # TODO either fully remove or fully implement timeout
    def gameLoop(self, card=None):
        loopStart = agnostic.ticks_ms()
        print("START {}".format(loopStart))
        toastRect = None
        labelRect = None
        if self.expectStay:
            labelRect = self.label(awaitReplace) # draw quickly before clearing rest of screen
            self.screen.clear()
            labelRect = self.label(awaitReplace, redraw=False)
        else:
            self.screen.clear()
            toastRect = self.toast(b"PLACE TAG\nto read", redraw=False)
        self.redraw()
        try:
            if card is not None: # handle 'simulated' card passed in as argument
                cardUid = card.uid
            else:
                cardUid = None

            while cardUid is None: # remain here until a cardUid is seen or timeout is hit
                print("presenting ({})".format(agnostic.ticks_ms() - loopStart)); taskStart = agnostic.ticks_ms()
                cardUid = self.rfid.awaitPresence()
                print("present! +{}".format(agnostic.ticks_ms() - taskStart))
        finally:
            if toastRect:
                self.wipeRect(toastRect)
            if labelRect:
                self.wipeRect(labelRect)
        labelRect = self.label(b"KEEP IN PLACE, loading..")
        print("loading ({})".format(agnostic.ticks_ms() - loopStart)); taskStart = agnostic.ticks_ms()
        if card is None:
            # TODO need to detect read failure - INVALID card content means reset to blank but failed read should go back to "Place Tag"
            card = self.rfid.readCard(cardUid=cardUid, unselect=False) # expecting to remain selected for write
        print("loaded! +{}".format(agnostic.ticks_ms() - taskStart))
        if card is None or not(card.storyUid == self.story.uid):
            card = self.story.createBlankCard(cardUid)
        labelRect = self.label(b"KEEP IN PLACE, saving...") # TODO CH bring this until before text is shown, so people don't forget
        origNodeUid = card.nodeUid
        print("handling ({})".format(agnostic.ticks_ms() - loopStart));taskStart = agnostic.ticks_ms()
        nextNode = self.engine.handleCard(card, self)
        print("handled! +{}".format(agnostic.ticks_ms() - taskStart))
        # TODO CH accelerate case where nodeUid not changed (e.g. wrong box - no need to rewrite)
        # will next page also be at this box?
        if issubclass(type(nextNode), GoalPage) and nextNode.goalBoxUid == self.box.uid:
            self.expectStay = True # goalpage at same box
        elif nextNode.uid != origNodeUid:
            self.expectStay = True # remote GoalPage or NodeFork unvisited
        else:
            self.expectStay = False # remote GoalPage or NodeFork now visited
        try:
            print("saving ({})".format(agnostic.ticks_ms() - loopStart));taskStart = agnostic.ticks_ms()
            self.rfid.writeCard(card, unselect=True) # unselecting, expecting card to be taken away
            print("saved! +{}".format(agnostic.ticks_ms() - taskStart))
        finally:
            self.wipeRect(labelRect)
        labelRect = self.label(awaitLift if self.expectStay else awaitLeave, redraw=False)
        self.redraw() # TODO workaround for draw alignment bug which seems only to affect this message
        try:
            print("removing ({})".format(agnostic.ticks_ms() - loopStart));taskStart = agnostic.ticks_ms()
            self.rfid.awaitAbsence()
            print("removed! {}".format(agnostic.ticks_ms() - taskStart))
        finally:
            self.wipeRect(labelRect)
        return card

    def powerDown(self):
        self.powerPin.value(1) # wired to OFF on Polulu Power Switch LV -
        sleep(1) # only seen in testing with LED attached - otherwise the pulse above should power off the unit
        self.powerPin.value(0)