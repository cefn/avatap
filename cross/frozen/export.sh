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

# SCREEN LIBRARY
$COPYPATHCMD micropython-st7920/st7920.py $MODULEDIR

# READER LIBRARY
$COPYPATHCMD micropython-mfrc522-cefn/mfrc522.py $MODULEDIR
# CH TODO REMOVE READER EXAMPLES
$COPYPATHCMD micropython-mfrc522-cefn/examples/read.py $MODULEDIR
$COPYPATHCMD micropython-mfrc522-cefn/examples/write.py $MODULEDIR

# FONT LIBRARY
$COPYPATHCMD bitfont/python/bitfont.py $MODULEDIR
# FONT FACES
$RMPATHCMD -R $MODULEDIR/faces || true
$CREATEPATHCMD $MODULEDIR/faces
$COPYPATHCMD bitfont/python/faces/__init__.py $MODULEDIR/faces/
$COPYPATHCMD bitfont/python/faces/font_5x7.py $MODULEDIR/faces/
$COPYPATHCMD bitfont/python/faces/font_ArtosSerif_8.py $MODULEDIR/faces/

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

# ENGINES
$RMPATHCMD -R $MODULEDIR/engines || true
$CREATEPATHCMD $MODULEDIR/engines
$COPYPATHCMD avatap/python/engines/__init__.py $MODULEDIR/engines/
$COPYPATHCMD avatap/python/engines/console.py $MODULEDIR/engines/

# AVATAP LIBRARIES
find avatap/python -maxdepth 1 -type f -name '*.py' -exec $COPYPATHCMD {} $MODULEDIR \;

# AVATAP REGIMES (e.g. INTEGRATION TEST)
$RMPATHCMD -R $MODULEDIR/regimes || true
$CREATEPATHCMD $MODULEDIR/regimes
$COPYPATHCMD avatap/python/regimes/integration_test.py $MODULEDIR/regimes/

# TODO CH - for Avatap dev, reactivate VFS and use dynamically loaded versions
$COPYPATHCMD avatap/python/engines/avatap.py $MODULEDIR/engines/
$COPYPATHCMD avatap/python/regimes/avatap.py $MODULEDIR/regimes/

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

