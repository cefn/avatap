import json
import gc
from mfrc522 import MFRC522

"""The number of banks available in the tag. Only one is active, and has its length stored in the lengths block"""
numBanks = 3
"""Default Mifare key which authenticates access to card sectors"""
key = b'\xff\xff\xff\xff\xff\xff'
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

def getRealIndex(safeIndex):
    safeIndex = safeIndex + numReservedDataBlocks  # offset to skip reserved editable blocks
    return ((safeIndex // 3) * 4) + (safeIndex % 3)  # calculate index, skipping auth blocks

class BankVault:
    def __init__(self, reader):
        #reader used to put a JSON byte array (up to 240 bytes) onto the 1k Mifare Classic tag
        self.rdr = reader
        #Buffer used for writing
        self.blockBuffer = bytearray(bytesPerBlock)
        # currently selected tag (avoid reauth)
        self.selectedTagUid = None

    # TODO CH add timeout here and in LaptopRfid
    # TODO CH change this to return None ASAP if there is no cardUid there
    # TODO CH should awaitPresence/Absence always force an unselect of any previous cards first?
    def awaitPresence(self):
        while True:
            print("Seeking...")
            (stat, tag_type) = self.rdr.request(MFRC522.REQIDL)  # check if antenna idle
            if stat is not MFRC522.OK:
                print("No tag")
                continue
            else:
                print("Separating...")
                (stat, tagUid) = self.rdr.anticoll()
                if stat is not MFRC522.OK:
                    print("Collision")
                    continue
                return tagUid

    def awaitAbsence(self):
        errThreshold = 2
        errCount = 0
        while errCount < errThreshold:
            (stat, tag_type) = self.rdr.request(MFRC522.REQIDL)  # check if antenna idle
            if stat is MFRC522.OK:
                errCount = 0
            else:
                errCount += 1
        return

    # reimplemented as blocking via await presence
    def selectTag(self, expectTagUid=None):
        if expectTagUid is None or not(self.selectedTagUid==expectTagUid):
            if self.selectedTagUid is not None:
                self.unselectTag()
            tagUid = self.awaitPresence()
            if expectTagUid is not None and not(tagUid == expectTagUid): raise AssertionError("Wrong Tag")
            if self.rdr.select_tag(tagUid) is not MFRC522.OK: raise AssertionError("Selection")
            self.selectedTagUid = tagUid
        else:
            print("Tag already selected")
        return self.selectedTagUid

    def unselectTag(self):
        self.selectedTagUid = None
        # TODO need to add 'HaltA' here? see https://github.com/cefn/micropython-mfrc522/issues/1
        self.rdr.halt_a()
        self.rdr.stop_crypto1()

    def readBlock(self, realBlockIndex):
        if self.selectedTagUid is None: raise AssertionError("Not selected")
        # TODO CH is this repeated auth always necessary, or only once?
        if self.rdr.auth(MFRC522.AUTHENT1A, realBlockIndex, key, self.selectedTagUid) is not MFRC522.OK: raise AssertionError("Auth")
        # TODO CH, optimise MFRC522 to prevent allocation here (implement 'readinto' function)
        block = self.rdr.read(realBlockIndex)
        # TODO CH, optimise to prevent re-allocation again to bytearray (duplicated in reader too?)
        block = bytearray(block)
        # TODO CH, if several allocations above are minimised, can this be dropped?
        gc.collect()
        return block

    def writeBlock(self, realBlockIndex, data):
        if self.selectedTagUid is None: raise AssertionError("Not selected")
        # TODO CH is this repeated auth always necessary, or only once?
        if self.rdr.auth(MFRC522.AUTHENT1A, realBlockIndex, key, self.selectedTagUid) is not MFRC522.OK: raise AssertionError("Auth")
        return self.rdr.write(realBlockIndex, data)

    def readLengthsBlock(self):
        return self.readBlock(lengthsRealIndex)

    def writeLengthsBlock(self, data):
        return self.writeBlock(lengthsRealIndex, data)

    def getActiveBank(self, lengthsBlock=None):
        if lengthsBlock is None:
            lengthsBlock = self.readLengthsBlock()
        activeBank = 0
        while lengthsBlock[activeBank] is 0 and activeBank < numBanks:
            activeBank += 1
        if activeBank < numBanks:
            return activeBank
        else:
            return None

    def readJson(self, tagUid=None, unselect=True):
        try:
            tagUid = self.selectTag(tagUid)
            lengthsBlock = self.readLengthsBlock()
            # establish active bank from lengths block
            activeBank = self.getActiveBank(lengthsBlock)
            if activeBank is not None:
                bankLength = lengthsBlock[activeBank]   # how many bytes in the bank
                bankBytes = bytearray(bankLength)       # pre-allocate a buffer to store them
                safeIndex = activeBank * blocksPerBank  # what's the first authorable block in the bank
                nextBytePos = 0
                # read the next block from the bank, until bankBytes is filled
                while nextBytePos < bankLength:
                    nextRealIndex = getRealIndex(safeIndex)
                    copyLength = min(bytesPerBlock, bankLength - nextBytePos)
                    # TODO CH pass an 'into' array, avoiding allocation
                    blockData = self.readBlock(nextRealIndex)
                    # TODO avoid implicit allocation blockData[:copyLength] when blockData length (bytesPerBlock) is copyLength (most of the time)
                    bankBytes[nextBytePos:nextBytePos + copyLength] = blockData[:copyLength]
                    nextBytePos += copyLength
                    safeIndex += 1
                # testing: import json; o = dict(hello="world"); b = bytes(json.dumps(o).encode("ascii")); print(json.loads(b.decode('ascii')))
                # TODO CH is there a way to avoid allocation of bytes object here to wrap bytearray
                bankBytes = bytes(bankBytes)
                return json.loads(bankBytes.decode('ascii'))
            else:
                raise AssertionError("No bank")
        finally:
            if unselect:
                self.unselectTag()
            gc.collect()

    # example ms=ticks_ms(); sack = vault.readJson(unselect=False); sack["eponapoints"]+=1; sack=vault.writeJson(sack, tagUid=vault.selectedTagUid); print(ticks_ms() - ms)

    def writeJson(self, obj, tagUid=None, unselect=True):
        try:
            # TODO does this implicitly unselect in the case that writeJson is called 'agnostic' to tag
            tagUid = self.selectTag(tagUid)
            lengthsBlock = self.readLengthsBlock()
            activeBank = self.getActiveBank(lengthsBlock)
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
                self.blockBuffer[:copyLength] = bankBytes[nextBytePos:nextBytePos + copyLength]
                self.writeBlock(nextRealIndex, self.blockBuffer)
                nextBytePos += copyLength
                safeIndex += 1
            nextBytePos = bytesPerBlock
            while nextBytePos > 0:
                nextBytePos -= 1
                self.blockBuffer[nextBytePos] = 0
            self.blockBuffer[nextBank]=bankLength
            self.writeLengthsBlock(self.blockBuffer)

        finally:
            if unselect:
                self.unselectTag()
            gc.collect()