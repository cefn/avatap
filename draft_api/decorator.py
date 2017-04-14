def decoratorFactory(msg):
	def decorator(fun):
		def decorated(*a,**k):
			print(msg)
			return fun(*a,**k)
		return decorated
	return decorator

@decoratorFactory("Hello World")
def sum(a,b):
	return a+b

sum(2,3)
