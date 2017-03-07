from milecastles import Container, Story

class Debug():
	def report(report):
		print(report)
		
	def debug(msg):
		print("DEBUG:" + msg)

	def info(msg):
		print("INFO:" + msg)

	def warn(msg):
		print("WARN:" + msg)

	def error(msg):
		print("ERROR:" + msg)

	def fatal(msg):
		print("FATAL:" + msg)

class Engine(Container):
	required = [n for n in Container.required if n!="uid"] + ["box"] # remove "uid"
	
	def __init__(self, *a, **k):
		super().__init__(*a, **k)
		self.debug = Debug()
		
	def registerStory(self, story):
		return self._register(Story, story)
	
	def lookupStory(self, storyUid):
		return self._lookup(Story, storyUid)
				
	def handleCard(self, card):
		self.card = card
		self.story = self.lookupStory(card.storyUid)
		passage = self.story.lookupPassage(card.passageUid)
		passage.handleTap(self)
		
	'''Should render some text, in whatever form required by the Engine'''
	def renderText(self, text):
		raise AssertionError("Not yet implemented")
