from agnostic import ticks_ms

story = None

signature = "engine, story, box, node, card, sack"

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

class Holder(object):
    def __init__(self, *a, **k):
        for key,val in k.items():
            setattr(self, key, val)

'''
Base class which treats all named arguments as attributes and 
all positional arguments as dicts containing named attributes
'''
class Item(Holder):
    required=[]
    optional=[]
    defaults={}
    
    # populate attributes from positional dicts and keyword args
    def __init__(self, *a, **k):
        super().__init__(self, *a, **k)

        itemType = type(self)
        itemTypeName = itemType.__name__
        itemRequired = itemType.required
        itemOptional = itemType.optional
        itemDefaults = itemType.defaults
                
        # populate missing attributes from defaults
        for key,val in itemDefaults.items():
            if not hasattr(self, key):
                setattr(self, key, val)

        # raise error if any 'required' attributes still missing   
        missing = list()
        for name in itemRequired:
            if not(hasattr(self, name)):
                missing.append(name)
        if len(missing) > 0:
            raise AssertionError(itemTypeName + " missing required attributes " + str(missing) )

        # check no unexpected keys passed        
        for key,val in k.items(): 
            assert key in itemRequired or key in itemDefaults or key in itemOptional, itemTypeName + " unexpected parameter '" + key + "'"
        
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
            raise AssertionError(type(self).__name__ + ": " +  cls.__name__ + " table already contains '" + item.uid + "'")

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
        
    def __exit__(self, exceptionType, exceptionValue, exceptionTrace):
        global story
        story = None
        
        if exceptionType == None :
            self.validate()
        else:
            raise exceptionValue
               
    def validate(self):
        assert type(self.startSack) == dict, "'sack' must be of type dict"
        # construct an easy dot lookup mechanism from within templates
        self.nodes = Holder(**self._get_table(Node))
        self.boxes = Holder(**self._get_table(Box))
        # delegate validation to nodes
        for nodeUid, node in self._get_table(Node).items():
            try:
                node.validate(self)
            except Exception as e:
                print("Problem validating Node, uid:" + node.uid)
                raise e
    
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
    required = UidItem.required + ["label", "description"]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getStoryContext().registerBox(self) 
                        
class Node(UidItem):
    defaults = dict(UidItem.defaults, 
        change = None
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getStoryContext().registerNode(self)

    def validate(self, story):
        # lookup box/node uids, generate new attributes pointing to boxes and nodes
        print("Validating " + type(self).__name__ + " with uid " + self.uid)
        uidSuffix = "Uid"
        for cls in [Node, Box]:
            clsSuffix = (cls.__name__ + uidSuffix)
            for key in dict(self.__dict__):
                if key.endswith(clsSuffix):
                    uidPrefix = key[:-len(uidSuffix)] 
                    item = story._lookup(cls, getattr(self, key))
                    setattr(self, uidPrefix, item)
                    
        # allow operators to validate themselves
        self.operators = []
        for key,val in self.__dict__.items():
            if isinstance(val, NodeOperator):
                self.operators.append(val)
                val.validate(story)
                
    def getGoalBoxUid(self, story):
        return None

    def getGoalBox(self, story):
        goalBoxUid = self.getGoalBoxUid(story)
        if(goalBoxUid != None):
            return story.lookupBox(goalBoxUid)
        return None
        
    def activate(self, engine):
        for operator in self.operators:
            operator.operate(engine)
        return None

    def render(self,  engine):
        return None

    def deactivate(self,  engine):
        return None
        
class NodeOperator(Item):

    def validate(self, story):
        pass

    def operate(self,  engine):
        pass
        
# See also https://twine2.neocities.org/1.html for Twine reference features around variables and execution
class SackChange(NodeOperator):
    optional = ["trigger", "assign","plus","minus","reset"]
    defaults = dict(NodeOperator.defaults,
        stayPositive = True,
    )
    
    def validate(self, story):
        assert hasattr(self, "assign") or hasattr(self, "plus") or hasattr(self, "minus") or hasattr(self, "reset"), type(self).__Name__ + " should have one of either 'assign', 'plus', 'minus' or 'reset'"
        assert not(hasattr(self, "reset"))  or ( not(hasattr(self, "assign")) and not(hasattr(self, "plus")) and not(hasattr(self, "minus")) ), type(self).__Name__ + " reset is incompatible with assign, plus or minus"
        assert not(hasattr(self, "assign")) or type(self.assign) == dict, type(self).__Name__ + " assign should be'" + str(dict)
        assert not(hasattr(self, "plus"))   or type(self.plus) == dict,   type(self).__Name__ + " plus should be"    + str(dict)
        assert not(hasattr(self, "minus"))  or type(self.minus) == dict,  type(self).__Name__ + " minus should be"   + str(dict)
        assert not(hasattr(self, "reset"))  or type(self.reset) == dict,  type(self).__Name__ + " reset should be"   + str(dict)
                           
    def operate(self, engine):
        # reset the flags
        self.triggered = False
        self.completed = False
        # process logic
        if not(hasattr(self, "trigger")) or engine.evaluateExpression(self.trigger):
            self.triggered = True
            sack = engine.card.sack
            
            if self.stayPositive:
                # check if 'minus' transactions might incorrectly send a value negative
                if(hasattr(self, "minus")):
                    for key,val in self.minus.items():
                        if key not in sack or sack[key] <= val:
                            # refuse the change
                            self.completed = False
                            return                        
            # can trigger change(s)
            
            # handle setting (any python value)
            if hasattr(self, "assign"):
                for key,val in self.assign.items():
                    sack[key]=val
            # handle addition (to a number)
            if hasattr(self, "plus"):
                for key,val in self.plus.items():
                    if key in sack:
                        sack[key] = sack[key] + val
                    else:
                        sack[key] = val
            # handle removal (from a number)
            if hasattr(self, "minus"):
                for key,val in self.minus.items():
                    if key in sack:
                        sack[key] = sack[key] - val
                    else:
                        sack[key] = - val
            
            if hasattr(self, "reset"):
                engine.card.sack = dict(self.reset)
            
            self.completed = True

class ConditionFork(Node):
    required = Node.required + ["condition", "trueNodeUid", "falseNodeUid"]

    def evaluate(self, engine):
        return engine.evaluateExpression(self.condition)
    
    def activate(self, engine):
        if self.evaluate(engine):
            return self.trueNodeUid
        else:
            return self.falseNodeUid    

    def getGoalBoxUid(self, story):
        trueBoxUid = story.lookupNode(self.trueNodeUid).getGoalBoxUid(story)
        falseBoxUid = story.lookupNode(self.falseNodeUid).getGoalBoxUid(story)
        if trueBoxUid == falseBoxUid: # well-defined only if true and false have same goal box
            return trueBoxUid
        else:
            raise AssertionError("Cannot derive goal box for " + type(self).__name__ + "true and false boxes differ")            

# TODO add loading logic which removes preceding spaces and space sequences > 1, making declaration easier
class Page(Node):
    required = Node.required + ["page"]
    defaults = dict(Node.defaults,
        template = " {% include 'page' " + signature + " %}"
    )
                    
    def render(self, engine):
        return self.template

class GoalPage(Page):
    required = Page.required + ["goalBoxUid"]
    defaults = dict(Page.defaults,
        missTemplate="Please go to {{node.goalBox.label}} to continue your adventure"
    )
    
    def getGoalBoxUid(self, story):
        return self.goalBoxUid

    def render(self, engine):
        if engine.box == self.goalBox:
            return self.template # render as usual
        else:
            return self.missTemplate            # render a miss
        
class ThroughPage(GoalPage):
    required = GoalPage.required + ["nextNodeUid"]
        
    def deactivate(self, engine):
        # progress the player to the next node once rendered
        if engine.box == self.goalBox:
            engine.setNodeUid(self.nextNodeUid)

"""
class ConfirmationPage(ThroughPage):
    defaults = dict(ThroughPage.defaults, 
        timeout=4000
    )
    
    def handleTap(self, engine):
        now = ticks_ms()
        # progress only if tap follows quickly
        if now - self.last_tap_ms < self.timeout:
            self.progressPlayer(engine.card)
        engine.renderText(self.getRenderedText(engine))
        self.last_tap_ms = now          

class WaitPage(ThroughPage):
    pass
"""    

class NodeFork(Page):
    required = Page.required + ["choices"]
    optional = Page.optional + ["hideChoices"]
    defaults = dict(Page.defaults, 
        template = " {% include 'page' %}\n{% include 'choiceList' %}",
        page = "Choose from the following:",
        choiceList = " {% for choiceUid in node.choiceNodeUids %}{% if not(node.isHidden(engine, choiceUid)) %}{% include 'choiceItem' choiceUid %}\n{% endif %}{% endfor %}",
        choiceItem = " {% args choiceUid %}{{ engine.fillNodeTemplate(node, node.choices[choiceUid]) }} : {{story.lookupNode(choiceUid).getGoalBox(story).label}}",
    )
    
    def validate(self, story):
        super().validate(story)
        
        nodeTable = story._get_table(Node)
        boxTable = story._get_table(Box)
        
        choices = self.choices

        assert type(choices) == dict, "'choices' must be a dict mapping node uids to string templates. Cannot accept " + str(choices)
        choiceNodeUids = list(choices.keys())
        choiceLabels = [choices[key] for key in choiceNodeUids]
        
        badTemplates = [val for val in choiceLabels if not(isinstance(val, str))]
        assert len(badTemplates)==0, "ChoicePage: choice templates must be string values. Cannot accept " + str(badTemplates)
        
        badNodeUids = [val for val in choiceNodeUids if not(val in nodeTable)]
        assert len(badNodeUids)==0, "ChoicePage: choice node uid values must be found in story table. Cannot accept " + str(badNodeUids)

        choiceNodes = [story.lookupNode(nodeUid) for nodeUid in choiceNodeUids]
        
        choiceBoxUids = [node.getGoalBoxUid(story) for node in choiceNodes]
        badBoxUids = [val for val in choiceBoxUids if not(val in boxTable)]
        assert len(badBoxUids)==0, "ChoicePage: box uid values must be found in story table. Cannot accept " + str(badBoxUids)
        assert len(choiceBoxUids) == len(set(choiceBoxUids)), "Some Nodes referenced by 'choices' share the same goalBoxUid. Cannot accept " + str(choiceBoxUids)

        # save nodes and boxes
        self.choiceNodeUids = choiceNodeUids
        self.choiceBoxUids = choiceBoxUids
        
    def isHidden(self, engine, choiceNodeUid):
        if hasattr(self, "hideChoices"):
            if choiceNodeUid in self.hideChoices:
                return engine.evaluateExpression(self.hideChoices[choiceNodeUid])
        return False
    
    def activate(self, engine):
        if engine.box.uid in self.choiceBoxUids: # intercept choosing tap and change node uid
            chosenPos = self.choiceBoxUids.index(engine.box.uid)
            return self.choiceNodeUids[chosenPos] 
        return super().activate(engine)
            
# macro for making ThroughPage node chain , based at the same goalBox, 
# each having one page from the list 'sequence'
def ThroughSequence(uid, nextNodeUid, goalBoxUid, sequence, **k):
    pairs = list(enumerate(sequence))
    pairs.reverse()
    for pos,page in pairs:
        if pos == 0:
            pageUid = uid
        else: # later nodes have uids based on first node uid + position
            pageUid = uid + str(pos - 1) 
        ThroughPage(
            uid =    pageUid,
            page =   page,
            goalBoxUid =    goalBoxUid,
            nextNodeUid =   nextNodeUid,
            **k
        )
        nextNodeUid = pageUid
        
# Condition render
# and text rendering from sack
# Condition routing
# Test Verification of story
# Rendering as graph
