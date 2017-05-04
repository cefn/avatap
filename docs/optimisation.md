# Optimisation

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

Modify bitfont library to allow inclusion of only a subset of characters - e.g. all caps of a high-res font (with friendly fallback behaviour for characters outside range)

Remove examples from reader library export

Remove unused modules from frozen modules list (e.g. webrepl ds18x20)