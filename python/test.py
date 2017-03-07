import unittest
from milecastles import *
from engines import Engine

class MockEngine(Engine):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.render_calls = list()
		
	def render(self, *args, **kwargs):
		self.render_calls.append((args, kwargs))

class PageTest(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.num_boxes = 4
		
	def setUp(self):

		# configure 'story' 
		self.storyUid = Uid("teststory")
		story = Story(
			uid=self.storyUid
		)

		# configure boxes
		self.boxes = [Box(story=story, uid=str(boxPos), label="The box called " + str(boxPos)) for boxPos in range(self.num_boxes)]
		
		# configure engines
		self.engines = [MockEngine(box=box) for box in self.boxes]
		for engine in self.engines:
			engine.registerStory(story)

		# create passage uids to wire up passages
		self.landingUid = Uid("landing")
		self.endingUid = Uid("ending")

		# create a beginning passage which points to the end passage
		PagePassage(story=story,
			uid=self.landingUid,
			rightBoxUid=self.engines[0].box.uid,
			rightText="Welcome to Milecastles.",
			nextPassageUid=self.endingUid
		)

		# create an ending passage for the story
		PagePassage(story=story,
			uid=self.endingUid,
			rightBoxUid=self.engines[1].box.uid,
			rightText="You have finished your adventure",
			nextPassageUid=self.landingUid
		)
		

	def tearDown(self):
		del self.boxes, self.engines, self.storyUid, self.landingUid, self.endingUid
			
	def test_show_text(self):
		# create an imaginary card
		card = Card(
			uid="abcdefgh",
			storyUid =self.storyUid,
			passageUid = self.landingUid,
			sack = dict(
				money=10,
				health=10
			)
		)
				
		# present the card to the relevant engine
		engine = self.engines[0]
		
		#import pdb; pdb.set_trace()

		engine.handle_card(card)

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
