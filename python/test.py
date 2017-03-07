import unittest
from milecastles import *
from engines import Engine

class MockEngine(Engine):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.render_calls = list()
		
	def renderText(self, *args, **kwargs):
		self.render_calls.append((args, kwargs))
		
# create passage ids
passageIdStrings = [
	"landingPassage",
	"endingPassage",
]
boxIdStrings = [
	"northBox",
	"eastBox",
	"southBox",
	"westBox"
]
# populate into an item
uidDict = dict()
for idString in passageIdStrings + boxIdStrings:
	uidDict[idString]=Uid(idString)
uids = Item(uidDict)
del uidDict
	
class PageTest(Container, unittest.TestCase):
	required = [n for n in Container.required if n!="uid"] # remove need for uid
	
	def __init__(self, *args, **kwargs): # note multiple inheritance
		super().__init__(*args, **kwargs)
		self.num_boxes = 4
	
	def registerEngine(self, engine):
		return self._register(Engine, engine)
	
	def lookupEngine(self, engineUid):
		return self._lookup(Engine, engineUid)
		
	def setUp(self):
		# create uids to wire up/trigger story+passages
		self.landingUid = 	Uid("landing")
		self.endingUid = 	Uid("ending")
		
		# create ids for boxes
		self.northBoxUid = 	Uid("north")
		self.eastBoxUid = 	Uid("east")
		self.southBoxUid = 	Uid("south")
		self.westBoxUid = 	Uid("west")
		
		# record all boxUids in a list for later exhaustive testing
		self.boxUids = [
			self.northBoxUid, 
			self.eastBoxUid, 
			self.southBoxUid, 
			self.westBoxUid
		]

		# create 'story' 
		self.story = Story(
			uid="teststory",
			startPassageUid=self.landingUid
		)
		
		with self.story:

			# configure boxes, starting at 1
			
			for boxUid in self.boxUids:
				Box(uid=boxUid, label="The box called " + boxUid.idString) 
			
			# create a beginning passage which points to the end passage
			PagePassage(
				uid=self.landingUid,
				rightBoxUid=self.northBoxUid,
				rightBoxText="Welcome to Milecastles.",
				nextPassageUid=self.endingUid
			)

			# create an ending passage for the story
			PagePassage(
				uid=self.endingUid,
				rightBoxUid=self.southBoxUid,
				rightBoxText="You have finished your adventure",
				nextPassageUid=self.landingUid
			)
		
		# configure engine for each box in the story
		for boxIdString,box in self.story._get_table(Box).items():
			engine = MockEngine(uid=boxIdString, box=box)
			engine.registerStory(self.story)
			self.registerEngine(engine)

	def tearDown(self):
		del self.story, self.registry, self.landingUid, self.endingUid
			
	def test_show_text(self):
		# create an imaginary card
		card = self.story.createBlankCard("abcdefgh")
				
		# present the card to the relevant engine
		engine = self.lookupEngine(self.northBoxUid)
		
		#import pdb; pdb.set_trace()

		engine.handleCard(card)

		# check results
		assert len(engine.render_calls) == 1
		a, k = engine.render_calls[0]
		print(a)
		
		assert card.passageUid == self.endingUid
		return True

'''
class TullieStoryTest(unittest.TestCase):
	def __init__(self, story, *args, **kwargs):
		super().__init__(*args, **kwargs)
		from stories import tullie
		self.story = tullie.story	
'''

if __name__ == "__main__":
	unittest.main()
