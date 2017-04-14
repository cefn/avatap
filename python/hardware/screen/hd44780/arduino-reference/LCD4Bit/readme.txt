This is a C++ library for Arduino for controlling an HD74800-compatible LCD in 4-bit mode.
Tested on Arduino 0005 Alpha.

Installation
--------------------------------------------------------------------------------

To install this library, just place this entire folder as a subfolder in your
Arduino/lib/targets/libraries folder.

When installed, this library should look like:

Arduino/lib/targets/libraries/LCD4Bit              (this library's folder)
Arduino/lib/targets/libraries/LCD4Bit/LCD4Bit.cpp  (the library implementation file)
Arduino/lib/targets/libraries/LCD4Bit/LCD4Bit.h    (the library description file)
Arduino/lib/targets/libraries/LCD4Bit/keywords.txt (the syntax coloring file)
Arduino/lib/targets/libraries/LCD4Bit/examples     (the examples in the "open" menu)
Arduino/lib/targets/libraries/LCD4Bit/readme.txt   (this file)

Building
--------------------------------------------------------------------------------

After this library is installed, you just have to start the Arduino application.
You may see a few warning messages as it's built.

To use this library in a sketch, go to the Sketch | Import Library menu and
select LCD4Bit.  This will add a corresponding line to the top of your sketch:
#include <LCD4Bit.h>

To stop using this library, delete that line from your sketch.

Geeky information:
After a successful build of this library, a new file named "LCD4Bit.o" will appear
in "Arduino/lib/targets/libraries/LCD4Bit". This file is the built/compiled library
code.

If you choose to modify the code for this library (i.e. "LCD4Bit.cpp" or "LCD4Bit.h"),
then you must first 'unbuild' this library by deleting the "LCD4Bit.o" file. The
new "LCD4Bit.o" with your code will appear after the next press of "verify"
