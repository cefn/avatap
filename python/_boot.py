import sys
import gc
gc.threshold((gc.mem_free() + gc.mem_alloc()) // 4)
import uos

""" # TODO CH Filesystem disabled to maximise memory
from flashbdev import bdev

try:
    if bdev:
        vfs = uos.VfsFat(bdev)
        uos.mount(vfs, '/flash')
        uos.chdir('/flash')
except OSError:
    import inisetup
    vfs = inisetup.setup()
"""
gc.collect()

import agnostic
from host.cockle import prepareHosts
from loader import storyUid, boxUid, loadStory
from machine import reset
agnostic.collect()

story = loadStory(storyUid)
agnostic.collect()

def run(loop=True):
    boxHosts = prepareHosts(story, [boxUid])
    boxHost = boxHosts[boxUid]
    while loop and boxHost.running:
        agnostic.report_collect()
        cardUid = boxHost.gameLoop()  # card value allows gameLoop to indicate idleness for future self-depower

"""
"""
try:
    run()
except MemoryError:
    reset()
except Exception as e:
    sys.print_exception(e)
    reset()


"""
from fuzz import walk
try:
    walk(story)
except MemoryError:
    reset()
except Exception as e:
    sys.print_exception(e)
"""

"""
from regimes.integration_test import run
run()
"""