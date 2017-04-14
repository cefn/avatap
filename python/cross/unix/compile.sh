#!/bin/bash
COMPILER=../../../micropython/mpy-cross/mpy-cross -mcache-lookup-bc

find ../ -maxdepth 1 -name '*.py' -exec ${COMPILER} {} \;
find ../ -maxdepth 1 -name '*.mpy' -exec mv {} ./ \;

find ../stories/ -maxdepth 1 -name '*.py' -exec ${COMPILER} {} \;
find ../stories/ -maxdepth 1 -name '*.mpy' -exec mv {} ./ \;
