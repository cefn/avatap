from time import sleep
from milecastles import GoalPage, AnonymousContainer, required
from vault import CardReadIncompleteError, CardBankMissingError, CardJsonInvalidError, CardJsonIncompatibleError

import agnostic

awaitLift =     b"LIFT & REPLACE for more"
awaitReplace =  b"Now REPLACE for more..."
awaitLeave =    b"REMOVE when ready"

# used to reset next tag (red) or trigger fuzzing routine (yellow)
redTags=(b'=\xe5zR\xf0', b'=whRp', b'=eoRe', b'=\x14\x8dR\xf6', b'=\x95?R\xc5', b'=Q\xf2R\xcc')
yellowTags=(b'=[8b<', b'=\x13\xc42\xd8', b'=J\xd92\x9c', b'=\xff(B\xa8', b'=\x0cDB7', b'=\xc5\x96B,')

PRESENCE_TIMEOUT=10000 # ms to wait before discarding card cache or reset command

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
    resetCard = False
    cardCache = None

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
        self.screen.fill_rect(left, top, right - 1, bottom - 1, self.blackPlotter) # color box in black
        self.smallFont.draw_line(line, x=left + 1, y=top + 1, plotter=self.whitePlotter)
        rect = (left, top, right, bottom)
        if redraw:
            self.redraw(rect)
        return rect

    def wipeRect(self, dirtyRect, plotter=None):
        if plotter is None:
            plotter = self.whitePlotter
        fillArgs = list(dirtyRect)
        # handle case that box draws too wide
        fillArgs[2] -= 1
        fillArgs[3] -= 1
        fillArgs.append(plotter)
        self.screen.fill_rect(*fillArgs)
        self.redraw(dirtyRect)

    # allows overriding of redraw
    def redraw(self, dirtyRect=None):
        if dirtyRect is not None:
            self.screen.redraw(dirtyRect[0], dirtyRect[1], dirtyRect[2] - 1, dirtyRect[3] - 1)
        else:
            self.screen.redraw()

    def newLoop(self, fuzz=False):
        agnostic.collect()

        cardUid = None
        card = None

        try: # toast and label finaliser

            toastRect = None
            labelRect = None
            if self.expectStay:
                labelRect = self.label(awaitReplace)  # draw quickly before clearing rest of screen
                self.screen.clear()
                labelRect = self.label(awaitReplace, redraw=False)
            else:
                self.screen.clear()
                if self.resetCard:
                    toastRect = self.toast(b"RESETTING TAG!", redraw=False)
                else:
                    toastRect = self.toast(b"PLACE TAG\nto read", redraw=False)
            self.redraw()

            print("WAITING FOR CARD")
            if self.cardCache or self.resetCard:    # block for short period
                cardUid = self.rfid.awaitPresence(PRESENCE_TIMEOUT)
            else:
                cardUid = self.rfid.awaitPresence()                         # block indefinitely
            if cardUid is None:  # resumeMs timeout was hit
                print("TIMEOUT: ", end="")
                if self.cardCache is not None:
                    print("RESUME ABANDONED")
                    self.cardCache = None
                if self.resetCard:
                    print("RESET ABANDONED")
                    self.resetCard = False
                return None

            print("CARD PRESENT")

            if cardUid in redTags:
                print("RESET REQUESTED")
                self.screen.clear()
                self.redraw()
                toastRect = self.toast(b"Reset requested")
                self.expectStay = False
                self.cardCache = None
                self.resetCard = True
                self.rfid.awaitAbsence()
                return cardUid
        finally:
            if toastRect:
                self.wipeRect(toastRect)
            if labelRect:
                self.wipeRect(labelRect)

        try: # unselect finaliser
            self.rfid.selectTag(cardUid)

            if self.resetCard and not(cardUid in redTags):
                self.resetCard = False
                card = self.story.createBlankCard(cardUid)
                self.rfid.writeCard(card=card, unselect=True)
                toastRect = self.toast(b"Reset complete")
                self.rfid.awaitAbsence()
                self.wipeRect(toastRect)
                return cardUid
            elif self.cardCache is not None:
                if cardUid == self.cardCache.uid:
                    card = self.cardCache
                    print("RESUMED AVOIDING READ")
                else:
                    print("NEW CARD: RESUME ABANDONED")
                self.cardCache = None  # discard cached data from previous cycle (implicitly after resumeMs)

            if card is None:
                try:
                    labelRect = self.label(b"KEEP IN PLACE, loading..")
                    card = self.rfid.readCard(cardUid=cardUid, unselect=False)
                    if card.storyUid != self.story.uid or card.storyVersion != self.story.version:
                        raise CardJsonIncompatibleError("Wrong story or version")
                    print("CARD LOADED")
                except CardReadIncompleteError:
                    print("EARLY REMOVAL")
                    return None
                except (CardBankMissingError, CardJsonInvalidError, CardJsonIncompatibleError, KeyError):
                    print("CARD INVALID")
                    card = self.story.createBlankCard(cardUid)

            try: # label finaliser
                labelRect = self.label(b"KEEP IN PLACE, saving...") # TODO CH calculate location to just wipe and draw 'saving.' over 'loading'

                origNodeUid = card.nodeUid
                nextNode = self.engine.handleCard(card, self)

                # will next page also be at this box?
                if issubclass(type(nextNode), GoalPage) and nextNode.goalBoxUid == self.box.uid:
                    self.expectStay = True # goalpage at same box
                elif nextNode.uid != origNodeUid:
                    self.expectStay = True # remote GoalPage or NodeFork unvisited
                else:
                    self.expectStay = False # remote GoalPage or NodeFork now visited

                try:
                    self.rfid.writeCard(card=card, unselect=False)
                    self.cardCache = card
                except:
                    print("Error; discarding write. One of...")
                    print("Card identity not the intended card to be written")
                    print("Card removed before write complete")
            finally:
                self.wipeRect(labelRect)

            # TODO try this to avoid error counting in awaitAbsence (meaning two presence cycles needed to detect)
            # cardVault.reader.reset()
        finally:
            try:
                labelRect = self.label(awaitLift if self.expectStay else awaitLeave, redraw=False)
                self.redraw()  # TODO redraw fully as workaround for draw alignment bug which seems only to affect this message
                self.rfid.unselectTag()
                if not fuzz: # if fuzzing, don't wait for tag lift
                    self.rfid.awaitAbsence()
                print("CARD REMOVED")
            finally:
                self.wipeRect(labelRect)

        return cardUid

    """
    def gameLoop(self, card=None):
        try:
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
                if self.resetMode:
                    toastRect = self.toast(b"RESETTING TAG!", redraw=False)
                else:
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

                cardBytes = bytes(cardUid)

                print("Card present:", end="")
                print(cardUid)

                if cardBytes in redTags: # red tags trigger a reset of the next tag shown
                    self.screen.clear()
                    self.redraw()
                    toastRect = self.toast(b"Reset requested")
                    self.rfid.awaitAbsence()
                    self.resetMode = True
                    return None

                if cardBytes in yellowTags:
                    return None
            finally:
                if toastRect:
                    self.wipeRect(toastRect)
                if labelRect:
                    self.wipeRect(labelRect)


            if card is None:
                if self.resetMode:
                    self.resetMode = False
                    card = None
                else:
                    labelRect = self.label(b"KEEP IN PLACE, loading..")
                    print("loading ({})".format(agnostic.ticks_ms() - loopStart));
                    taskStart = agnostic.ticks_ms()
                    # TODO need to detect read failure - INVALID card content means reset to blank but failed read should go back to "Place Tag"
                    card = self.rfid.readCard(cardUid, unselect=False)  # expecting to remain selected for write
                    print("loaded! +{}".format(agnostic.ticks_ms() - taskStart))
            # generate blank card if card still none (reset intended, or incompatible card contents)
            if card is None or not(card.storyUid == self.story.uid):
                card = self.story.createBlankCard(cardUid)
            labelRect = self.label(b"KEEP IN PLACE, saving...") # TODO CH calculate location to just wipe and draw 'saving.' over 'loading'
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
                self.rfid.writeCard(card, unselect=False) # unselecting, expecting card to be taken away
                print("saved! +{}".format(agnostic.ticks_ms() - taskStart))
            finally:
                self.wipeRect(labelRect)
            labelRect = self.label(awaitLift if self.expectStay else awaitLeave, redraw=False)
            self.redraw() # TODO redraw fully as workaround for draw alignment bug which seems only to affect this message
            try:
                print("removing ({})".format(agnostic.ticks_ms() - loopStart));taskStart = agnostic.ticks_ms()
                self.rfid.awaitAbsence()
                print("removed! {}".format(agnostic.ticks_ms() - taskStart))
            finally:
                self.wipeRect(labelRect)
            return card
        finally:
            self.rfid.unselectTag()
    """

    def powerDown(self):
        self.powerPin.value(1) # wired to OFF on Polulu Power Switch LV -
        sleep(1) # only seen in testing with LED attached - otherwise the pulse above should power off the unit
        self.powerPin.value(0)