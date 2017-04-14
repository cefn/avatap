# A subclass of python's native dict, which auto-populates values with
# template strings like {key} by looking up other string values stored
# within the same dict
class ResolvingDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.resolvedstrings = dict()

    # recursively expands string values using str.format, drawing from
    # its own dict entries and eliminating circular references by
    # checking against a thread-local list of references which are on
    # the 'resolving stack' - note this does not work when Formatter
    # class vformat call is substituted with (ostensibly equivalent)
    # str.format call
    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        #print("GET %s['%s'] = %s" % str(dict.get(self, 'name_label')), str(key), str(val))
        if type(val) is str:
            if key not in self.resolvedstrings:
                try:
                    # used to track circular refs
                    threadlocal = threading.local()
                    
                    try: # check if resolution list already allocated
                        threadlocal.resolving 
                        allocatedhere = False 
                    except: # resolution list not already allocated
                        threadlocal.resolving = list()
                        allocatedhere = True
                        
                    # quit on circular refs
                    if key in threadlocal.resolving:
                        raise Error('Cycle found in references! ' + threadlocal.resolving )
                    else:                    
                        # recursively expand string value with string.Formatter
                        threadlocal.resolving.append(key)
                        self.resolvedstrings[key]=Formatter().vformat(val,[],self)
                        threadlocal.resolving.pop()
                finally:
                    if allocatedhere : # de-allocate resolution list
                        del threadlocal.resolving
                        
            return self.resolvedstrings[key]
        else:
            return val
