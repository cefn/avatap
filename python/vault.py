import json
import gc
from mfrc522 import MFRC522

"""The reader used to put a JSON byte array (up to 240 bytes) onto the 1k Mifare Classic tag"""
rdr = MFRC522(0, 2, 4, 5, 14)
"""The number of banks available in the tag. Only one is active, and has its length stored in the lengths block"""
numBanks = 3
"""Default Mifare key which authenticates access to card sectors"""
# TODO CH change below to bytearray so it can be frozen
# key = b'\xff\xff\xff\xff\xff\xff'
key = [255, 255, 255, 255, 255, 255]
"""Number of bytes per block"""
bytesPerBlock = 16
"""Number of total blocks in 1k Mifare Classic tag"""
numBlocks = 64
"""Number of data (non-auth) blocks"""
numDataBlocks = (numBlocks // 4) * 3 # Every fourth block is an auth block, not used for banking
"""Block 0 is manufacturer-protected, block 1 is lengthblock and block 2 kept for future"""
numReservedDataBlocks = 3
"""Remaining authorable blocks"""
safeBlocks = numDataBlocks - numReservedDataBlocks
"""Authorable blocks allocated to each bank"""
blocksPerBank = safeBlocks // numBanks

"""Reserved block for keeping the length of JSON banks"""
lengthsRealIndex = 1

"""Buffer used for writing"""
blockBuffer = bytearray(bytesPerBlock)

""" # doesn't work in micropython
def fill(count, value):
    while count > 0:
        yield value
        count -= 1
"""


def getRealIndex(safeIndex):
    safeIndex = safeIndex + numReservedDataBlocks  # offset to skip reserved editable blocks
    return ((safeIndex // 3) * 4) + (safeIndex % 3)  # calculate index, skipping auth blocks

selectedTagUid=None

def selectTag(tagUid=None):
    global selectedTagUid
    if tagUid is None or not(selectedTagUid==tagUid):
        if selectedTagUid is not None:
            print("Previous tag still selected")
            unselectTag()
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        if stat is not MFRC522.OK: raise AssertionError("Idle")
        (stat, raw_uid) = rdr.anticoll()
        if stat is not MFRC522.OK: raise AssertionError("Collision")
        if tagUid is not None and not(tagUid == raw_uid):
            raise AssertionError("Wrong tag")
        if rdr.select_tag(raw_uid) is not MFRC522.OK: raise AssertionError("Selection")
        selectedTagUid = raw_uid
    else:
        print("Tag already selected")
    return selectedTagUid

def unselectTag():
    global selectedTagUid
    selectedTagUid = None
    rdr.stop_crypto1()

def readBlock(realBlockIndex):
    if selectedTagUid is None: raise AssertionError("Not selected")
    if rdr.auth(rdr.AUTHENT1A, realBlockIndex, key, selectedTagUid) is not MFRC522.OK: raise AssertionError("Auth")
    # TODO CH, optimise MFRC522 to prevent allocation here (implement 'readinto' function)
    block = rdr.read(realBlockIndex)
    # TODO CH, optimise to prevent re-allocation again to bytearray
    block = bytearray(block)
    gc.collect()
    return block

def writeBlock(realBlockIndex, data):
    if selectedTagUid is None: raise AssertionError("Not selected")
    if rdr.auth(rdr.AUTHENT1A, realBlockIndex, key, selectedTagUid) is not MFRC522.OK: raise AssertionError("Auth")
    return rdr.write(realBlockIndex, data)

def readLengthsBlock():
    return readBlock(lengthsRealIndex)

def writeLengthsBlock(data):
    return writeBlock(lengthsRealIndex, data)

def getActiveBank(lengthsBlock=None):
    if lengthsBlock is None:
        lengthsBlock = readLengthsBlock()
    activeBank = 0
    while lengthsBlock[activeBank] is 0 and activeBank < numBanks:
        activeBank += 1
    if activeBank < numBanks:
        return activeBank
    else:
        return None

def readJson(tagUid=None, unselect=True):
    try:
        tagUid = selectTag(tagUid)
        lengthsBlock = readLengthsBlock()
        # establish active bank from lengths block
        activeBank = getActiveBank(lengthsBlock)
        if activeBank is not None:
            bankLength = lengthsBlock[activeBank]   # how many bytes in the bank
            bankBytes = bytearray(bankLength)       # pre-allocate a buffer to store them
            safeIndex = activeBank * blocksPerBank  # what's the first authorable block in the bank
            nextBytePos = 0
            # read the next block from the bank, until bankBytes is filled
            while nextBytePos < bankLength:
                nextRealIndex = getRealIndex(safeIndex)
                copyLength = min(bytesPerBlock, bankLength - nextBytePos)
                blockData = readBlock(nextRealIndex)
                bankBytes[nextBytePos:nextBytePos + copyLength] = blockData[:copyLength]
                nextBytePos += copyLength
                safeIndex += 1
            # testing: import json; o = dict(hello="world"); b = bytes(json.dumps(o).encode("ascii")); print(json.loads(b.decode('ascii')))
            # TODO CH avoid allocation of bytes object here
            bankBytes = bytes(bankBytes)
            return json.loads(bankBytes.decode('ascii'))
        else:
            raise AssertionError("No bank")
    finally:
        if unselect:
            unselectTag()
        gc.collect()

# example ms=ticks_ms(); sack = vault.readJson(unselect=False); sack["eponapoints"]+=1; sack=vault.writeJson(sack, tagUid=vault.selectedTagUid); print(ticks_ms() - ms)

def writeJson(obj, tagUid=None, unselect=True):
    try:
        tagUid = selectTa
        g(tagUid)
        lengthsBlock = readLengthsBlock()
        activeBank = getActiveBank(lengthsBlock)
        if activeBank is not None:
            nextBank = (activeBank + 1) % numBanks
        else:
            nextBank = 0
        safeIndex = nextBank * blocksPerBank
        bankBytes = json.dumps(obj).encode("ascii")
        bankLength = len(bankBytes)
        nextBytePos = 0
        while nextBytePos < bankLength:
            nextRealIndex = getRealIndex(safeIndex)
            copyLength = min(bytesPerBlock, bankLength - nextBytePos)
            blockBuffer[:copyLength] = bankBytes[nextBytePos:nextBytePos + copyLength]
            writeBlock(nextRealIndex, blockBuffer)
            nextBytePos += copyLength
            safeIndex += 1
        nextBytePos = bytesPerBlock
        while nextBytePos > 0:
            nextBytePos -= 1
            blockBuffer[nextBytePos] = 0
        blockBuffer[nextBank]=bankLength
        writeLengthsBlock(blockBuffer)

    finally:
        if unselect:
            unselectTag()
        gc.collect()