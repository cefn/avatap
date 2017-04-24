#!/bin/bash
cd "$(dirname "$(realpath "$0")")";
GITPATH=$(realpath ../../../../)
MODULEPATH=micropython/esp8266/modules/
cd $GITPATH
# AVATAP LIBRARIES
find avatap/python -maxdepth 1 -type f -name '*.py' -exec cp -v {} $MODULEPATH \;
# MUSEUM STORIES
mkdir -p $MODULEPATH/stories
touch $MODULEPATH/stories/__init__.py
find avatap/python/stories -maxdepth 1 -type f -name '*.py' -exec cp -v -R {} $MODULEPATH/stories \;
# SCREEN LIBRARY
cp -v micropython-st7920/st7920.py $MODULEPATH
# READER LIBRARY
cp -v micropython-mfrc522/mfrc522.py $MODULEPATH
cp -v micropython-mfrc522/examples/read.py $MODULEPATH
cp -v micropython-mfrc522/examples/write.py $MODULEPATH
# FONT LIBRARY
cp -v bitfont/python/bitfont.py $MODULEPATH
# FONT FACES
mkdir -p $MODULEPATH/faces
touch $MODULEPATH/faces/__init__.py
cp -v bitfont/python/faces/font_5x7.py $MODULEPATH/faces/
cp -v bitfont/python/faces/font_ArtosSerif_8.py $MODULEPATH/faces/

# LOAD TESTER
cp -v avatap/python/cross/frozen/load.py $MODULEPATH

# TRIGGER FREEZING OF MODULES INTO FIRMWARE IMAGE AND UPLOAD IT
cd micropython/esp8266/
set -e
export PATH=/home/cefn/Documents/shrimping/git/esp-open-sdk/xtensa-lx106-elf/bin:$PATH
#make clean
#make axtls
make build/firmware-combined.bin
#make PORT=/dev/ttyUSB0 FLASH_MODE=dio FLASH_SIZE=32m deploy
#CH below invocation is faster
esptool.py --port /dev/ttyUSB0 --baud 1500000 write_flash --flash_mode dio --flash_size=32m 0 build/firmware-combined.bin

