from time import sleep
from milecastles import GoalPage, AnonymousContainer, required

delayActive = True

awaitLift =     b"LIFT & REPLACE for more."
awaitReplace =  b"Now REPLACE for more...."
awaitLeave =    b""

def hostDelay(delay):
    if delayActive:
        sleep(delay)

def randomDelay(maxDelay=1):
    import random
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
    expectStay = False

    def displayGeneratedText(self, generator):
        self.screen.clear()
        self.smallFont.draw_generator(generator, self.blackPlotter)
        self.screen.redraw()

    def toast(self, para, redraw=True):
        x = 0
        y = 0
        dX, dY = self.bigFont.draw_para(para, self.blackPlotter, x=x, y=y)
        rect = (x,y,x + dX, y + dY) # compensate for weird offset logic? (redraw uses last coord, not upper bound)
        if redraw:
            self.screen.redraw(*rect)
        return rect

    def label(self, line, redraw=True):
        labelWidth = self.smallFont.line_cols(line)
        labelHeight = self.smallFont.height
        left = self.screen.width - labelWidth - 1
        top = self.screen.height - labelHeight - 1
        right = left + labelWidth + 2
        bottom = top + labelHeight + 2
        self.screen.fill_rect(left - 2, top - 2, right, bottom, set=True) # color box in black
        self.smallFont.draw_line(line, x=left + 1, y=top + 1, plotter=self.whitePlotter)
        rect = (left, top, right, bottom)
        if redraw:
            self.screen.redraw(*rect)
        return rect

    def wipeRect(self, dirtyRect, set=False):
        self.screen.fill_rect(*dirtyRect, set=set)
        self.screen.redraw(*dirtyRect)

    # TODO CH add 'special control tag' handling behaviour
    def gameLoop(self):
        toastRect = None
        labelRect = None
        if self.expectStay:
            labelRect = self.label(awaitReplace) # draw rapidly before full screen refresh
            self.screen.clear()
            labelRect = self.label(awaitReplace, redraw=False)
        else:
            self.screen.clear()
            toastRect = self.toast(b"PLACE TAG\nto read")
        self.screen.redraw()
        cardUid = None
        while cardUid is None: # hang here until a cardUid is seen
            cardUid = self.rfid.awaitPresence()
        if toastRect:
            self.wipeRect(toastRect)
        if labelRect:
            self.wipeRect(labelRect)
        labelRect = self.label(b"KEEP IN PLACE, loading..")
        card = self.rfid.readCard(cardUid=cardUid)
        if card is None:
            card = self.story.createBlankCard(cardUid)
        self.wipeRect(labelRect)
        origNodeUid = card.nodeUid
        nextNode = self.engine.handleCard(card, self)
        # will next page also be at this box?
        if issubclass(type(nextNode), GoalPage) and nextNode.goalBoxUid == self.box.uid:
            self.expectStay = True # goalpage at same box
        elif nextNode.uid != origNodeUid:
            self.expectStay = True # remote GoalPage or NodeFork unvisited
        else:
            self.expectStay = False # remote GoalPage or NodeFork now visited
        labelRect = self.label(b"KEEP IN PLACE, saving...")
        self.rfid.writeCard(card)
        self.wipeRect(labelRect)
        labelRect = self.label(awaitLift if self.expectStay else awaitLeave)
        self.rfid.awaitAbsence()
        self.wipeRect(labelRect)

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