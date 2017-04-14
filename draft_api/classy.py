class Item(object):
	def __init__(self, *args, **kwargs):
		for data in args[1:]:
			for key in data:
				setattr(self, key, data[key])
		for key in kwargs:
			setattr(self, key, kwargs[key]) 
			
class val:
	def __init__(self, name, default=None, doc=None):
		self.name = name
		privateName = "_" + name
		def getter(self):
			if not(hasattr(self, privateName)): # set initial value
				setattr(self, privateName, default)
			return getattr(self, privateName)
		def setter(self, value):
			return setattr(self, privateName, value)
		deleter = None
		self.prop = property(getter, setter, deleter, doc)

'''A class decorator which injects logic into the __init__ method for 
a subclass of Item. Given a list of names passed in, an Error will 
be thrown when a name is not assigned by keyword args'''
def assertMembers(*args, **kwargs):
	# create a new dict
	memberProperties = {}
	memberDefaults = kwargs
	memberRequired = []
	for arg in args:
		argType = type(arg)
		if(argType==str):
			memberRequired.append(arg)
		elif(argType==dict):
			memberDefaults.update(arg)
		elif(argType==val):
			memberProperties[arg.name]= arg.prop
		else:
			raise AssertionError('Every unnamed argument to members should be a string name or a dict containing named defaults')
	def decorator(Cls):
		if not(issubclass(Cls, Item)):
			raise AssertionError("assertMembers decorator only works with objects subclassing from Item")
		# add vals (properties)
		for name in memberProperties:
			setattr(Cls, name, memberProperties[name])
		# augment the init method
		oldInit = Cls.__init__
		def newInit(self, *args, **kwargs):
			# start with default key/value pairs 
			newKwargs = dict(memberDefaults)
			# merge in key/value pairs provided to constructor
			newKwargs.update(kwargs)
			for name in memberRequired:
				if not(name in newKwargs) and not(name in memberProperties):
					raise AssertionError("Required value for " + name + " was not provided")
			super(Cls, self).__init__(self, args, newKwargs)
			pass
		Cls.__init__ = newInit
		return Cls
	return decorator

# TODO consider adding a require decorator which ensures that a given class has certain properties passed, possibly with the means of setting a default if it isn't?

'''
def superinit(self, *args, **kwargs):
	super().__init__(self, *args, **kwargs)

def autoinit(cls):
	if(not(hasattr(cls, '__init__'))):
		setattr(cls, '__init__', superinit)
	else:
		raise AssertionError("@autoinit failed: Class already has an __init__() method")
'''
