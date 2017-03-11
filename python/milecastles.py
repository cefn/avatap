from agnostic import ticks_ms
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
            assert type(data)==dict, "Item#__init__() can only handle 'dict' arguments"
            for key in data: 
                setattr(self, key, data[key])
        # assume keyword arguments specify attributes
        for key in kwargs:
            setattr(self, key, kwargs[key])

        # populate with defaults
        for key in type(self).defaults:
            if not hasattr(self, key):
                setattr(self, key, type(self).defaults[key])

        # raise error if any 'required' attributes are missing   
        missing = list()
        for name in type(self).required:
            if not(hasattr(self, name)):
                missing.append(name)
        if len(missing) > 0:
            raise AssertionError(type(self).__name__ + " missing required attributes " + str(missing) )
        
'''
    A common superclass for items with ids. Accepts a string id argument
    and silently replaces it with a typed Uid object which is required 
    by other Uid oriented references, this supports implicit validation 
    of data structures (e.g. encouraging you to refer to myNode.uid in 
    preference to the possibly "theuid")
''' 
class UidItem(Item):
    required = Item.required + ["uid"]
                
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
        if not(item.uid in table):
            table[item.uid]=item
        else:
            raise AssertionError("Lookup table for " + cls.__name__ + " already contains item with uid" + item.uid)

    ''''''
    def _lookup(self, cls, uid):
        if hasattr(self, "registry"):
            if cls.__name__ in self.registry:
                table = self.registry[cls.__name__]
                if uid in table:
                    return table[uid]
        raise AssertionError("'" + uid + "' not in " + cls.__name__ + " lookup table")
            
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
        # construct an easy dot lookup mechanism from within templates
        self.nodes = Item(**self._get_table(Node))
        self.boxes = Item(**self._get_table(Box))
        # delegate validation to nodes
        for nodeUid, node in self._get_table(Node).items():
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
        # lookup box/node uids, generate new attributes pointing to boxes and nodes
        print("Validating " + type(self).__name__ + " with uid " + self.uid)
        uidSuffix = "Uid"
        for cls in [Node, Box]:
            clsSuffix = (cls.__name__ + uidSuffix)
            for key in kwargs:
                if key.endswith(clsSuffix):
                    uidPrefix = key[:-len(uidSuffix)] 
                    item = story._lookup(cls, getattr(self, key))
                    setattr(self, itemKey, item)
                    
        # allow plugins to validate themselves
        self.plugins = []
        for key,val in self.__dict__.items():
            if isinstance(val, NodePlugin):
                plugins.append(val)

    def activate(self,  engine):
        for plugin in self.plugins:
            plugin.activate(engine)

    def deactivate(self, engine):
        for plugin in self.plugins:
            plugin.deactivate(engine)
        
    def handleTap(self, engine):
        for plugin in self.plugins:
            plugin.handleTap(engine)

class NodePlugin(Item):

    def validate(self, story):
        pass

    def activate(self,  engine):
        pass

    def deactivate(self, engine):
        pass    
        
    def handleTap(self, engine):
        pass

# See also https://twine2.neocities.org/1.html for Twine reference features around variables and execution
class SackChange(NodePlugin):
    defaults = dict(NodePlugin.defaults,
        trigger = None,
        stayPositive = True,
    )
    
    def validate(self, story):
        assert hasattr(self, "assign") or hasattr(self, "plus") or hasattr(self, "minus"), "SackChangePage should have one of either 'assign', 'plus' or 'minus'"
        assert not(hasattr("assign") or type(self.assign) == dict,  "SackChange assign should be of type dict"
        assert not(hasattr("plus")   or type(self.plus) == dict,    "SackChange plus should be of type dict"
        assert not(hasattr("minus")  or type(self.minus) == dict,   "SackChange minus should be of type dict"
                           
    def activate(self, engine):
        self.reset()
        if self.trigger == None or engine.evaluateExpression(self.trigger):
            self.triggered = True
            sack = engine.card.sack
            
            if self.stayPositive:
                # check if minus transactions might incorrectly send a value negative
                if(hasattr(self, "minus")):
                    for key,val in self.minus:
                        if key not in sack or sack[key] <= val:
                            self.completed = False
                            return                        
            # can trigger change(s)
            
            # handle setting (any python value)
            if(hasattr(self, "assign")):
                for key,val in self.assign:
                    sack[key]=val
            # handle addition (to a number)
            if(hasattr(self, "plus")):
                for key,val in self.plus.items():
                    if key in sack:
                        sack[key] = sack[key] + val
                    else:
                        sack[key] = val
            # handle removal (from a number)
            if(hasattr(self, "minus")):
                for key,val in self.minus:
                    if key in sack:
                        sack[key] = sack[key] - entry
                    else:
                        sack[key] = - val
            self.completed = True

    def deactivate(self, engine):
        self.reset() # for paranoia, to ensure nothing reads old state by mistake

    def reset():
        del self.triggered, self.completed

class ConditionFork(Node):
    required = Node.required + ["condition", "trueNodeUid", "falseNodeUid"]

    def activate(self, engine):
        super().activate(engine)
        if self.evaluate(engine):
            engine.setNodeUid(self.trueNodeUid)
        else:
            engine.setNodeUid(self.falseNodeUid)

    def evaluate(self, engine):
        return engine.evaluateExpression(self.condition)

class Page(Node):
    required = Node.required + ["page"]

    def getTemplateString(self, engine):
        return self.page
    
    def getTemplateResolver(self, engine):
        return Resolver(**self.__dict__)
                
    def displayTemplate(self, engine):
        engine.renderTemplate(self.getTemplateString(engine), self.getTemplateResolver(engine))

class VisitPage(Page):
    required = Page.required + ["visitBoxUid", "visitBoxText"]
    defaults = dict(Page.defaults,
        page="""{% if box == node.visitBox %}{%include 'visitBoxText' %}{% else %}{% include 'otherBoxText' %}{% endif %}""",
        otherBoxText="Please go to {{node.visitBoxLabel}} to continue your adventure"
    )
        
class LinearPage(VisitPage):
    required = VisitPage.required + ["nextNodeUid"]
                            
    def gotoNextNode(self, engine):
        engine.setNodeUid(self.nextNodeUid)
                    
    def handleTap(self, engine):
        super.handleTap(engine)
        self.displayTemplate(engine)
        if engine.box.uid == self.visitBoxUid:
            self.gotoNextNode(engine)
        
"""
class ConfirmationPage(LinearPage):
    defaults = dict(LinearPage.defaults, 
        timeout=4000
    )
    
    def handleTap(self, engine):
        now = ticks_ms()
        # progress only if tap follows quickly
        if now - self.last_tap_ms < self.timeout:
            self.progressPlayer(engine.card)
        engine.renderText(self.getRenderedText(engine))
        self.last_tap_ms = now          

class WaitPage(LinearPage):
    pass
"""    
    
class ChoicePage(VisitPage):
    required = VisitPage.required + ["choices"]
    
    def validate(self, story):
        super().validate(story)
        
        nodeTable = story._get_table(Node)
        boxTable = story._get_table(Box)
        
        choices = self.choices

        assert type(choices) == dict, "'choices' must be a dict mapping node uids to string templates. Cannot accept " + str(choices)
        choiceTemplates = choices.values()
        choiceNodeUids = choices.keys()        
        
        badTemplates = [val for val in choiceTemplates if not(isinstance(val, str))]
        assert len(badTemplates)==0, "ChoicePage: choice templates must be string values. Cannot accept " + str(badTemplates)
        
        badNodeUids = [val for val in choiceNodeUids if not(val in nodeTable)]
        assert len(badNodeUids)==0, "ChoicePage: choice node uid values must be found in story table. Cannot accept " + str(badNodeUids)

        choiceNodes = [story.lookupNode(nodeUid) for nodeUid in choiceNodeUids]        
        badNodes = [val for val in choiceNodes if not(isinstance(val, VisitPage))]
        assert len(badNodes) == 0, "ChoiceFork choices must point to subclasses of VisitPage. Cannot accept " + str(badNodes)
        
        choiceBoxUids = [node.visitBoxUid for node in choiceNodes]
        badBoxUids = [val for val in choiceBoxUids if not(val in boxTable)]
        assert len(badBoxUids)==0, "ChoicePage: box uid values must be found in story table. Cannot accept " + str(badBoxUids)
        assert len(choiceBoxUids) == len(set(choiceBoxUids)), "Some VisitBoxNodes referenced by 'choices' share the same box. Cannot accept " + str(choiceBoxUids)

        choiceBoxes = [story.lookupBox(boxUid) for boxUid in choiceBoxUids]
        
        # save nodes and boxes
        self.choiceNodes = choiceNodes
        self.choiceBoxes = choiceBoxes

    def getTemplateString(self, engine):
        try:
            # find the matching choice, if it exists, and respond
            choiceBoxUids = [box.uid for box in self.choiceBoxes]
            chosenPos = choiceBoxUids.index(engine.box.uid)
            chosenNode = self.choiceNodes[chosenPos]
            engine.setNodeUid(chosenNode.uid)
            return "You chose: " + self.choices[chosenNode.uid] + "\n... now tap to continue"
        except ValueError:
            # box not in list of choices
            # render the choice string
            choiceString = ""
            for choiceNode,choicePos in enumerate(self.choiceNodes):
                choiceString += "\n" + self.choices[choiceNode.uid] + " : " + self.choiceBoxes[choicePos].label
            if engine.box.uid == self.visitBoxUid:
                # it's the visit box, render the page as normal
                return super().getTemplateString(engine) + choiceString
            else:
                # it's not the visit box, bypass rendering the page
                return "This box is not among your choices. To continue the game..." + choiceString

'''
def constructLinearSequence(inboundUid, outboundUid, pages):
    pages = list(pages)
    pages.reverse()
    toUid = outboundUid
    for page,pos in enumerate(pages):
'''        
        
# Condition render
# and text rendering from sack
# Condition routing
# Test Verification of story
# Rendering as graph
