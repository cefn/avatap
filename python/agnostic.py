import sys
"""
Provides platform-agnostic exported symbols which may be provided in different ways on different platforms.
For example, the const() symbol provides for values which are treated as constant by the micropython bytecode
compiler, but the agnostic library enables python3 to use const() but just provides it as a dummy identity function
Similarly, os, io, and time are provided by uos, uio and utime on micropython, and re-exporting them from agnostic
allows them to be used without lots of platform-detection logic strewn through other libraries.
"""

assert hasattr(sys, "implementation"), "FATAL: Cannot run in Python 2"
if sys.implementation.name == "micropython":
    from micropython import const
    from utime import time
    from utime import ticks_ms
    import uos as os
    import uio as io
else:
    from time import time
    def ticks_ms():
        return int(time()*1000)
    def const(val):
        return val
    import os as os
    import io as io