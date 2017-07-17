import sys
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

import agnostic
agnostic.collect()
import host.cockle
import loader
from machine import reset
agnostic.collect()

story = loader.loadStory(loader.storyUid)
agnostic.collect()

def run(loop=True):
    boxHosts = host.cockle.prepareHosts(story, [loader.boxUid])
    boxHost = boxHosts[loader.boxUid]
    while loop and boxHost.running:
        agnostic.report_collect()
        cardUid = boxHost.gameLoop()  # card value allows gameLoop to indicate idleness for future self-depower

while True:
    try:
        run()
    except MemoryError:
        reset()
    except Exception as e:
        sys.print_exception(e)
        continue

"""
while True:
    from fuzz import walk
    try:
        walk(story)
    except MemoryError:
        reset()
    except Exception as e:
        sys.print_exception(e)
        continue
"""

"""
from regimes.integration_test import run
run()
"""