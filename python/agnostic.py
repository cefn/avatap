import sys

assert hasattr(sys, "implementation"), "FATAL: Cannot run in Python 2"
if sys.implementation.name == "micropython":
    from utime import time
    from utime import ticks_ms
    import uos as os
    import uio as io
else:
    from time import time
    def ticks_ms():
        return int(time()*1000)
    import os
    import io