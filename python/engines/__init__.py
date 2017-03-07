from milecastles import Container, Story

class Engine(Container):
	required = Container.required + ["box"]
	
	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		
	def registerStory(self, story):
		return self._register(Story, story)
	
	def lookupStory(self, storyUid):
		return self._lookup(Story, storyUid)
		
	def handle_card(self, card):
		story = self.lookupStory(card.storyUid)
		passage = story.lookupPassage(card.passageUid)
		passage.handle_tap(self,card)
		
	'''Should render some text, in whatever form required by the Engine'''
	def render(self, text):
		raise Error("Not yet implemented")
