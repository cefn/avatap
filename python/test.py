import unittest
from milecastles import *
from engine import Engine

from stories import exampleShort


class MockEngine(Engine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.render_calls = list()

    def displayText(self, *args, **kwargs):
        self.render_calls.append((args, kwargs))


class EngineContainer(AnonymousContainer):
    def registerEngine(self, engine):
        return self._register(Engine, engine)

    def lookupEngine(self, engineUid):
        return self._lookup(Engine, engineUid)


class PageTest(unittest.TestCase):
    def __init__(self, *a, **k):  # note multiple inheritance
        super().__init__(*a, **k)
        self.num_boxes = 4

    def setUp(self):
        # create 'story'
        self.story = exampleShort.story
        # configure engine for each box in the story
        self.engines = dict()
        boxTable = self.story._get_table(Box)
        for boxIdString, box in boxTable.items():
            engine = MockEngine(box=box)
            engine.registerStory(self.story)
            self.engines[boxIdString] = engine

    def tearDown(self):
        del self.engines, self.story

    def test_show_text(self):
        # create an imaginary card
        card = self.story.createBlankCard("abcdefgh")

        # present the card to the relevant engine
        engine = self.engines[exampleShort.northBox.uid]

        # import pdb; pdb.set_trace()

        engine.handleCard(card)

        # check results
        assert len(engine.render_calls) == 1
        a, k = engine.render_calls[0]
        print(a)

        assert card.nodeUid == "ending"
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
