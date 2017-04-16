from agnostic import ticks_ms

"""
    Avatap provides a model for text adventures in which players travel between distributed stations
    with lo-res screens, tapping in at each station with an RFID card containing their 'game state'. 
    
    On the card is 
    * a storyUid - identifying which Story they are following
    * a nodeUid - identifying their position or Node in the Story
    * a sack - containing accumulated game state in the form of key:value pairs
    
    Nodes only represent story structure and temporary data used for screen-rendering logic. The only 
    persistent state remains in the player's RFID card. Game input takes place purely through the act 
    of tapping a station. 
    
    The basic load and render cycle (visible within engines.Engine) is as follows...
    *   The card is read, and the box, card, story, and sack are made available as attributes of the 
        engine. 
    *   The current node is set as engine.node
    *   The node's activate() routine is called, passing the engine reference. If activate() returns 
        a new current nodeUid, the activated node gets a deactivate() call, and the previous step is repeated.
    *   The final node in the chain (which did not redirect to a different node) will get a render() call
        causing a template to be generated and sent to the screen
    *   At this point, the RFID card is rewritten with the new game state, the node gets a deactivate() call
        and all state related to this player and tap is lost
    
    Processing all story logic through transient state within the lifetime of a single tap imposes 
    substantial limitations on the interaction model available compared to, for example, the Twine framework.
    
    The design of this API has focused on guiding authors who are not expert programmers to create their
    own stories using the primitives of Boxes and various specialised Story 'Nodes' and 'NodeOperators'
    which respect the fundamental limitations of this unusual medium.
    
    In particular, the syntax for authoring is comprehensible, consistent and exposes no python language 
    structures other than keyword arguments and dicts (lookup tables). 
    
    This approach is enriched by certain values being interpreted as python expressions accessing API objects. 
    A consistent set of entities is made available using python identifiers within Story templates, routing 
    and trigger conditions, (recorded in milecastles.signature), currently "engine, story, box, node, card, sack"
    
    The core components you need to master to create a story are the following three Node types and one NodeOperator...
    
    ConditionFork   - Immediately redirects to one of two Nodes in the story, according to whether its 'condition' evaluates to true or not
                      [Typically this condition will check for the state of things in the sack]

    NodeFork        - Guides the player to choose Nodes hosted at different Boxes. When you choose a Box, redirects to the corresponding Node
                      [Story validation failes if your choice nodes don't have different goalBoxes]

    ThroughPage     - Guides the player to a specific Box. On arrival at the Box, renders a page, then redirects to a specific Node in the Story 
                      [the ThroughSequence procedure creates a ThroughPage chain in which Box guidance is not normally triggered; they are at the same box]
                    
    SackChange      - If the trigger condition is True (or omitted) the player's sack is changed according to named sets of name:value pairs
                      ['assign' - sets the values, 'plus' adds them, 'minus' subtracts them, 'reset' must be used on its own and replaces the sack completely]

"""

class Debug():
    def report(self, report):
        print(report)

    def debug(self, msg):
        self.report("DEBUG:" + msg)

    def info(self, msg):
        self.report("INFO:" + msg)

    def warn(self, msg):
        self.report("WARN:" + msg)

    def error(self, msg):
        self.report("ERROR:" + msg)

    def fatal(self, msg):
        self.report("FATAL:" + msg)

debug = None
debug = Debug()

story = None

required = object()
optional = object()

# The signature of objects passed to templates and routing/trigger conditions
signature = "engine, story, box, node, card, sack"

def loadStory(storyIdString):
    """Loads a Story with a given storyIdString, assuming it is at stories.[storyIdString].story"""
    loaded = __import__("stories." + storyIdString)
    module = getattr(loaded, storyIdString)
    return module.story
    
def getStoryContext():
    global story
    assert story != None, "Need `with story:` block"
    return story

class Holder(object):
    def __init__(self, *a, **k):
        for key,val in k.items():
            setattr(self, key, val)

    def assert_attr(self, name, check, msg):
        if not(check):
            raise AssertionError("Param Err {} {} {} {}".format(type(self), self.uid  if hasattr(self, "uid") else "" , str(name), msg))


class StrictHolder(Holder):
    """
    Enforces that no attributes are previously unknown.
    They are expected to already be set to a default value, or are set to milecastles.required or milecastles.optional.
    """
    def __init__(self, *a, **k):
        for key, val in k.items():
            self.assert_attr(key, hasattr(self, key), "unknown param")
        super().__init__(self, *a, **k)

'''
Base class which treats all named arguments as attributes and 
all positional arguments as dicts containing named attributes
'''
class Item(Holder):

    # populate attributes from positional dicts and keyword args
    def __init__(self, *a, **k):
        super().__init__(self, *a, **k)

        names = dir(self)

        # raise error if any 'required' attributes still missing
        for name in names:
            value = getattr(self, name)
            if value == optional:
                setattr(self, name, None)
            self.assert_attr(name, value != required, "attribute required")

class UidItem(Item):
    '''
        A common superclass for items with ids. Accepts a string id argument
        and silently replaces it with a typed Uid object which is required
        by other Uid oriented references, this supports implicit validation
        of data structures (e.g. encouraging you to refer to myNode.uid in
        preference to the possibly "theuid")
    '''
    uid = required

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
    uid = optional

class Story(Container):
    startNodeUid = required
    startSack = optional

    def __init__(self, *a, **k):
        super().__init__(self, *a, **k)
        if self.startSack is None:
            self.startSack = dict()

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
        # construct an easy dot lookup mechanism from within templates
        self.nodes = Holder(**self._get_table(Node))
        self.boxes = Holder(**self._get_table(Box))
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
    storyUid = required
    nodeUid = required
    sack = required

class Box(UidItem):
    label = required
    description = required

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getStoryContext().registerBox(self)


class Node(UidItem):
    change = None
    time = optional

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        getStoryContext().registerNode(self)

    def validate(self, story):
        # lookup box/node uids, generate new attributes pointing to boxes and nodes
        print("Validating {} with uid {}".format(type(self).__name__, self.uid))
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
            redirectedUid = operator.operate(engine)
            if redirectedUid:
                return redirectedUid # allow operators to send a redirect nodeUid
        return None

    def render(self,  engine):
        return None

    def deactivate(self,  engine):
        return None

# TODO add MultiNodeOperator as wrapper around (non-strict) Holder, allowing addressing of operators by name using dot notation even when multiple
class NodeOperator(Item):

    def validate(self, story):
        pass

    def operate(self,  engine):
        pass


# See also https://twine2.neocities.org/1.html for Twine reference features around variables and execution
class SackChange(NodeOperator):
    trigger = optional
    assign = optional
    plus = optional
    minus = optional
    reset = optional
    stayPositive = True,

    def validate(self, story):
        assignName = "assign"
        plusName = "plus"
        minusName = "minus"
        resetName = "reset"
        changeNames = [assignName, plusName, minusName, resetName]
        dictMessage = "should be dict"
        self.assert_attr("[required]", any([hasattr(self, changeName) for changeName in changeNames]), "needs one of " + str(changeNames))
        self.assert_attr(resetName,  self.reset is None or all([self.assign is None, self.plus is None, self.reset is None]), "obliterates " + str([name for name in changeNames if not name is resetName]))
        self.assert_attr(assignName, self.assign is None or type(self.assign) == dict, dictMessage)
        self.assert_attr(plusName,   self.plus is None or   type(self.plus) == dict,   dictMessage)
        self.assert_attr(minusName,  self.minus is None or  type(self.minus) == dict,  dictMessage)
        self.assert_attr(resetName,  self.reset is None or  type(self.reset) == dict,  dictMessage)

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
                if(hasattr(self, minusName)):
                    for key,val in self.minus.items():
                        if key not in sack or sack[key] <= val:
                            # refuse the change
                            self.completed = False
                            return                        
            # can trigger change(s)
            
            # handle setting (any python value)
            if self.assign is not None:
                for key,val in self.assign.items():
                    sack[key]=val
            # handle addition (to a number)
            if self.plus is not None:
                for key,val in self.plus.items():
                    if key in sack:
                        sack[key] = sack[key] + val
                    else:
                        sack[key] = val
            # handle removal (from a number)
            if self.minus is not None:
                for key,val in self.minus.items():
                    if key in sack:
                        sack[key] = sack[key] - val
                    else:
                        sack[key] = - val
            
            if self.reset is not None:
                engine.card.sack = dict(self.reset)
            
            self.completed = True

class ConditionFork(Node):
    condition = required
    trueNodeUid = required
    falseNodeUid = required

    def evaluate(self, engine):
        return engine.evaluateExpression(self.condition)
    
    def activate(self, engine):
        super().activate(engine)
        if self.evaluate(engine):
            return self.trueNodeUid
        else:
            return self.falseNodeUid    

    def getGoalBoxUid(self, story):
        trueBoxUid = story.lookupNode(self.trueNodeUid).getGoalBoxUid(story)
        falseBoxUid = story.lookupNode(self.falseNodeUid).getGoalBoxUid(story)
        self.assert_attr("goalBoxUid", trueBoxUid == falseBoxUid, "true and false boxes differ")
        return trueBoxUid

class Page(Node):
    page = required
    template = "{% include 'page' " + signature + " %}"

    def render(self, engine):
        return self.template

class GoalPage(Page):
    goalBoxUid = required
    missTemplate="Please go to {{node.goalBox.label}} to continue your adventure"

    def getGoalBoxUid(self, story):
        return self.goalBoxUid

    def activate(self, engine):
        # only trigger operators when it's actually the goal box
        if engine.box == self.goalBox:
            return super().activate(engine)
        else:
            return None

    def render(self, engine):
        if engine.box == self.goalBox:
            return self.template # render as usual
        else:
            return self.missTemplate            # render a miss
        
class ThroughPage(GoalPage):
    nextNodeUid = required

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
    choices = required
    hideChoices = optional
    template = "{% include 'page' %}\n{% include 'choiceList' %}",
    page = "Choose from the following:",
    choiceList = " {% for choiceUid in node.choiceNodeUids %}{% if not(node.isHidden(engine, choiceUid)) %}{% include 'choiceItem' choiceUid %}\n{% endif %}{% endfor %}",
    choiceItem = " {% args choiceUid %}{{ engine.fillNodeTemplate(node, node.choices[choiceUid]) }} : {{story.lookupNode(choiceUid).getGoalBox(story).label}}",

    def validate(self, story):
        super().validate(story)
        
        nodeTable = story._get_table(Node)
        boxTable = story._get_table(Box)
        
        choices = self.choices

        self.assert_attr("choices", type(choices) == dict, "should map node uids to templates ")
        choiceNodeUids = list(choices.keys())
        choiceLabels = [choices[key] for key in choiceNodeUids]
        
        badTemplates = [val for val in choiceLabels if not(isinstance(val, str))]
        self.assert_attr("choiceLabels", len(badTemplates)==0, "not strings; " + str(badTemplates))

        badNodeUids = [val for val in choiceNodeUids if not(val in nodeTable)]
        self.assert_attr("choiceNodeUids", len(badNodeUids)==0, "not in story;" + str(badNodeUids))

        choiceNodes = [story.lookupNode(nodeUid) for nodeUid in choiceNodeUids]
        
        choiceBoxUids = [node.getGoalBoxUid(story) for node in choiceNodes]
        badBoxUids = [val for val in choiceBoxUids if not(val in boxTable)]
        self.assert_attr("choiceBoxUids", len(badBoxUids)==0, "not in story;" +  str(badBoxUids))
        self.assert_attr("choiceBoxUids", len(choiceBoxUids) == len(set(choiceBoxUids)), "duplicate goalBoxUids;" +  str(badBoxUids))

        # save nodes and boxes
        self.choiceNodeUids = choiceNodeUids
        self.choiceBoxUids = choiceBoxUids
        
    def isHidden(self, engine, choiceNodeUid):
        if hasattr(self, "hideChoices"):
            if choiceNodeUid in self.hideChoices:
                return engine.evaluateExpression(self.hideChoices[choiceNodeUid])
        return False
    
    def activate(self, engine):
        redirectedUid = super().activate(engine)
        if redirectedUid:
            return redirectedUid
        elif engine.box.uid in self.choiceBoxUids: # intercept choosing tap and change node uid
                chosenPos = self.choiceBoxUids.index(engine.box.uid)
                return self.choiceNodeUids[chosenPos]

# macro for making ThroughPage node chain , based at the same goalBox, 
# each having one page from the list 'sequence'
def ThroughSequence(uid, nextNodeUid, goalBoxUid, sequence, **k):
    pairs = list(enumerate(sequence))
    pairs.reverse()
    for pos,page in pairs:
        if pos == 0:
            pageUid = uid
            kwargs = k
        else: # later nodes have uids based on first node uid + position
            pageUid = uid + str(pos - 1)
            kwargs = {}
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
