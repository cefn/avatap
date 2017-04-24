# Test framework discussion

The ideal module to use is *pytest* as the testing library, supported by *doctest* to check that examples inlined in the *jsdoc* documentation continue to be valid as development proceeds. *Pytest* is a mature testing framework which apparently improves on python's built-in *unittest* module.

Doctest allows you to include a sequence of lines within the docstring for a specific class, method or function which can effectively be 'copied' from a python REPL (Read, Eval, Print, Loop) session.

However, since there is no support for pytest within the micropython framework, we have been pushed back to using just the original unittest framework.

