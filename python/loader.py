#Attempts to import everything in the proper sequence
# garbage collecting between and reporting remaining memory
from agnostic import report_import, report_collect

storyUid = "arbeia"
boxUid = "1"

def loadDisplay():
    report_collect()
    report_import("machine")
    report_import("st7920")
    report_import("faces.font_5x7")

def loadOther():
    report_collect()
    #report_import("faces.font_timB14")
    report_import("mfrc522")
    report_import("milecastles")
    report_import("boilerplate")
    report_import("engines")
    report_import("host")
    report_import("vault")

def loadStory(name):
    report_collect()
    imp = report_import("stories." + name)
    mod = getattr(imp, name)
    return getattr(mod, 'story')