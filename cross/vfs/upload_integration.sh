#!/bin/bash
set -e 

export AMPY="ampy --port /dev/ttyUSB0"
export AMPYPUT="$AMPY put" 
export AMPYRESET="$AMPY reset"

# Start in script current directory
cd "$(dirname "$(realpath "$0")")";

# change to git directory containing multiple repos
cd ../../../

# change into cockle directory to deploy generic image
#cd cockle
#python3 -m flash.deploy
#$AMPYRESET
#sleep 10
#cd ../


# add agnostic library
echo agnostic...
$AMPYPUT avatap/python/agnostic.py
$AMPYRESET

# add screen libraries
echo st7920...
$AMPYPUT micropython-st7920/canvas.py
$AMPYPUT micropython-st7920/st7920.py
$AMPYRESET

# add font libraries
echo bitfont...
$AMPYPUT bitfont/python/bitfont.py
$AMPY mkdir faces
$AMPYPUT bitfont/python/faces/font_5x7.py faces/font_5x7.py
#$AMPYPUT bitfont/python/faces/font_timB14.py faces/font_timB14.py
$AMPYRESET

# add reader libraries
echo mfrc522...
$AMPYPUT micropython-mfrc522/mfrc522.py
$AMPYRESET

# add integration test
echo integration_test...
$AMPYPUT avatap/python/regimes/integration_test.py test.py
$AMPYRESET
