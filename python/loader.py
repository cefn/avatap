#Attempts to import everything in the proper sequence
# garbage collecting between and reporting remaining memory
from agnostic import report_import

#TODO CH explore the ordering of these imports, and interleave with garbage collection, as per memory test

# time boot routine with
# from utime import ticks_ms; ms = ticks_ms(); import loader; loader.loadAll(); print("Loading took:" + str(ticks_ms() - ms))

storyUid = "corbridge"

def loadDisplay():
    report_import("machine")
    report_import("st7920")
    report_import("faces.font_5x7")

def loadOther():
    #report_import("faces.font_timB14")
    report_import("mfrc522")
    report_import("milecastles")
    report_import("boilerplate")
    report_import("engines")
    report_import("host")
    report_import("vault")

def loadStory(name):
    report_import("stories." + name)

def loadAll():
    loadDisplay()
    loadOther()
    loadStory(storyUid)