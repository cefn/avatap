'''A dict which auto-fills returned strings with matching values from the dict, recursively'''
class Resolver(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.stack = list()
        self.resolved = dict()
        
    def __getitem__(self, key):
        # record key expansion,  prevent circular refs + stack overflow
        if(key in self.stack):
            raise AssertionError("String expansion references itself, giving up")
        else:
            self.stack.append(key)
        val = dict.__getitem__(self, key)
        if(type(val)==str):
            val = val.format(**self)

        # key now handled, remove from stack
        assert key==self.stack.pop()
        
        return val

r = Resolver()
r["biter"]="man"
r["bitee"]="dog"
r["headline"]="{biter} bites {bitee}"
r["article"]="{headline}\nOn Tuesday a {biter} bit a {bitee} right on the"
print(r["article"])
