import sys
import agnostic
import gc
from milecastles import AnonymousContainer, Box, Card, required
from engine import Engine

class ConsoleSiteEmulator(AnonymousContainer):
    story = required

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
        # get boxes from story registry, create+store an engine for each 
        boxTable = self.story._get_table(Box)
        self.engines = dict()        
        for boxUid,box in boxTable.items():
            engine = ConsoleEngine(box=box)
            engine.registerStory(self.story)
            self.engines[boxUid] = engine
            
        # for each card, register it with the emulator
        cardIds = "abcd"
        for cardId in cardIds:
            card = self.story.createBlankCard(cardId)
            self.registerCard(card)
            
        self.currentCard = None
    
    def registerCard(self, card):
        self._register(Card, card)
        
    def lookupCard(self, cardUid):
        self._lookup(Card, cardUid)
        
    def run(self):
        while True:
            #agnostic.report_collect()
            command = input()
            
            # handle commands indentifying a card in the emulator
            cardTable = self._get_table(Card) # use box lookup from story
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
                    print(">1 matching boxes '{}' : {}".format(command, str(matchingBoxUids) ))
                elif numMatching == 1: # a single box got matched
                    boxUid = matchingBoxUids[0]
                    if self.currentCard != None:
                        print("Tap '{}' with '{}'".format(command, self.currentCard.uid))
                        self.engines[boxUid].handleCard(self.currentCard)
                    else:
                        print("No card. Choose from {}".format(str(list(cardTable.keys()))))
    
class ConsoleEngine(Engine):
    
    def displayGeneratedText(self, generator):
        for chunk in generator:
            sys.stdout.write(chunk)

if __name__ == "__main__":
    from milecastles import loadStory
    story = loadStory("exampleShort")
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()
