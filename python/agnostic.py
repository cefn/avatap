import sys

"""
Provides platform-agnostic exported symbols which may be provided in different ways on different platforms.
For example, the const() symbol provides for values which are treated as constant by the micropython bytecode
compiler, but the agnostic library enables python3 to use const() but just provides it as a dummy identity function
Similarly, os, io, and time are provided by uos, uio and utime on micropython, and re-exporting them from agnostic
allows them to be used without lots of platform-detection logic strewn through other libraries.
"""

assert hasattr(sys, "implementation"), "FATAL: Cannot run in Python 2"

# number of bytes at which to reset
LOW_MEMORY = 13000

if sys.implementation.name == "micropython":
    from micropython import const, opt_level
    opt_level(1) # removes debug symbols?
    from machine import reset as reboot
    """
    from esp import deepsleep
    def reboot():
        deepsleep(1) # sleep for 1 microsecond
    """
    import gc
    from utime import sleep,ticks_ms
    import uos as os
    import uio as io

    def reboot_collect():
        report_collect()
        if gc.mem_free() > LOW_MEMORY:
            print("MEMORY OK")
        else:
            print("LOW MEMORY, REBOOTING")
            reboot()

    def collect():
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

    def report_collect():
        wasfree = gc.mem_free()
        collect()
        sys.stdout.write(str(wasfree))
        sys.stdout.write("+")
        sys.stdout.write(str(gc.mem_free() - wasfree))
        sys.stdout.write("=")
        sys.stdout.write(str(gc.mem_free()))
        sys.stdout.write("\n")

    def do_import(moduleName):
        return __import__(moduleName)

    def report_import(moduleName):
        sys.stdout.write(moduleName)
        sys.stdout.write("\n")
        result = do_import(moduleName)
        report_collect()
        return result

else:
    def collect():
        pass
    def report_import():
        pass
    def report_collect():
        pass
    def reboot_collect():
        pass
    def noop():
        pass
    class AttrObj:
        pass
    gc = AttrObj()
    setattr(gc, "collect", noop)
    from time import sleep,time
    def ticks_ms():
        return int(time()*1000)
    def const(val):
        return val
    import os as os
    import io as io