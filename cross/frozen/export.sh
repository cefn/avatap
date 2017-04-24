#!/bin/bash
set -e 

# Start in script current directory
cd "$(dirname "$(realpath "$0")")";

# prepare paths
GITDIR=$(realpath ../../../)
MODULEDIR="micropython/esp8266/modules"

# prepare commands
ECHO=""
COPYPATHCMD="$ECHO cp -v"
CREATEPATHCMD="$ECHO mkdir -p"
RMPATHCMD="$ECHO rm"
MAKECMD="$ECHO make"
ESPTOOLCMD="$ECHO esptool.py"

# switch to top level folder containing all git repositories
cd $GITDIR

# descend into avatap/python to cache templates, generate QString declarations then return
cd avatap/python
find templates -type f -name 't_*.py' -exec $RMPATHCMD {} \;
python3 -m templates > ../../micropython/esp8266/qstrdefsport.h
cd ../../

# AVATAP LIBRARIES
find avatap/python -maxdepth 1 -type f -name '*.py' -exec $COPYPATHCMD {} $MODULEDIR \;

# MUSEUM STORIES
$RMPATHCMD -rf $MODULEDIR/stories
$CREATEPATHCMD $MODULEDIR/stories
find avatap/python/stories -maxdepth 1 -type f -name '*.py' -exec $COPYPATHCMD -R {} $MODULEDIR/stories \;

# MUSEUM TEMPLATES
$RMPATHCMD -rf $MODULEDIR/templates
$CREATEPATHCMD $MODULEDIR/templates
find avatap/python/templates -maxdepth 1 -type f -name '*.py' -exec $COPYPATHCMD -R {} $MODULEDIR/templates \;

# MUSEUM STORIES
$RMPATHCMD -rf $MODULEDIR/regimes
$CREATEPATHCMD $MODULEDIR/regimes
find avatap/python/regimes -maxdepth 1 -type f -name '*.py' -exec $COPYPATHCMD -R {} $MODULEDIR/regimes \;

# SCREEN LIBRARY
$COPYPATHCMD micropython-st7920/st7920.py $MODULEDIR
# READER LIBRARY
$COPYPATHCMD micropython-mfrc522/mfrc522.py $MODULEDIR
$COPYPATHCMD micropython-mfrc522/examples/read.py $MODULEDIR
$COPYPATHCMD micropython-mfrc522/examples/write.py $MODULEDIR
# FONT LIBRARY
$COPYPATHCMD bitfont/python/bitfont.py $MODULEDIR
# FONT FACES
$RMPATHCMD -R $MODULEDIR/faces
$CREATEPATHCMD $MODULEDIR/faces
touch $MODULEDIR/faces/__init__.py
$COPYPATHCMD bitfont/python/faces/font_5x7.py $MODULEDIR/faces/
$COPYPATHCMD bitfont/python/faces/font_ArtosSerif_8.py $MODULEDIR/faces/

# TRIGGER FREEZING OF MODULES INTO FIRMWARE IMAGE AND UPLOAD IT
cd micropython/esp8266/
set -e
export PATH=/home/cefn/Documents/shrimping/git/esp-open-sdk/xtensa-lx106-elf/bin:$PATH
#$MAKECMD clean
#$MAKECMD axtls
$MAKECMD build/firmware-combined.bin
#$MAKECMD PORT=/dev/ttyUSB0 FLASH_MODE=dio FLASH_SIZE=32m deploy
#CH below invocation is faster
$ESPTOOLCMD --port /dev/ttyUSB0 --baud 1500000 write_flash --flash_mode dio --flash_size=32m 0 build/firmware-combined.bin

