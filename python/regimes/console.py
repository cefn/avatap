from time import sleep
import sys
from math import floor
from os import urandom
import agnostic
from milecastles import AnonymousContainer, Box, Card, required, raiser
from engines import Engine

def log2approx(val):
    val = floor(val)
    approx = 0
    while val != 0:
        val &= ~ (1 << approx)
        approx = approx + 1
    return approx

def randint(minVal, maxVal=None):
    if (maxVal != None):
        return minVal + randint(maxVal - minVal)
    else:
        maxVal = minVal
    byteCount = (log2approx(maxVal) // 8) + 1  # each byte is 8 powers of two
    val = 0
    randBytes = urandom(byteCount)
    idx = 0
    while idx < len(randBytes):
        val |= randBytes[idx] << (idx * 8)
        idx += 1
    del randBytes
    return val % maxVal

def fuzz(emulator):
    emulator.handleInput("a")
    while True:
        emulator.handleInput(command=str(randint(1,4)))
        agnostic.report_collect()
        sleep(1)

class SiteEmulator(AnonymousContainer):

    story = required

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

        # get boxes from story registry, create+store an engine for each
        boxTable = self.story._get_table(Box)
        self.engines = dict()
        for boxUid, box in boxTable.items():
            engine = Engine(box=box)
            engine.registerStory(self.story)
            self.engines[boxUid] = engine

        # for each card, register it with the emulator
        cardIds = "a"
        for cardId in cardIds:
            card = self.story.createBlankCard(cardId)
            self.registerCard(card)

        self.currentCard = None

    def registerCard(self, card):
        self._register(Card, card)

    def lookupCard(self, cardUid):
        self._lookup(Card, cardUid)

class ConsoleHost:
    def displayGeneratedText(self, generator):
        for chunk in generator:
            sys.stdout.write(chunk)

class ConsoleSiteEmulator(SiteEmulator):

    def createEngine(self, box):
        return ConsoleEngine(box=box)

    def handleInput(self, command=None):
        if command is None:
            command = input()

        # handle commands indentifying a card in the emulator
        host = ConsoleHost()
        cardTable = self._get_table(Card)  # use box lookup from story
        if command in cardTable:
            self.currentCard = cardTable[command]
            print("Card:'{}'".format(command))
        else:
            # handle commands identifying a box in the story
            boxUids = list(self.story._get_table(Box).keys())
            matchingBoxUids = [boxUid for boxUid in boxUids if command in boxUid]
            numMatching = len(matchingBoxUids)
            if numMatching == 0:
                print("No matching box '{}'".format(command))
            elif numMatching >= 2:
                print(">1 matching boxes '{}' : {}".format(command, str(matchingBoxUids)))
            elif numMatching == 1:  # a single box got matched
                boxUid = matchingBoxUids[0]
                if self.currentCard != None:
                    print("Tap '{}' with '{}'".format(command, self.currentCard.uid))
                    self.engines[boxUid].handleCard(self.currentCard, host)
                else:
                    print("No card. Choose from {}".format(str(list(cardTable.keys()))))

    def run(self):
        while True:
            agnostic.collect()
            self.handleInput()
            agnostic.collect()


if __name__ == "__main__":
    from milecastles import loadStory
    story = loadStory("exampleShort")
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()