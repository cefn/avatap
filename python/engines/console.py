from milecastles import Item,Box
from engines import Engine

class ConsoleSiteEmulator(Item):

	required = Item.required + ["story"]

	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		
		# get boxes from story registry, create+store an engine for each 
		boxTable = self.story._get_table(Box)
		self.engines = dict()		
		for boxUid,box in boxTable.items():
			self.engines[boxUid] = ConsoleEngine(box=box)
			
		# for each card, register it with the emulator
		cardIds = ["a","b","c","d"]
		for cardId in self.cardIds:
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
		
	def run():
		while True:
			command = input()
			
			# handle commands indentifying a card in the emulator
			cardTable = self._get_table(Card) # use box lookup from story
			if command in cardTable: 
				self.currentCard = self.cards[command]
				print("Current card set to '" + command + "'")
						
			# handle commands identifying a box in the story
			boxTable = self.story._get_table(Box) # use box lookup from story
			if command in boxTable: 
				if self.currentCard != None:
					print("Tapping box'" + command + "' with card '" + self.currentCard.uid.idString + "'")
					engine = self.engines[command]
					engine.handle_card(self.currentCard)
				else:
					print("Cannot tap box. No card selected. Choose one of " + str(list(cards.keys())))
	
class ConsoleEngine(Engine):
	
	def render(self, text):
		print("text")
		
if __name__ == "__main__":
	story = 
	emulator = ConsoleSiteEmulator()	


