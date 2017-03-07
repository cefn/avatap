story = None

def loadStory(storyIdString):
	global story
	story = __import__("stories." + storyIdString).story

'''
Base class which treats all named arguments as attributes and 
all positional arguments as dicts containing named attributes
'''
class Item(object):
	required=[]
	defaults={}
	
	# populate attributes from positional and
	def __init__(self, *args, **kwargs): 
		for data in args[1:]: # exclude self
			for key in data:
				setattr(self, key, data[key])
		for key in kwargs:
			# check that uids are typed as Uid
			if key.lower().endswith("uid"):
				uidType = type(kwargs[key])
				if not(uidType==Uid):
					raise AssertionError("Attribute " + key + " with name ending 'uid' is actually of type " + uidType.__name__)
			setattr(self, key, kwargs[key])

		# raise error if any 'required' attributes are missing   
		missing = list()
		for name in type(self).required:
			if not(hasattr(self, name)):
				missing.append(name)
		if len(missing) > 0:
			raise AssertionError(type(self).__name__ + " missing required attributes " + str(missing) )
		
		for key in type(self).defaults:
			if not hasattr(self, key):
				setattr(self, key, type(self).defaults[key])
				
class Container(Item):
	
	def _get_table(self, cls):
		if not(hasattr(self, 'registry')):
			self.registry = dict()
		if not(cls.__name__ in self.registry):
			 self.registry[cls.__name__]=dict()
		return self.registry[cls.__name__]
		
	'''register any subclass of item to be looked up later by its id'''
	def _register(self, cls, item):
		table = self._get_table(cls)
		if not(item.uid.idString in table):
			table[item.uid.idString]=item
		else:
			raise AssertionError("Lookup table for " + cls.__name__ + " already contains item with uid" + item.uid.idString)

	''''''
	def _lookup(self, cls, uid):
		if not(type(uid) == Uid):		
			raise AssertionError("Attempted lookup with type" + type(uid) + "; should be Uid")	
		else:
			if hasattr(self, "registry"):
				if cls.__name__ in self.registry:
					table = self.registry[cls.__name__]
					if uid.idString in table:
						return table[uid.idString]
			import pdb; pdb.set_trace()

			raise AssertionError("'" + uid.idString + "' not in " + cls.__name__ + " lookup table")


class Uid:
	def __init__(self, idString):
		self.idString = idString

	"""Override the default Equals behavior"""
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.idString == other.idString
		return False

	def __neq__(self, other):
		return not self.__eq__(other)
		
	def __hash__(self):
		return hash(type(self).__name__) ^ hash(self.idString)

'''
	A common superclass for items with ids. Accepts a string id argument
	and silently replaces it with a typed Uid object which is required 
	by other Uid oriented references, this supports implicit validation 
	of data structures (e.g. encouraging you to refer to myPassage.uid in 
	preference to the possibly "theuid")
'''	
class UidItem(Item):
	required = Item.required + ["uid"]
	def __init__(self, *a, **k):
		# intercept string uids, turn into Uid objects
		uid = k["uid"]
		if type(uid) == str:
			k["uid"]=Uid(uid)
		super().__init__(*a,**k)
	
class Story(Container):
	required = Container.required + ["startPassageUid"]
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
			
	def registerPassage(self, passage):
		return self._register(Passage, passage)
	
	def lookupPassage(self, passageUid):
		return self._lookup(Passage, passageUid)

	def registerBox(self, box):
		return self._register(Box, box)
	
	def lookupBox(self, boxUid):
		return self._lookup(Box, boxUid)

class Card(UidItem):
	required = UidItem.required + ["storyUid", "passageUid", "sack"]


class Box(UidItem):
	required = UidItem.required + ["label"]
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.story.registerBox(self)
						
class Passage(UidItem):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.story.registerPassage(self)
		
	def handle_tap(self, engine, card):
		raise AssertionError("Not yet implemented")

class PagePassage(Passage):
	required = Passage.required + ["rightBoxUid", "rightText", "nextPassageUid"]
	defaults = dict(Passage.defaults, **{
		"wrongText":None
	})
	
	def __init__(self, *a, **k):
		super().__init__(*a,**k)
					
	def handle_tap(self, engine, card):
		box = engine.box
		import pdb; pdb.set_trace()
		if box.uid == self.rightBoxUid:
			nextPassage = self.story.lookupPassage(self.nextPassageUid)
			card.passageUid = nextPassage.uid
			if self.rightBoxUid == nextPassage.rightBoxUid:
				engine.render(self.rightText + "\n...tap to continue")
			else:
				engine.render(self.rightText + "\n...now go to " + self.story.lookupBox(nextPassage.rightBoxUid).label)				
		else:
			if self.wrongText == None:
				wrongText = "Please go to " + self.story.lookupBox(self.rightBoxUid).label + " to continue your adventure"
			else:
				wrongText = self.wrongText
			engine.render(wrongText)
		
'''
A passage which displays its text on tap, then requires you to tap 
again to confirm navigation within a certain time. Failing to tap would 
ConfirmationPassage(Passage):
	def handle_tap():
'''
		

'''
# superceded by 'script' attribute which is evaluated in the context of a tap (e.g. "sack.money = sack.money + 5")
# See also https://twine2.neocities.org/1.html for Twine reference features around variables and execution
class ExecutePassage(PagePassage):
	pass
'''

'''
class WaitPassage(PagePassage):
	pass
'''

class ChoicePassage(PagePassage):
	pass
	
class ConditionalPassage(PagePassage):
	pass


# Condition render
# and text rendering from sack
# Condition routing
# Test Verification of story
# Rendering as graph

class ConsoleBox(Box):
	def render(self, text):
		print(text)
