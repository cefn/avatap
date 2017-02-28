import unittest
from milecastles import *
from stories import tullie

def create_card():
	return Card(
		uid="abcdefgh",
		storyUid = "teststory",
		passageUid = "welcome",
		sack = dict(
			money=10,
			health=10
		)
	)


class MockBox(ConsoleBox):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.render_calls = list()
		
	def render(self, *args, **kwargs):
		self.render_calls.append((args, kwargs))
		super().render(*args, **kwargs)

class PageTest(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.num_boxes = 4
	
	def setUp(self):
		
		# configure 'story' 
		self.story = Story(
			uid="teststory"
		)
		
		self.passage = PagePassage(
			uid="welcome",
			page="Welcome to Milecastles. {instruction}",
			showBoxUid='0',
			nextPassageUid = 'welcome'
		)

		# add a circular passage
		self.story.registerPassage(self.passage)

		# configure 'boxes' containing the story
		self.boxes = dict()
		for boxPos in range(self.num_boxes):
			boxUid = str(boxPos) # keyed by a str for json encoding
			box = MockBox(uid=boxUid)
			self.boxes[boxUid]=box
			box.registerStory(self.story)
		
		# create an imaginary card
		self.card = create_card()

	def tearDown(self):
		del self.story, self.passage, self.boxes, self.card
			
	def test_show_text(self):
		showBox = self.boxes[self.passage.showBoxUid]		
		showBox.handle_card(self.card)
		assert len(showBox.render_calls) == 1
		a, k = showBox.render_calls[0]
		print(a)
		return True

if __name__ == "__main__":
	unittest.main()
