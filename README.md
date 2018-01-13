# avatap

This provides an implementation of an interactive, RFID-driven text adventure, originally developed to be installed in museums along the Hadrian's wall. The boxes are RFID-readers with low resolution screens driven by ESP8266 modules running Micropython. They serve a single page of the adventure at a time when you place your tag. To choose adventures, you decide which location in the game area to visit and tag next. Boxes power up from boot in about 4 seconds, allowing them to be maintained in a low-power configuration, to be installed in distributed and rural locations.
