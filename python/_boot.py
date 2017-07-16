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
import loader
from os import urandom
from machine import reset
agnostic.collect()


def floor(n):
    res = int(n)
    return res if res == n or n >= 0 else res-1

def log2approx(val):
    val = floor(val)
    approx = 0
    while val != 0:
        val &= ~ (1 << approx)
        approx = approx + 1
    return approx

def randint(minVal, maxVal=None):
    if (maxVal != None):
        return minVal + randint(maxVal - minVal)
    else:
        maxVal = minVal
    byteCount = (log2approx(maxVal) // 8) + 1  # each byte is 8 powers of two
    val = 0
    randBytes = urandom(byteCount)
    idx = 0
    while idx < len(randBytes):
        val |= randBytes[idx] << (idx * 8)
        idx += 1
    del randBytes
    return val % maxVal


story = loader.loadStory(loader.storyUid)
agnostic.collect()

from milecastles import Box

def fuzz():
    """Emulate whole museum in one box"""

    boxUids = list(story._get_table(Box).keys())
    boxHosts = prepareHosts(story, boxUids)

    while True:
        #agnostic.reboot_collect()
        agnostic.report_collect()
        nextBoxUid = boxUids[randint(len(boxUids))]
        print("Visiting box {}".format(nextBoxUid))
        nextHost = boxHosts[nextBoxUid]
        nextHost.cardCache = None
        cardUid = nextHost.gameLoop(fuzz=True)

def run():
    boxHosts = prepareHosts(story, [loader.boxUid])
    boxHost = boxHosts[loader.boxUid]
    while True:  # useful for testing powerDown, although loop runs only once if Polulu latching
        while boxHost.running:
            #agnostic.reboot_collect()
            agnostic.report_collect()
            try:
                cardUid = boxHost.gameLoop()  # card value allows gameLoop to indicate idleness for future self-depower
            except Exception as e:
                sys.print_exception(e)
        print("Powering down")
        boxHost.powerDown()

try:
    fuzz()
except MemoryError:
    reset()

"""
from regimes.integration_test import run
run()
"""