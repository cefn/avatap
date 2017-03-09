from util import ticks_ms
from boilerplate import Resolver

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
    of data structures (e.g. encouraging you to refer to myNode.uid in 
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
    required = Container.required + ["startNodeUid", "startSack"]
    defaults = dict(Container.defaults, 
        startSack = dict()
    )
                        
    def __enter__(self):
        global story
        story = self
        
    def __exit__(self, type, value, traceback):
        self.validate()
        global story
        story = None
        
    def validate(self):
        assert type(self.startSack) == dict, "'sack' must be of type dict"
        # delegate validation to nodes
        for nodeUid, node in self._getTable(Node).items():
            node.validate(self)
    
    def registerNode(self, node):
        return self._register(Node, node)
    
    def lookupNode(self, nodeUid):
        return self._lookup(Node, nodeUid)

    def registerBox(self, box):
        return self._register(Box, box)
    
    def lookupBox(self, boxUid):
        return self._lookup(Box, boxUid)
        
    def createBlankCard(self, cardUid):
        return Card(
            uid=cardUid,
            storyUid = self.uid,
            nodeUid = self.startNodeUid,
            sack = dict(self.startSack)
        )

class Card(UidItem):
    required = UidItem.required + ["storyUid", "nodeUid", "sack"]

class Box(UidItem):
    required = UidItem.required + ["label"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getStoryContext().registerBox(self) 
                        
class Node(UidItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getStoryContext().registerNode(self)

    def validate(self, story):
        pass

    def activate(self,  engine):
        pass

    def deactivate(self, engine):
        pass    
        
    def handleTap(self, engine, card):
        raise AssertionError("Not yet implemented")
        
class BoolMethodFork(ThroughNode):
    required = Node.required + ["trueNodeUid", "falseNodeUid"]
    
    def activate(self, engine):
        if self.evaluate(engine):
            engine.setNodeUid(self.trueNodeUid)
        else:
            engine.setNodeUid(self.falseNodeUid)
    
    def evaluate(self, engine):
        raise AssertionError("Not yet implemented")

class BoolExpressionFork(ThroughNode):
    required = BooleanMethodRouter.required + ["expression"]

    def evaluate(self, engine):
        return engine.evaluateExpression(self.expression)

class TemplatedNode(Node):
    required = Node.required + ["template"]

    def getTemplateString():
        return self.template
    
    def getTemplateResolver():
        return TemplateResolver(**self.__dict__)
                
    def displayTemplate(self, engine):
        engine.render(self.getTemplateString(), self.getTemplateResolver())

class VisitBoxPassage(TemplatedNode):
    required = TemplatedNode.required + ["visitBoxUid", "visitBoxText"]
    defaults = dict(TemplatedNode.defaults,
        template="{% if box.uid == node.visitBoxUid %}{{node.visitBoxText}}{% else %}{{node.otherBoxText}}{% endif %}"
        otherBoxText="Please go to {node.visitBoxLabel} to continue your adventure"
    )

    def validate(self, story):
        self.visitBoxLabel = story.lookupBox(self.visitBoxUid).label
        
class LinearPassage(VisitBoxPassage):
    required = VisitBoxPassage.required + ["nextNodeUid"]

    def getTemplateString(self, engine):
        nextNode = engine.story.lookupNode(self.getNextNodeUid())
        if isinstance(nextNode, VisitBoxPassage):
            self.nextBoxLabel = engine.story.lookupBox(nextNode.visitBoxUid).label
            if nextNode.visitBoxUid != self.visitBoxUid:
                return super().getTemplateString(engine) + "\n find {{node.nextBoxLabel}} and tap in to continue"
        return super().getTemplateString(engine) = "\n...tap to continue"
                        
    def gotoNextNode(self, engine):
        engine.setNodeUid(self.nextNodeUid)
                    
    def handleTap(self, engine):
        self.gotoNextNode(engine)
        self.displayTemplate(engine)
        
class ConfirmationPassage(LinearPassage):
    defaults = dict(StraightPassage.defaults, 
        timeout=4000
    )
    
    def handleTap(self, engine):
        now = ticks_ms()
        # progress only if tap follows quickly
        if now - self.last_tap_ms < self.timeout:
            self.progressPlayer(engine.card)
        engine.renderText(self.getRenderedText(engine))
        self.last_tap_ms = now      

class SackChangePassage(LinearPassage):
    defaults = dict(LinearPassage.defaults,
        changeCondition = None
        add = None
        remove = None
    )
    
    def validate(self, story):
        super().validate(story)
        assert self.add == None or type(self.add) == dict
        assert self.remove == None or type(self.remove) == dict
        assert hasattr(self, "add") or hasattr(self, "remove"), "SackChangePassage should have one of either 'add' or 'remove'"
    
    def handleTap(self, engine):
        if self.changeCondition == None or engine.evaluateExpression(self.changeCondition):
            sack = engine.card.sack
            # handle addition (list of entries or a number)
            if(hasattr(self, "add")):
                for key,val in self.add.items():
                    if key in sack:
                        sack[key] = sack[key] + val
                    else:
                        sack[key] = val
            # handle removal (list of entries or a number)
            if(hasattr(self, "remove)):
                for key,val in self.remove:
                    if key in sack:                        
                        if type(val) == list:
                            for entry in val:
                                sack[key].remove(entry)
                        else:
                            sack[key] = sack[key] - entry
        # now run the main routine
        super().handleTap(engine)
        
'''
# superceded by 'script' attribute which is evaluated in the context of a tap (e.g. "sack.money = sack.money + 5")
# See also https://twine2.neocities.org/1.html for Twine reference features around variables and execution
class ExecutePassage(StraightPassage):
    pass
'''

'''
class WaitPassage(StraightPassage):
    pass
'''    
    
class ChoicePassageFork(VisitBoxPassage):
    required = VisitBoxPassage.required + ["choices"]
    
    def validate(self, story):
        print( "Validating Node:" + self.uid.idString)
        choices = self.choices
        assert type(choices) == dict, "'choices' is not a dict mapping box uids to string templates as expected"
        assert all([isinstance(val, str) for val in choices]), "'choices' property template values are not all of type 'str'"
        choiceNodeUids = choices.keys()
        assert all([isinstance(key, Uid) for key in choiceNodeUids]), "'choices' property uid keys are not all of type 'Uid'"
        choiceNodes = [story.lookupNode(nodeUid) for nodeUid in choiceNodeUids]
        assert all([isinstance(node, VisitBoxNode) for node in choiceNodes]), "ChoiceFork choices must point to subclasses of VisitBoxNode"
        choiceBoxUids = [node.visitBoxUid for node in choiceNodes]
        assert len(choiceBoxUids) == len(set(choiceBoxUids)), "Some VisitBoxNodes referenced by 'choices' share the same box" + str(choiceBoxUids)
        choiceBoxes = [engine.story.lookupBox(boxUid) for boxUid in choiceBoxUids]
        # record nodes and boxes
        self.choiceNodes = choiceNodes
        self.choiceBoxes = choiceBoxes

    def getTemplateString(self, engine):
        try:
            # find the matching choice, if it exists
            choiceBoxUids = [box.uid for box in self.choiceBoxes]
            chosenPos = choiceBoxUids.index(engine.box.uid)
            chosenNode = chosenNodes[choiceIndex]
            engine.setNodeUid(chosenNode.uid)
            return "You chose: " + self.choices[chosenNode.uid] + "\n... now tap to continue"
        except ValueError:
            # box not in list of choices
            # render the choice string
            choiceString = ""
            for choiceNode,choicePos in enumerate(self.choiceNodes):
                choiceString += "\n" + self.choices[choiceNode.uid] + " : " + self.choiceBoxes[choicePos].label
            if engine.box.uid == self.visitBoxUid:
                # it's the visit box, render the page
                return super().getTemplateString(engine) + choiceString
            else:
                # it's not the visit box
                return "This box is not among your choices. To continue the game..." + choiceString

'''
def constructLinearSequence(inboundUid, outboundUid, templates):
    templates = list(templates)
    templates.reverse()
    toUid = outboundUid
    for template,pos in enumerate(templates):
'''        
        
# Condition render
# and text rendering from sack
# Condition routing
# Test Verification of story
# Rendering as graph
