from sys import print_exception
from os import urandom
from agnostic import report_collect
from host.cockle import prepareHosts
from milecastles import Box

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

def walk(story):
    """Emulate whole museum in one box"""

    boxUids = list(story._get_table(Box).keys())
    boxHosts = prepareHosts(story, boxUids)

    while True:
        # agnostic.reboot_collect()
        report_collect()
        nextBoxUid = boxUids[randint(len(boxUids))]
        print("Visiting box {}".format(nextBoxUid))
        nextHost = boxHosts[nextBoxUid]
        nextHost.cardCache = None
        cardUid = nextHost.gameLoop(fuzz=True)


