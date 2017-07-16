# Optimisation

Experiment with overclocking for 2x speedup https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/powerctrl.html (make SPI or externally-timed functionality unstable?) 

Make debug validation logic depend on Milecastles debug flag, to accelerate story loading and minimise memory fragmentation (speed powerup for solar boxes)

TODO replace non-debug asserts with if and AssertionError? This will permit future optimisation by toggling a flag

Toggle optimisation on in boot.py to save RAM, using...
micropython.opt_level(1) 
...following https://github.com/micropython/micropython/pull/2484

The following could be attempted in the build process to minimise RAM utilisation.

Turn off VFAT in _boot.py
Turn off Networking/Wifi also in _boot.py - does this actually stop it?
Turn off debugging metadata in loaded bytecode (Don't know how)

Use string hash of template source to identify template to save/load, instead of storyUid, nodeUID, templateName tuple, eliminating duplicates, also minimising size of qstrdefsport.h file both of which contribute to overflowing the irom segment currently.

Change evaled expressions to be compiled functions as well.
Change integer indexes in bitfont to use array/ustruct/uctypes as per footer comment in https://docs.micropython.org/en/latest/esp8266/reference/constrained.html

Modify bitfont library to allow inclusion of only a subset of characters - e.g. all caps of a high-res font (with friendly fallback behaviour for characters outside range). Promote firstAsciiChar and endAsciiChar to be on a per-typeface basis.

Remove examples from reader library export

Remove unused modules from frozen modules list (e.g. webrepl ds18x20)

Remove rotation logic from st7920 library

Avoid full screen redraw (fix memory map logic)

Avoid nested function calls and checks from plotter which calls screen plot inside. Instead plotter factory should have embedded plot operation, with plotter= value replacing set= value in screen draw operations.

Somehow force templates to be constructed with bytes not unicode strings. Maybe make no difference, since unicode encodes ascii efficiently enough, and micropython frozen strings are effectively bytes anyway?

Follow instructions to build a diode gate, to permit hardware SPI to be used for both reader and screen (given screen's intolerance for SCK or SID transience when SS is unselected) 
See https://www.eevblog.com/forum/projects/how-to-properly-connect-lcd-128x64-via-spi/ and http://hyperphysics.phy-astr.gsu.edu/hbase/Electronic/diodgate.html
