from milecastles import *
from engines import Engine

class ConsoleSiteEmulator(Container):
	required = [n for n in Container.required if n!="uid"] + ["story"]

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
			card = Card(
				uid=cardId,
				storyUid =self.story.uid,
				passageUid = self.story.startPassageUid,
				sack = dict()
			)
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
						
			# handle commands identifying a box in the story
			boxTable = self.story._get_table(Box) # use box lookup from story
			if command in boxTable: 
				if self.currentCard != None:
					print("Tapping box '" + command + "' with card '" + self.currentCard.uid.idString + "'")
					engine = self.engines[command]
					engine.handleCard(self.currentCard)
				else:
					print("Cannot tap box. No card selected. Choose one of " + str(list(cardTable.keys())))
	
class ConsoleEngine(Engine):
	
	def renderText(self, text):
		print(text)
		
if __name__ == "__main__":
	from milecastles import loadStory
	story = loadStory("example")
	emulator = ConsoleSiteEmulator(story=story)
	emulator.run()
