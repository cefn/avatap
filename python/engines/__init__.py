from milecastles import Container, Story
from boilerplate import Compiler

class Debug():
	def report(report):
		print(report)
		
	def debug(msg):
		print("DEBUG:" + msg)

	def info(msg):
		print("INFO:" + msg)

	def warn(msg):
		print("WARN:" + msg)

	def error(msg):
		print("ERROR:" + msg)

	def fatal(msg):
		print("FATAL:" + msg)

class Engine(Container):
	required = [n for n in Container.required if n!="uid"] + ["box"] # remove "uid"
	
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
        self.setNodeUid(card.nodeUid)
    
    def setNodeUid(self, nodeUid):
        try:
            if self.node.uid != nodeUid:
                self.node.deactivate(self)
        except AttributeError:
            
        	node = self.story.lookupNode(card.nodeUid)
        self.node = node
        node.activate(self)
        # if node not substituted, handle tap
        if self.node == node:
            node.handleTap(self)
            
    def getEngineContext():
        return dict(
            engine =    self, 
            box =       self.box,
            node =      self.node,
            card =      self.card,
            sack =      self.card.sack
        )
    
    def evaluateExpression(self, expression):
        return eval(self.expression, self.getEngineContext())
    
    def renderTemplate(self, templateString, templateResolver):
        # prefix template with declaration of standard self, engine args
        templateString = "{% args engine, box, node, card, sack %}\n" + templateString
        template_in = io.StringIO(templateString)
        template_out = io.StringIO()
        c = Compiler(resolver, template_in, template_out)
        try:
            c.compile()
            compiled = template_out.getvalue()
            g = dict()
            eval(compiled, g)
            renderFun = g["render"]
            self.renderText(renderFun(**self.getEngineContext()))
        except Error as k:
            import ipdb; ipdb.set_trace()
            raise k
		
	'''Should render some text, in whatever form required by the Engine'''
	def renderText(self, text):
		raise AssertionError("Not yet implemented")
