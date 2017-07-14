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
from host.cockle import prepareHost
import loader
agnostic.collect()

story = loader.loadStory(loader.storyUid)
agnostic.collect()

boxHosts = prepareHost(story, [loader.boxUid])

boxHost = boxHosts[loader.boxUid]
while True: # useful for testing powerDown, although loop runs only once if Polulu latching
    while boxHost.running:
        agnostic.report_collect()
        try:
            cardUid = boxHost.newLoop() # card value allows gameLoop to indicate idleness for future self-depower
        except Exception as e:
            sys.print_exception(e)
    print("Powering down")
    boxHost.powerDown()

"""
from regimes.integration_test import run
run()
"""