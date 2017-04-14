Track2 - 128x64 pixel screen
X check that ST7920=based 128x64 screen can be driven by Arduino at 3.3V
	- yes - 3.3V logic works, but needs 5V VCC for screen
X Try to duplicate the Arduino-based wiring with a second screen, preparing it for SPI 
X try to port the Raspberry Pi SPI initialisation and pixel-drawing operations (seem to target the same screen) to ESP8266 micropython
- if this works, identify a lo-res font and export it to python-based pixel information, and check writing speed is adequate

Track3 - RFID Read/write cycle
- Prove that JSON can be written to an RFID card and read back. How long does it take?
- explore use of card presence as a control for screen viewing
- Explore use of IRQ to trigger prompt SPI read of RFID

Track4 - Cockle SPI Slave Select
- check that SPI write to ST7920 and SPI read/write to MFRC522 are compatible pseudo-simultaneously, or establish alternating regime

Track 5 - Cockle Memory Limits
- load the full corbridge emulator into the Micropython cockle
- if there are memory issues, then build your own Micropython with frozen modules following... https://learn.adafruit.com/micropython-basics-loading-modules/frozen-modules

Track 6 - Minification
- process through minify to...
	- switch spaces to tabs
	- remove docstrings and comments
	- possibly obfuscate
- process through ast (https://docs.python.org/2/library/ast.html#ast.NodeTransformer) to...
	- remove indentation characters from story text strings

# ABANDONED

Track1 40x4 character screen
- create an arduino-based version using the proven TM404 LCD 4-bit driver
- prove that it runs at 3.3V as well
- figure out the alternate circuit required to drive it by 3.3V logic
- work back from initialisation routine in Arduin TM404 reference, adding the same sequence to the Microbit HD44780 python code

