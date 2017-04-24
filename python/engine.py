from agnostic import io,gc
from milecastles import AnonymousContainer, Holder, Story, signature, required, optional, debug
from boilerplate import Compiler, Resolver

templatePrefix = "{{% args {} %}}".format(signature)

class Engine(AnonymousContainer):
    box = required
    card = None
    story = None
    node = None

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

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

    # CH TODO factor out into boilerplate
    def jinjaToPython(self, templateResolver, templateString):
        # prefix the templateString with the standard argument signature
        templateString = templatePrefix + templateString
        # create streams and wire them
        template_in = io.StringIO(templateString)
        template_out = io.StringIO()
        c = Compiler(template_in, template_out, loader=templateResolver)
        # do a compile run
        try:
            c.compile()
            gc.collect()
            return template_out.getvalue()
        except Exception as k:
            raise k

    def loadGeneratorFactory(self, node, templateString):
        try:
            compiled = self.jinjaToPython(node, templateString)
            # TODO CH MEMORY 'Cache' pre-compiled modules, indexed by MD5 hash of templateString (use import from filesystem/frozen module not exec from memory)
            g = dict()
            # evaluate the compiled code
            exec(compiled, g)
            # extract the render function which was created during exec
            gc.collect()
            return g["render"]
        except Exception as k:
            raise k

    def constructGenerator(self, node, templateString):
        renderFun = self.loadGeneratorFactory(node, templateString)
        # create a string generator by calling the render function, passing context arguments
        generator = renderFun(**self.getEngineContext())
        gc.collect()
        return generator

    # TODO CH MEMORY - Avoid fragmentation from concatenating strings - pass generator directly to newly improved bitfont (which accepts generators)
    def concatenateGeneratedStrings(self, renderGen):
        # concatenate the generated strings
        renderOut = io.StringIO()
        for chunk in renderGen:
            renderOut.write(chunk)
        # return concatenated string
        renderedString = renderOut.getvalue()
        gc.collect()
        return renderedString

    def saveTemplatePython(self, templateId, templatePython):
        with open("templates/t_{}.py".format(templateId), "w") as f:
            f.write(templatePython)

    def loadTemplateGeneratorFactory(self, templateId):
        templateModule = __import__("templates.t_{}".format(templateId), globals(), locals(), ["render"] )
        return templateModule.render

    def displayNode(self, node):
        templateName = node.getRenderedTemplateName(self)
        templateId = "{}_{}_{}".format(self.story.uid, node.uid, templateName)

        # CH suppress behaviour of dynamically compiling, runtime evaluating
        # generator = self.constructGenerator(node, templateString)

        # CH instead load from module, (optionally lazy-create module)
        try:
            generatorFactory = self.loadTemplateGeneratorFactory(templateId)
        except ImportError as e:
            templateResolver = Resolver(node) # use node as resolver (referenced templates also attributes of node)
            templateJinja = getattr(node, templateName) # get jinja source from attribute of node
            self.saveTemplatePython(templateId, self.jinjaToPython(templateResolver, templateJinja))
            generatorFactory = self.loadTemplateGeneratorFactory(templateId)

        generator = generatorFactory(**self.getEngineContext())
        nodeText = self.concatenateGeneratedStrings(generator)
        if debug:
            debug.debug("SACK" + str(self.card.sack))
        self.displayText(nodeText)

    '''Should render some text, in whatever form required by the Engine'''
    def displayText(self, text):
        raise AssertionError("Not yet implemented")