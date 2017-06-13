import gc
gc.threshold((gc.mem_free() + gc.mem_alloc()) // 4)

import uos
""" # TODO CH Disable Filesystem again to max memory
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

boxHost = prepareHost(story, loader.boxUid)
while boxHost.running:
    agnostic.report_collect()
    boxHost.gameLoop()
boxHost.powerDown()