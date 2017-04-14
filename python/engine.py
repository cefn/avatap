from agnostic import io
from milecastles import AnonymousContainer, Holder, Story, signature,debug
from boilerplate import Compiler, Resolver

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

class Engine(AnonymousContainer):
    required = AnonymousContainer.required + ["box"] # remove "uid"
    defaults = dict(AnonymousContainer.defaults,
        card =  None,
        story = None,
        node =  None
    )
        
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.debug = Debug()
        
    def registerStory(self, story):
        return self._register(Story, story)
    
    def lookupStory(self, storyUid):
        return self._lookup(Story, storyUid)
                
    def handleCard(self, card):
        self.card = card
        self.story = self.lookupStory(card.storyUid)
        currentUid = card.nodeUid
        while self.node == None:
            currentNode = self.story.lookupNode(currentUid)
            redirectedUid = currentNode.activate(self)
            if redirectedUid != None and redirectedUid != currentUid:
                currentNode.deactivate(self)
                currentUid = redirectedUid
            else:
                self.setNode(currentNode)
        self.displayNode(self.node)
        self.node.deactivate(self)
        self.node = None
        self.story = None
        self.card = None
            
    def setNodeUid(self, nodeUid):
        node = self.story.lookupNode(nodeUid)
        return self.setNode(node)
    
    def setNode(self, node):
        self.node = node
        self.card.nodeUid = node.uid
        return self.node
            
    def getEngineContext(self):
        return dict(
            engine =    self, 
            story =     self.story,
            box =       self.box,
            node =      self.node,
            card =      self.card,
            sack =      Holder(**self.card.sack) # enables dot addressing of dictionary
        )
    
    def evaluateExpression(self, expression):
        return eval(expression, self.getEngineContext())
   
    def fillNodeTemplate(self, node, templateString):
        # prefix the templateString with the standard argument signature
        # TODO preceding space is added here as a workaround for https://github.com/pfalcon/utemplate/issues/5
        templateString = "{% args " + signature + " %}" + " " + templateString
        # use node as its own resolver
        templateResolver = Resolver(**node.__dict__)
        # create streams and wire them
        template_in = io.StringIO(templateString)
        template_out = io.StringIO()
        c = Compiler(template_in, template_out, loader=templateResolver)
        try:
            # do a compile run
            c.compile()
            compiled = template_out.getvalue()
            g = dict()
            # evaluate the compiled code
            exec(compiled, g)
            # extract the render function which was created during exec
            renderFun = g["render"]
            # create a string generator by calling the render function
            renderGen = renderFun(**self.getEngineContext())
            # concatenate the generated strings
            renderOut = io.StringIO()
            for chunk in renderGen:
                renderOut.write(chunk)
            # return concatenated string
            renderedString = renderOut.getvalue() 
            # TODO preceding space is removed here as workaround for https://github.com/pfalcon/utemplate/issues/5
            return renderedString[1:] 
        except Exception as k:
            import ipdb; ipdb.set_trace()
            raise k
    
    def displayNode(self, node):
        nodeText = self.fillNodeTemplate(node, node.render(self))
        if hasattr(self, "debug"):
            self.debug.debug("SACK" + str(self.card.sack))
        self.displayText(nodeText)
        
    '''Should render some text, in whatever form required by the Engine'''
    def displayText(self, text):
        raise AssertionError("Not yet implemented")
