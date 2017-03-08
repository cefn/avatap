from util import ticks_ms

story = None

def loadStory(storyIdString):
    storyModulePath = "stories." + storyIdString
    print("Loading story from " + storyModulePath)
    loaded = __import__(storyModulePath)
    module = getattr(loaded, storyIdString)
    return module.story
    
def getStoryContext():
    global story
    assert story != None, "Code needs to execute in a `with story:` block"
    return story

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

# valid types which can be passed as the 'uid' value when creating an item
uidInitTypes = [type(None), Uid, str]

'''
Base class which treats all named arguments as attributes and 
all positional arguments as dicts containing named attributes
'''
class Item(object):
    required=[]
    defaults={}
    
    # populate attributes from positional dicts and keyword args
    def __init__(self, *args, **kwargs): 
        # assume positional arguments are dicts
        for data in args: # exclude self
            assert type(data)==dict, "non-dict passed to Item#__init__()"
            for key in data: 
                setattr(self, key, data[key])
        # assume keyword arguments specify attributes
        for key in kwargs:
            suffix = "uid"
            # check that uids are typed as Uid
            if key.lower().endswith(suffix):
                uidType = type(kwargs[key])
                assert uidType == Uid or uidType == type(None), "Attribute '{0}' with name ending '1' is actually of type {2}".format(key, suffix, str(uidType))
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

# Class which simplifies handling a list of idStrings or Uids and exposing them as attributes on an object, named by idString
class UidRegistry(Item):
        def __init__(self,  *a):
            uidDict = dict()
            for uid in a:
                if type(uid)==str:
                    uid = Uid(uid)
                if type(uid)!=Uid:
                    import pdb; pdb.set_trace()
                assert type(uid)==Uid
                uidDict[uid.idString]=uid
            super().__init__(**uidDict)

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
        if "uid" in k:
            uid = k["uid"]
            uidType = type(uid)
            assert uidType in uidInitTypes, "'uid' is of '{}'. Uids must be one of ()".format(str(uidType),str(uidInitTypes))
            if type(uid) == str: # cast strings to Uid
                k["uid"]=Uid(uid)
        super().__init__(*a,**k)
                
class Container(UidItem):
    
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
            raise AssertionError("'" + uid.idString + "' not in " + cls.__name__ + " lookup table")
            
class AnonymousContainer(Container):
    required = [n for n in Container.required if n!="uid"]
    
class Story(Container):
    required = Container.required + ["startPassageUid"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                    
    def __enter__(self):
        global story
        story = self
        
    def __exit__(self, type, value, traceback):
        global story
        story = None
    
    def registerPassage(self, passage):
        return self._register(Passage, passage)
    
    def lookupPassage(self, passageUid):
        return self._lookup(Passage, passageUid)

    def registerBox(self, box):
        return self._register(Box, box)
    
    def lookupBox(self, boxUid):
        return self._lookup(Box, boxUid)
        
    def createBlankCard(self, cardUid):
        return Card(
            uid=cardUid,
            storyUid = self.uid,
            passageUid = self.startPassageUid,
            sack = dict(
                money=100
            )
        )

class Card(UidItem):
    required = UidItem.required + ["storyUid", "passageUid", "sack"]

class Box(UidItem):
    required = UidItem.required + ["label"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getStoryContext().registerBox(self) 
                        
class Passage(UidItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global story
        story.registerPassage(self)

    def activate(self,  engine):
        raise AssertionError("Not yet implemented")
        
    def getRenderedDict(self, engine):
        d = dict()
        
        # populate using all primitive attributes of Passage
        for key,value in self.__dict__.items():
            valType = type(value)
            if valType==str or valType==int or valType==float or valType==bool:
                d[key]=str(value)
        
        # populate using all attributes of sack
        for key,value in engine.card.sack.items():
            assert key not in d, "Error processing sack value. RenderedDict already contains '" + key + "'"
            d[key]=value
        
        return d
        
    def getRenderedText(self, engine):
        d = self.getRenderedDict(engine)
        nextT = self.getRenderedTemplate(engine)
        prevT = None
        try:
            while nextT != prevT: # repeats until formatted text is the same as unformatted
                prevT = nextT
                nextT = prevT.format(**d)
            return nextT
        except KeyError as k:
            import pdb; pdb.set_trace()
            raise k
        
    def getRenderedTemplate(self):
        raise AssertionError("Not yet implemented")
        
    def handleTap(self, engine, card):
        raise AssertionError("Not yet implemented")

class BoxPassage(Passage):
    required = Passage.required + ["rightBoxUid", "rightBoxText"]
    defaults = dict(Passage.defaults, 
        wrongBoxText="Please go to {rightBoxLabel} to continue your adventure"
    )
    
    def getRenderedDict(self, engine):
        d = super().getRenderedDict(engine)
        d.update(
            rightBoxLabel = engine.story.lookupBox(self.rightBoxUid).label
        )
        return d

    def getRenderedTemplate(self, engine):
        box = engine.box
        if box.uid == self.rightBoxUid:
            return "{rightBoxText}"
        else:
            return "{wrongBoxText}"

class PagePassage(BoxPassage):
    required = BoxPassage.required + ["nextPassageUid"]
    
    def getNextPassage(self, engine):
        return engine.story.lookupPassage(self.nextPassageUid)
    
    def getNextBox(self, engine):
        nextPassage = self.getNextPassage(engine)
        return engine.story.lookupBox(nextPassage.rightBoxUid)      
        
    def getRenderedDict(self, engine):
        d = super().getRenderedDict(engine)
        d.update(
            nextBoxLabel=self.getNextBox(engine).label
        )
        return d
            
    def getRenderedTemplate(self, engine):
        template = super().getRenderedTemplate(engine)
        nextPassage = self.getNextPassage(engine)
        if self.rightBoxUid == nextPassage.rightBoxUid:
            return template + "\n...tap to continue"
        else:
            return template + "\n...now go to {nextBoxLabel}"

    def progress_player(self, engine):
        engine.card.passageUid = self.nextPassageUid
                    
    def handleTap(self, engine):
        self.progress_player(engine)
        engine.renderText(self.getRenderedText(engine))
        
class ConfirmationPassage(PagePassage):
    defaults = dict(PagePassage.defaults, 
        tapTime=4000
    )
    
    def handleTap(self, engine):
        now = ticks_ms()
        # progress only if tap follows quickly
        if now - self.last_tap_ms < self.tapTime:
            self.progress_player(engine.card)
        engine.renderText(self.getRenderedText(engine))
        self.last_tap_ms = now      

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
    
class ConditionalPassage(Passage):
        def checkCondition(self,  engine):
            raise AssertionError("Not yet implemented")


# Condition render
# and text rendering from sack
# Condition routing
# Test Verification of story
# Rendering as graph
