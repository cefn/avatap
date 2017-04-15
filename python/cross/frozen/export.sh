#!/bin/bash
find ../../ -maxdepth 1 -name '*.py' -exec cp {} ../../../../micropython/esp8266/modules/ \;
find ../../stories/ -maxdepth 1 -name '*.py' -exec cp {} ../../../../micropython/esp8266/modules/ \;
