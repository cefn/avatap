from milecastles import AnonymousContainer, Box, Card
from engines import Engine

class ConsoleSiteEmulator(AnonymousContainer):
    required = AnonymousContainer.required + ["story"]

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        
        # get boxes from story registry, create+store an engine for each 
        #import pdb; pdb.set_trace()
        boxTable = self.story._get_table(Box)
        self.engines = dict()        
        for boxIdString,box in boxTable.items():
            engine = ConsoleEngine(box=box)
            engine.registerStory(self.story)
            self.engines[boxIdString] = engine
            
        # for each card, register it with the emulator
        cardIds = ["a","b","c","d"]
        for cardId in cardIds:
            card = story.createBlankCard(cardId)
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
                boxes = list(self.story._get_table(Box).values())
                boxCommands = [str(pos + 1) for pos in range(len(boxes))]
                try:
                    boxPos = boxCommands.index(command)
                    if self.currentCard != None:
                        print("Tapping box '" + command + "' with card '" + self.currentCard.uid.idString + "'")
                        engine = self.engines[boxes[boxPos].uid.idString]
                        engine.handleCard(self.currentCard)
                    else:
                        print("Cannot tap box. No card selected. Choose one of " + str(list(cardTable.keys())))            
                except ValueError:
                    print("Command not a card id or a box position. Can't understand command")
    
class ConsoleEngine(Engine):
    
    def renderText(self, text):
        print(text)
        
if __name__ == "__main__":
    from milecastles import loadStory
    story = loadStory("exampleShort")
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()
