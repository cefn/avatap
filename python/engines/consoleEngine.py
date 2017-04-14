from milecastles import AnonymousContainer, Box, Card
from engine import Engine

class ConsoleSiteEmulator(AnonymousContainer):
    required = AnonymousContainer.required + ["story"]

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
        # get boxes from story registry, create+store an engine for each 
        #import pdb; pdb.set_trace()
        boxTable = self.story._get_table(Box)
        self.engines = dict()        
        for boxUid,box in boxTable.items():
            engine = ConsoleEngine(box=box)
            engine.registerStory(self.story)
            self.engines[boxUid] = engine
            
        # for each card, register it with the emulator
        cardIds = ["a","b","c","d"]
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
            command = input()
            
            # handle commands indentifying a card in the emulator
            cardTable = self._get_table(Card) # use box lookup from story
            if command in cardTable: 
                self.currentCard = cardTable[command]
                print("Current card set to '" + command + "'")

            else:
                # handle commands identifying a box in the story
                boxUids = list(self.story._get_table(Box).keys())
                matchingBoxUids = [boxUid for boxUid in boxUids if command in boxUid]
                numMatching = len(matchingBoxUids)
                if numMatching == 0:
                    print("No box uids match '" + command + "'")
                elif numMatching >= 2:
                    print("Too many box uids match '" + command + "' : " + str(matchingBoxUids) )
                elif numMatching == 1: # a single box got matched
                    boxUid = matchingBoxUids[0]
                    if self.currentCard != None:
                        print("Tapping box '" + command + "' with card '" + self.currentCard.uid + "'")
                        self.engines[boxUid].handleCard(self.currentCard)
                    else:
                        print("Cannot tap box. No card selected. Choose one of " + str(list(cardTable.keys())))            
    
class ConsoleEngine(Engine):
    
    def displayText(self, text):
        print(text)
        
if __name__ == "__main__":
    from milecastles import loadStory
    story = loadStory("exampleShort")
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()
