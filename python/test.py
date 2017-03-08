import unittest
from milecastles import *
from engines import Engine

class MockEngine(Engine):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.render_calls = list()
		
	def renderText(self, *args, **kwargs):
		self.render_calls.append((args, kwargs))
		
# create uids to wire up/trigger story+passages
storyUid = Uid("teststory")
passageUids = [Uid(name) for name in [
	"landingPassage",
	"endingPassage",
]]
boxUids = [Uid(name) for name in [
	"northBox",
	"eastBox",
	"southBox",
	"westBox"
]]

# populate into an item using a dict
#import pdb; pdb.set_trace()
uids = UidRegistry(*boxUids+passageUids)

class EngineContainer(AnonymousContainer):
	def registerEngine(self, engine):
		return self._register(Engine, engine)
	
	def lookupEngine(self, engineUid):
		return self._lookup(Engine, engineUid)	
	
class PageTest(unittest.TestCase):
	
	def __init__(self, *a, **k): # note multiple inheritance
		super().__init__(*a, **k)
		self.num_boxes = 4
		
	def setUp(self):

		# create 'story' 
		self.story = Story(
			uid=storyUid,
			startPassageUid=uids.landingPassage
		)
		
		with self.story:

			# configure boxes			
			for boxUid in boxUids:
				Box(uid=boxUid, label="The box called " + boxUid.idString) 
			
			# create a beginning passage which points to the end passage
			PagePassage(
				uid=uids.landingPassage,
				rightBoxUid=uids.northBox,
				rightBoxText="Welcome to Milecastles.",
				nextPassageUid=uids.endingPassage
			)

			# create an ending passage for the story
			PagePassage(
				uid=uids.endingPassage,
				rightBoxUid=uids.southBox,
				rightBoxText="You have finished your adventure",
				nextPassageUid=uids.landingPassage			)
		
		# configure engine for each box in the story
		self.engines = EngineContainer()
		for boxIdString,box in self.story._get_table(Box).items():
			engine = MockEngine(uid=boxIdString, box=box)
			engine.registerStory(self.story)
			self.engines.registerEngine(engine)

	def tearDown(self):
		del self.engines, self.story
			
	def test_show_text(self):
		# create an imaginary card
		card = self.story.createBlankCard("abcdefgh")
				
		# present the card to the relevant engine
		engine = self.engines.lookupEngine(uids.northBox)
		
		#import pdb; pdb.set_trace()

		engine.handleCard(card)

		# check results
		assert len(engine.render_calls) == 1
		a, k = engine.render_calls[0]
		print(a)
		
		assert card.passageUid == uids.endingPassage
		return True

'''
class TullieStoryTest(unittest.TestCase):
	def __init__(self, story, *args, **kwargs):
		super().__init__(*args, **kwargs)
		from stories import tullie
		self.story = tullie.story	
'''

'''
loader = unittest.defaultTestLoader

def suite():
    suite = unittest.TestSuite()
    suite.addTest(PageTest())
    return suite
'''

if __name__ == "__main__":
	unittest.main()
