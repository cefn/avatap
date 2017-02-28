story = None

def loadStory(storyUid):
	global story
	story = __import__("stories." + storyUid).story

'''
Base class which treats all named arguments as attributes and 
all positional arguments as dicts containing named attributes
'''
class Item(object):
	required=[]
	def __init__(self, *args, **kwargs):
		# populate attributes from positional and keyword args
		for data in args[1:]: # exclude self
			for key in data:
				setattr(self, key, data[key])
		for key in kwargs:
			setattr(self, key, kwargs[key])

		# raise error if any 'required' attributes are missing   
		missing = list()
		for name in type(self).required:
			if not(hasattr(self, name)):
				missing.append(name)
		if len(missing) > 0:
			raise AssertionError(type(self).__name__ + " missing required attributes " + str(missing) )
	
class UidItem(Item):
	required = Item.required + ["uid"]
	pass
	
class Story(UidItem):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.passages = dict()
	
	def registerPassage(self, passage):
		self.passages[passage.uid]=passage
	
	def lookupPassage(self, passageUid):
		return self.passages[passageUid]

class Card(UidItem):
	required = UidItem.required + ["storyUid", "passageUid", "sack"]

class Box(UidItem):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.stories = dict()
	
	def registerStory(self, story):
		self.stories[story.uid]=story
	
	def lookupStory(self, storyUid):
		return self.stories[storyUid]
	
	def handle_card(self, card):
		story = self.lookupStory(card.storyUid)
		passage = story.lookupPassage(card.passageUid)
		passage.handle_tap(self,card)
				
class Passage(UidItem):
	pass

class PagePassage(Passage):
	required = Passage.required + ["showBoxUid", "page", "nextPassageUid"]
					
	def handle_tap(self, box, card):
		if box.uid == self.showBoxUid:
			story = box.lookupStory(card.storyUid)
			nextPassage = story.lookupPassage(self.nextPassageUid)
			if self.showBoxUid == nextPassage.showBoxUid:
				box.render(self.page + "\n...tap to continue")
			else:
				box.render(self.page + "\n...now go to box" + self.nextUid)
		else:
			box.render(error="Wrong box. Go to box " + self.showUid)


class ConsoleBox(Box):
	def render(self, text):
		print(text)
